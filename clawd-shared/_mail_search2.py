import os, re, email
from email import policy

ROOT = r'C:\North_Star_Projects\Litigation-Wilson\preserved\mail'
folders = ['aaron','allysa.redmon','build','christine.stewart','construction','martin','michael','scott.culver','veronica.leyva']

# (A) read Veronica's Immediate Notice body
vp = os.path.join(ROOT, 'veronica.leyva', '196dace84730dec9.eml')
msg = email.message_from_bytes(open(vp,'rb').read(), policy=policy.default)
body = ''
for part in msg.walk():
    if part.get_content_type() == 'text/plain':
        try: body = part.get_content(); break
        except: pass
if not body:
    for part in msg.walk():
        if part.get_content_type() == 'text/html':
            try:
                import re as _r
                body = _r.sub('<[^>]+>', '', part.get_content()); break
            except: pass
print('===== VERONICA IMMEDIATE NOTICE (2025-05-16) BODY =====')
print('BCC field (to):', msg.get('to'))
print('---')
print((body or '(no text body)')[:2200])
print('===== END BODY =====\n')

# (B) cease/desist/stop-work hunt incl attachment filenames
kw = [b'cease', b'desist', b'stop work', b'stop all work', b'stop-work']
rx = re.compile(r'cease|desist|stop\s*-?\s*work', re.I)
out = []
for fld in folders:
    d = os.path.join(ROOT, fld)
    for fn in os.listdir(d):
        if not fn.endswith('.eml'): continue
        p = os.path.join(d, fn)
        try:
            with open(p,'rb') as f: head = f.read(1500000)
        except: continue
        if not any(k in head.lower() for k in kw): continue
        try: m = email.message_from_bytes(open(p,'rb').read(), policy=policy.default)
        except: continue
        subj = str(m.get('subject','') or ''); frm = str(m.get('from','') or ''); to = str(m.get('to','') or ''); date = str(m.get('date','') or '')
        b = ''; atts = []
        try:
            for part in m.walk():
                ct = part.get_content_type()
                fnm = part.get_filename()
                if fnm: atts.append(fnm)
                if ct in ('text/plain','text/html'):
                    try: b += (part.get_content() or '')[:80000]
                    except: pass
        except: pass
        in_body = bool(rx.search(subj + '\n' + b))
        in_att = any(rx.search(a) for a in atts)
        if in_body or in_att:
            where = ('BODY' if in_body else '') + (' ATTACHMENT' if in_att else '')
            attstr = (' | ATT: ' + '; '.join(a[:40] for a in atts if rx.search(a))) if in_att else ''
            out.append('[%s] %s/%s | %s | FROM %s | TO %s | SUBJ %s%s' % (where.strip(), fld, fn, date, frm[:40], to[:55], subj[:60], attstr))

print('===== CEASE/DESIST/STOP-WORK HITS: %d =====' % len(out))
print('\n'.join(out) if out else '(none found in bodies, subjects, or attachment filenames)')
