import os, email, re
from email import policy
from email.utils import parsedate_to_datetime
from datetime import datetime

ROOT = r'C:\North_Star_Projects\Litigation-Wilson\preserved\mail'
folders = ['aaron','allysa.redmon','build','christine.stewart','construction','martin','michael','scott.culver','veronica.leyva']
def get_text(m):
    t=''
    for p in m.walk():
        if p.get_content_type()=='text/plain':
            try: t+=(p.get_content() or '')
            except: pass
    h=''
    for p in m.walk():
        if p.get_content_type()=='text/html':
            try: h+=(p.get_content() or '')
            except: pass
    h=re.sub(r'(?is)<(script|style).*?</\1>',' ',h); h=re.sub(r'<[^>]+>',' ',h)
    h=h.replace('&nbsp;',' ').replace('&amp;','&').replace('&#39;',"'").replace('&gt;','>').replace('&lt;','<').replace('&quot;','"')
    return t+' \n[HTML]\n '+h
hits=[]
for fld in folders:
    d=os.path.join(ROOT,fld)
    for fn in os.listdir(d):
        if not fn.endswith('.eml'): continue
        p=os.path.join(d,fn)
        try:
            with open(p,'rb') as f: head=f.read(8000)
        except: continue
        if b'2026' not in head: continue
        try:
            hm=email.message_from_bytes(head,policy=policy.default)
            dt=parsedate_to_datetime(hm.get('date'))
        except: continue
        if dt is None: continue
        try:
            if dt.date() < datetime(2026,7,12).date(): continue
        except: continue
        try: m=email.message_from_bytes(open(p,'rb').read(),policy=policy.default)
        except: m=hm
        txt=get_text(m)
        if 'corner' not in txt.lower(): continue
        subj=str(m.get('subject','') or ''); frm=str(m.get('from','') or ''); to=str(m.get('to','') or '')
        ds=dt.strftime('%a %Y-%m-%d %H:%M %z')
        hits.append('%s | %s\n FROM %s\n TO %s\n SUBJ %s\n >>> %s'%(ds,fld+'/'+fn,frm[:60],to[:60],subj[:80],' '.join(txt.split())[:2600]))
open(r'C:\Users\aaron\clawd-shared\_cornered.txt','w',encoding='utf-8').write('\n\n====\n\n'.join(hits))
print('recent emails (>=2026-07-12) containing "corner":', len(hits))
