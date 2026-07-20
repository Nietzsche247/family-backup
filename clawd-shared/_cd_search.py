import os, re, email
from email import policy

ROOT = r'C:\North_Star_Projects\Litigation-Wilson\preserved\mail'
folders = ['aaron','allysa.redmon','build','christine.stewart','construction','martin','michael','scott.culver','veronica.leyva']
kw = [b'cease', b'desist', b'stop work', b'stop all work', b'stop-work']
rx_cd = re.compile(r'cease|desist', re.I)
rx_sw = re.compile(r'stop\s*-?\s*work', re.I)
cd, sw = [], []
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
                fnm = part.get_filename()
                if fnm: atts.append(fnm)
                if part.get_content_type() in ('text/plain','text/html'):
                    try: b += (part.get_content() or '')[:80000]
                    except: pass
        except: pass
        hay = subj + '\n' + b + '\n' + ' '.join(atts)
        line = '%s/%s | %s | FROM %s | TO %s | SUBJ %s' % (fld, fn, date, frm[:38], to[:50], subj[:55])
        if any(rx_cd.search(a) for a in atts): line += ' | ATT-MATCH: ' + '; '.join(a for a in atts if rx_cd.search(a))
        if rx_cd.search(hay): cd.append(line)
        elif rx_sw.search(hay): sw.append(line)
o = ['===== CEASE / DESIST (%d) =====' % len(cd)] + (cd or ['(none)']) + ['', '===== STOP-WORK only (%d) =====' % len(sw)] + (sw or ['(none)'])
open(r'C:\Users\aaron\clawd-shared\_cd_search.txt','w',encoding='utf-8').write('\n'.join(o))
print('cease/desist=%d stop-work=%d' % (len(cd), len(sw)))
