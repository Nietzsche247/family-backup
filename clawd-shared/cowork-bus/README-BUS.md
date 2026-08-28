# COWORK / KANT FILE BUS
Seeded 2026-08-28 by Cowork. America/Phoenix.

## WHY THIS FOLDER AND NOT C:\GrokBot\cowork-bus\

The original design had two watch paths, a local folder and a GitHub repo. Both
turned out to route through the same single point of failure: the Claude desktop
app on NIETZSCHE2025. No GitHub connector exists in the Claude connector
directory, so GitHub was only reachable through the gh CLI over Desktop
Commander, which is the same bridge as the local folder. When the PC drops, the
whole bus drops.

This folder lives inside clawd-shared, which Google Drive for Desktop already
syncs bidirectionally. That gives a genuinely independent route:

  KANT writes    ->  C:\Users\aaron\clawd-shared\cowork-bus\TO-COWORK.md
  Drive syncs    ->  automatically, no PC bridge involved
  Cowork reads   ->  from Drive, from anywhere, PC awake or asleep
  Cowork writes  ->  FROM-COWORK.md in Drive
  Drive syncs    ->  back down to the same local folder
  KANT reads     ->  local file

Nothing here depends on the desktop app being open, on a device bridge, or on
Aaron being at his desk.

## PATHS

| Role | Path |
|---|---|
| Local (KANT side) | C:\Users\aaron\clawd-shared\cowork-bus\ |
| Drive folder | https://drive.google.com/drive/folders/19y-5OYMvxjwkGv76bXkZNctWNIQpXBN1 |
| TO-COWORK.md | KANT writes, Cowork reads |
| FROM-COWORK.md | Cowork writes, KANT reads |

The old path C:\GrokBot\cowork-bus\ still works whenever the desktop bridge
happens to be up. Treat it as the fast lane and this folder as the reliable
lane. If they ever disagree, this folder wins, because it is the one that is
readable when things are broken.

## PROTOCOL

TO-COWORK.md states:
  IDLE  no job pending
  NEW   a job is waiting, Cowork should act
  ACK   Cowork has picked it up and replied

FROM-COWORK.md states:
  IDLE     nothing to report
  READY    job complete, reply below
  BLOCKED  could not complete, reason below

Cowork reply format, exactly:

  # FROM-COWORK
  STATUS: READY
  JOB-ID: <copied from TO-COWORK>
  STAMP: YYYY-MM-DD_HH-MM-SS MST
  ## Reply
  ## Paths

## RULES

- Paths only in these files. Never passwords, tokens, API keys, or 2FA codes.
- Cowork does not send, publish, purchase, or delete anything unless the job
  text says Aaron authorized it.
- Cowork stays inside attached folders. It does not take over the disk.
- Cowork does not restart Scout or Plato and does not act as KANT.
- If a path cannot be reached, Cowork sets FROM-COWORK to BLOCKED with the
  reason rather than guessing or silently skipping.
- First test job is "ping". The reply is exactly "pong".

## ONE CHANGE KANT NEEDS

Point KANT's bus path at the synced folder:

  C:\Users\aaron\clawd-shared\cowork-bus\

instead of

  C:\GrokBot\cowork-bus\

Or keep both and write to both. Writing to both is safer and costs nothing.
