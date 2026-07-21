import os, email, re
from email import policy
from email.utils import parsedate_to_datetime

ROOT = r'C:\North_Star_Projects\Litigation-Wilson\preserved\mail'
folders = ['aaron','allysa.redmon','build','christine.stewart','construction','martin','michael','scott.culver','veronica.leyva']
def get_text(m):
    t=''
    for p in m.walk():
        if p.get_content_type()=='text/plain':
            try: t+=(p.get_content() or '')
            except: pass
    if t.strip(): return t
    h=''
    for p in m.walk():
        if p.get_content_type()=='text/html':
            try: h+=(p.get_content() or '')
            except: pass
    h=re.sub(r'(?is)<(script|style).*?</\1>',' ',h)
    h=re.sub(r'<[^>]+>',' ',h); h=h.replace('&nbsp;',' ').replace('&amp;','&').replace('&#39;',"'").replace('&quot;','"')
    return h
def top(b):
    for sep in ['\nOn ','\n> ','-----Original','________','Sent from my']: b=b.split(sep)[0]
    return ' '.join(b.split())
W=[]; seen=set()
for fld in folders:
    d=os.path.join(ROOT,fld)
    for fn in os.listdir(d):
        if not fn.endswith('.eml'): continue
        p=os.path.join(d,fn)
        try:
            with open(p,'rb') as f: head=f.read(8000)
        except: continue
        if b'davidwilson0' not in head: continue
        try: hm=email.message_from_bytes(head,policy=policy.default)
        except: continue
        if 'davidwilson0' not in str(hm.get('from','') or '').lower(): continue
        try: m=email.message_from_bytes(open(p,'rb').read(),policy=policy.default)
        except: m=hm
        mid=str(m.get('message-id','') or fn)
        if mid in seen: continue
        seen.add(mid)
        subj=str(m.get('subject','') or ''); to=str(m.get('to','') or '')
        dt=parsedate_to_datetime(m.get('date')) if m.get('date') else None
        ds=dt.strftime('%Y-%m-%d %H:%M') if dt else '????'
        tl=top(get_text(m))
        W.append((ds,'%s | %s | to %s\n  SUBJ %s\n  >> %s'%(ds,fld+'/'+fn,to[:45],subj[:70],tl[:1800] or '(truly empty)')))
W.sort(reverse=True)
open(r'C:\Users\aaron\clawd-shared\_recount3.txt','w',encoding='utf-8').write('=== WILSON-AUTHORED w/ HTML bodies (newest first) ===\n\n'+'\n\n'.join(x[1] for x in W))
print('wilson-authored:',len(W))
