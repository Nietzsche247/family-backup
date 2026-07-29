import sys, email, email.policy
from pathlib import Path
sys.path.insert(0, r"C:\Users\aaron\clawd-shared")
from wilson_counsel_pdf import KEY, EMLS, pick_body, atts_of, OUT

print(f"{'SRC':9} {'body chars':>10} {'atts':>5}  {'pages':>5}  body source")
print("-" * 78)
for src, name in EMLS:
    p = KEY / name
    with open(p, "rb") as fh:
        msg = email.message_from_binary_file(fh, policy=email.policy.default)
    body, note = pick_body(msg)
    a = atts_of(msg)
    pdf = OUT / "emails_as_pdf" / f"{p.stem}.pdf"
    raw = pdf.read_bytes()
    pages = raw.count(b"/Type /Page\n") + raw.count(b"/Type /Page ")
    if pages == 0:
        pages = raw.count(b"/Type/Page")
    src_note = "plain" if "text/plain" in note else (
        "html-stripped" if "html" in note else "NONE")
    print(f"{src:9} {len(body):>10,} {len(a):>5}  {pages:>5}  {src_note}")
    if len(body) < 40:
        print(f"          !! THIN BODY: {body[:200]!r}")

print()
print("first 400 chars of each body")
print("=" * 78)
for src, name in EMLS:
    p = KEY / name
    with open(p, "rb") as fh:
        msg = email.message_from_binary_file(fh, policy=email.policy.default)
    body, _ = pick_body(msg)
    print(f"\n--- {src}  subject: {msg.get('Subject','')!r}")
    print(body[:400].replace("\r", ""))
