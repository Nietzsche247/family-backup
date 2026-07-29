import sys, email, email.policy
sys.path.insert(0, r"C:\Users\aaron\clawd-shared")
from wilson_counsel_pdf import KEY, EMLS

for src, name in EMLS:
    p = KEY / name
    with open(p, "rb") as fh:
        msg = email.message_from_binary_file(fh, policy=email.policy.default)
    rows = []
    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue
        fn = part.get_filename()
        disp = (part.get("Content-Disposition") or "").lower()
        cid = part.get("Content-ID") or ""
        if "attachment" not in disp and not fn:
            continue
        raw = part.get_payload(decode=True) or b""
        rows.append((fn or "[unnamed]", part.get_content_type(),
                     len(raw), "inline" if "inline" in disp else "attach", cid))
    if rows:
        print(f"\n{src}  {name}")
        for fn, ct, n, kind, cid in rows:
            safe = fn.encode("ascii", "replace").decode()
            print(f"    [{kind:6}] {safe:52} {ct:34} {n:>10,}  {cid}")
