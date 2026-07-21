import os, email
from email import policy
from email.utils import parsedate_to_datetime
from datetime import datetime

ROOT = r'C:\North_Star_Projects\Litigation-Wilson\preserved\mail'
folders = ['aaron','allysa.redmon','build','christine.stewart','construction','martin','michael','scott.culver','veronica.leyva']
lo = datetime(2026,7,15).date(); hi = datetime(2026,7,20).date()
rx_wil = ('wilson','davidwilson0')
wk = ['warranty','complaint','punch','open item','leak','crack','defect','plaster','pebble','interior','finish','surface','stain','delam','tile','deck','repair','callback','call back','list of open']
seen=set(); hits=[]
for fld in folders:
    d=os.path.join(ROOT,fld)
    for fn in os.listdir(d):
        if not fn.endswith('.eml'): continue
        p=os.path.join(d,fn)
        try:
            with open(p,'rb') as f: head=f.read(6000)
        except: continue
        if b'2026' not in head: continue
        try:
            hm=email.message_from_bytes(head,policy=policy.default)
            dt=parsedate_to_datetime(hm.get('date'))
        except: continue
        if dt is None: continue
        try: ld=dt.date()
        except: continue
        if not (lo<=ld<=hi): continue
        try: m=email.message_from_bytes(open(p,'rb').read(),policy=policy.default)
        except: m=hm
        mid=str(m.get('message-id','') or fn)
        if mid in seen: continue
        seen.add(mid)
        subj=str(m.get('subject','') or ''); frm=str(m.get('from','') or ''); to=str(m.get('to','') or ''); cc=str(m.get('cc','') or '')
        b=''
        try:
            for part in m.walk():
                if part.get_content_type()=='text/plain':
                    try: b+=(part.get_content() or '')[:20000]
                    except: pass
        except: pass
        hdr=(frm+' '+to+' '+cc).lower()
        wil = any(w in hdr or w in (subj.lower()) for w in rx_wil)
        khit=[w for w in wk if w in (subj+' '+b).lower()]
        # keep: anything Wilson-involved, or warranty-keyword, or michael<->client
        if not (wil or khit): continue
        # trim quoted tail
        top = b.split('\nOn ')[0].split('\n> ')[0].strip()
        hits.append((dt, '%s | %s\n  FROM %s\n  TO %s  CC %s\n  SUBJ %s\n  WILSON:%s  kw:%s\n  >> %s' % (
            dt.strftime('%a %Y-%m-%d %H:%M %z'), fld+'/'+fn, frm[:60], to[:70], cc[:45], subj[:75],
            'YES' if wil else 'no', ','.join(khit) or '-', ' '.join(top[:600].split()))))
hits.sort(key=lambda x:x[0])
out='\n\n'.join(h[1] for h in hits)
open(r'C:\Users\aaron\clawd-shared\_thu_sun.txt','w',encoding='utf-8').write(out)
print('emails in window 2026-07-15..20 (Wilson/warranty):', len(hits))
