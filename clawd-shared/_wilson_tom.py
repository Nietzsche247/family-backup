import os, re, email
from email import policy

ROOT = r'C:\North_Star_Projects\Litigation-Wilson\preserved\mail'
folders = ['aaron','allysa.redmon','build','christine.stewart','construction','martin','michael','scott.culver','veronica.leyva']
pf = [b'davidwilson0', b'tommy', b'garage', b'overlay', b'auction']
rx_from = re.compile(r'davidwilson0@yahoo', re.I)
rx_tommy = re.compile(r'\btommy\b', re.I)
rx_gar = re.compile(r'garage', re.I)
rx_ovl = re.compile(r'overlay', re.I)
rx_auc = re.compile(r'auction', re.I)
rx_priv = re.compile(r'thomae|kimminau|defenselawtucson|jake@|@e\.read', re.I)
seen = set(); out = []

def snip(text, rx, w=170):
    m = rx.search(text)
    if not m: return ''
    s = max(0, m.start()-w); e = min(len(text), m.end()+w)
    return ' '.join(text[s:e].split())

for fld in folders:
    d = os.path.join(ROOT, fld)
    for fn in os.listdir(d):
        if not fn.endswith('.eml'): continue
        p = os.path.join(d, fn)
        try:
            with open(p,'rb') as f: head = f.read(800000)
        except: continue
        if not any(k in head.lower() for k in pf): continue
        try: m = email.message_from_bytes(open(p,'rb').read(), policy=policy.default)
        except: continue
        mid = str(m.get('message-id','') or fn)
        if mid in seen: continue
        seen.add(mid)
        subj=str(m.get('subject','') or ''); frm=str(m.get('from','') or ''); to=str(m.get('to','') or ''); cc=str(m.get('cc','') or ''); date=str(m.get('date','') or '')
        b=''
        try:
            for part in m.walk():
                if part.get_content_type()=='text/plain':
                    try: b+= (part.get_content() or '')[:100000]
                    except: pass
        except: pass
        hay = subj+'\n'+b
        wilson_author = bool(rx_from.search(frm))
        hits = []
        if wilson_author: hits.append('WILSON-AUTHORED')
        if rx_tommy.search(hay): hits.append('tommy')
        if rx_gar.search(hay): hits.append('garage')
        if rx_ovl.search(hay): hits.append('overlay')
        if rx_auc.search(hay): hits.append('auction')
        if not hits: continue
        priv = bool(rx_priv.search(frm+' '+to+' '+cc))
        rx1 = rx_tommy if 'tommy' in hits else (rx_gar if 'garage' in hits else (rx_ovl if 'overlay' in hits else (rx_auc if 'auction' in hits else rx_from)))
        sn = '' if priv else snip(b or subj, rx1)
        out.append('[%s]%s %s/%s | %s\n   FROM %s | TO %s\n   SUBJ %s\n   >> %s' % (
            ','.join(hits), ' [PRIV-FLAG]' if priv else '', fld, fn, date, frm[:55], (to+' cc:'+cc)[:80], subj[:75], sn[:340]))

open(r'C:\Users\aaron\clawd-shared\_wilson_tom.txt','w',encoding='utf-8').write('\n\n'.join(out))
print('distinct hits:', len(out))
