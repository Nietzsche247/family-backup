"""SkillOpt-Sleep — OpenClaw Fleet backend (Phase 1 POC).

A real model backend for the sleep cycle, driving the **Anthropic Messages
API** directly (urllib — no SDK dependency, works in the isolated POC env).
It subclasses ``CliBackend`` so it inherits the proven attempt/judge/reflect
prompts, JSON parsing, response cache and token accounting; only ``_call`` is
overridden to hit the API.

Model routing follows the OpenClaw fleet convention "provider/model", e.g.
  anthropic/claude-sonnet-4-6   -> attempt (target)
  anthropic/claude-opus-4-8     -> reflect/judge (optimizer)

Local rule/exact judges (gbrain-style) are scored WITHOUT any API call (see
CliBackend.judge), so the ledger-emit rule rubrics cost zero tokens to grade.
"""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from typing import Optional

from skillopt_sleep.backend import CliBackend, Backend


ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"

# Map fleet model ids -> concrete Anthropic API model names.
# On this fleet's Anthropic gateway the API model ids ARE the short labels
# (verified via /v1/models): claude-sonnet-4-6, claude-opus-4-8, etc. So the
# resolver simply strips the "anthropic/" provider prefix and passes through.
# Friendly aliases are mapped for convenience. Override via SKILLOPT_FLEET_MODEL_MAP.
_DEFAULT_MODEL_MAP = {
    "sonnet": "claude-sonnet-4-6",
    "opus": "claude-opus-4-8",
}


def _resolve_model(model: str) -> str:
    m = (model or "").strip()
    override = os.environ.get("SKILLOPT_FLEET_MODEL_MAP")
    if override:
        try:
            _DEFAULT_MODEL_MAP.update(json.loads(override))
        except Exception:
            pass
    # strip provider prefix ("anthropic/claude-sonnet-4-6" -> "claude-sonnet-4-6")
    if "/" in m:
        m = m.split("/", 1)[1]
    if m in _DEFAULT_MODEL_MAP:
        return _DEFAULT_MODEL_MAP[m]
    if m.startswith("claude-"):
        return m  # already a concrete fleet model id
    return _DEFAULT_MODEL_MAP.get("sonnet")


class OpenClawFleetBackend(CliBackend):
    """Anthropic-backed backend implementing the SkillOpt Backend protocol.

    attempt(task, skill, memory) -> str         (inherited prompt, our _call)
    judge(task, response)        -> (hard, soft, rationale)  (local rules; API for rubric)
    reflect(...)                 -> [EditRecord] (inherited prompt, our _call)
    tokens_used()                -> int          (accumulated prompt+completion tokens)
    """

    name = "openclaw-fleet"

    def __init__(
        self,
        model: str = "anthropic/claude-sonnet-4-6",
        api_key: str = "",
        timeout: int = 120,
        max_tokens: int = 1024,
    ) -> None:
        super().__init__(model=_resolve_model(model), timeout=timeout)
        self.fleet_model = model
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.default_max_tokens = max_tokens
        self.name = f"openclaw-fleet:{model}"
        self._call_count = 0
        self._error_count = 0

    def _call(self, prompt: str, *, max_tokens: int = 1024) -> str:
        if not self.api_key:
            return ""
        body = json.dumps({
            "model": self.model,
            "max_tokens": max(256, int(max_tokens or self.default_max_tokens)),
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")
        req = urllib.request.Request(
            ANTHROPIC_URL, data=body, method="POST",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": ANTHROPIC_VERSION,
                "content-type": "application/json",
            },
        )
        import time as _t
        last = ""
        for attempt in range(4):
            try:
                self._call_count += 1
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                # accumulate real token usage when present
                try:
                    u = data.get("usage", {})
                    self._tokens += int(u.get("input_tokens", 0)) + int(u.get("output_tokens", 0))
                except Exception:
                    pass
                parts = data.get("content", []) or []
                text = "".join(
                    b.get("text", "") for b in parts if isinstance(b, dict) and b.get("type") == "text"
                ).strip()
                if text:
                    return text
                last = "empty-response"
            except urllib.error.HTTPError as e:
                self._error_count += 1
                try:
                    last = e.read().decode("utf-8")[:200]
                except Exception:
                    last = str(e)
                # retry on 429 / 5xx; bail on 4xx auth errors
                if e.code not in (429, 500, 502, 503, 529):
                    return ""
            except Exception as e:  # noqa: BLE001
                self._error_count += 1
                last = str(e)
            if attempt < 3:
                _t.sleep((2 ** attempt) * 0.6)
        return ""

    # _cached_call inherited from CliBackend handles attempt/judge caching.

    def stats(self) -> dict:
        return {
            "fleet_model": self.fleet_model,
            "api_model": self.model,
            "api_calls": self._call_count,
            "api_errors": self._error_count,
            "tokens": self._tokens,
        }


def build_fleet_backend(
    *,
    target_model: str = "anthropic/claude-sonnet-4-6",
    optimizer_model: str = "anthropic/claude-opus-4-8",
    api_key: str = "",
    preferences: str = "",
) -> Backend:
    """Build a DualBackend: attempt on target model, reflect/judge on optimizer.

    Mirrors SkillOpt's target-vs-optimizer split (run the skill on a cheaper
    model, write edits with the stronger one). For ledger-emit, judging is rule
    based (local), so the optimizer model is used only for reflect().
    """
    from skillopt_sleep.backend import DualBackend

    target = OpenClawFleetBackend(model=target_model, api_key=api_key)
    if optimizer_model and optimizer_model != target_model:
        optimizer = OpenClawFleetBackend(model=optimizer_model, api_key=api_key)
        optimizer.preferences = preferences
        dual = DualBackend(target=target, optimizer=optimizer)
        dual.preferences = preferences
        return dual
    target.preferences = preferences
    return target
