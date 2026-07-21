import os, email
from email import policy
from email.utils import parsedate_to_datetime

ROOT = r'C:\North_Star_Projects\Litigation-Wilson\preserved\mail'
folders = ['aaron','allysa.redmon','build','christine.stewart','construction','martin','michael','scott.culver','veronica.leyva']
def body(m):
    b=''
    try:
        for p in m.walk():
            if p.get_content_type()=='text/plain':
                try: b+=(p.get_content() or '')
                except: pass
    except: pass
    return b
def atts(m):
    o=[]
    try:
        for p in m.walk():
            fn=p.get_filename()
            if fn: o.append(fn)
    except: pass
    return o
def top(b):
    for sep in ['\nOn ','\n> ','\n-----Original','\n________','\nFrom: ','\nSent from']: b=b.split(sep)[0]
    return ' '.join(b.split())
W=[]; T=[]; seen=set()
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
        frm=str(hm.get('from','') or '').lower(); to=str(hm.get('to','') or '').lower(); cc=str(hm.get('cc','') or '').lower()
        subj=str(hm.get('subject','') or '')
        isW='davidwilson0' in frm
        isT=('davidwilson0' in (to+cc)) and ('tom' in subj.lower())
        if not (isW or isT): continue
        try: m=email.message_from_bytes(open(p,'rb').read(),policy=policy.default)
        except: m=hm
        mid=str(m.get('message-id','') or fn)
        if mid in seen: continue
        seen.add(mid)
        dt=parsedate_to_datetime(m.get('date')) if m.get('date') else None
        ds=dt.strftime('%Y-%m-%d %H:%M') if dt else '????'
        bod=body(m); tl=top(bod)
        if isW:
            W.append((ds,'W | %s | %s\n  TO %s | SUBJ %s\n  >> %s'%(ds,fld+'/'+fn,to[:60],subj[:70],tl[:1600] or '(empty)')))
        if isT:
            T.append((ds,'T | %s | %s | from %s\n  SUBJ %s | ATTACH %s\n  >> %s'%(ds,fld+'/'+fn,frm[:45],subj[:60],atts(m),tl[:700])))
W.sort(reverse=True); T.sort()
o='=== W: ALL WILSON-AUTHORED (newest first) ===\n\n'+'\n\n'.join(x[1] for x in W)
o+='\n\n\n=== T: TOM-SUBJECT EMAILS TO WILSON (attachments) ===\n\n'+'\n\n'.join(x[1] for x in T)
open(r'C:\Users\aaron\clawd-shared\_recount2.txt','w',encoding='utf-8').write(o)
print('W wilson-authored:',len(W),'| T tom-to-wilson:',len(T))
