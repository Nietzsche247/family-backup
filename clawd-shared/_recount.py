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
    for sep in ['\nOn ','\n> ','\n-----Original','\n________','\nFrom: ']: b=b.split(sep)[0]
    return ' '.join(b.split())
A=[]; B=[]; seen=set()
mk=['terminat','no longer','delaney',' tom','letter','cease']
bk=['corner','warn','sat down','tried to','stay away','trust','meeting','tom','tommy','help me','stress']
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
        isA='michael' in frm and 'davidwilson0' in (to+cc)
        isB='davidwilson0' in frm
        if not (isA or isB): continue
        try: m=email.message_from_bytes(open(p,'rb').read(),policy=policy.default)
        except: m=hm
        mid=str(m.get('message-id','') or fn)
        if mid in seen: continue
        seen.add(mid)
        subj=str(m.get('subject','') or ''); dt=parsedate_to_datetime(m.get('date')) if m.get('date') else None
        ds=dt.strftime('%Y-%m-%d %H:%M') if dt else '????'
        bod=body(m); tl=top(bod); low=(subj+' '+bod).lower()
        if isA and any(k in low for k in mk):
            A.append((ds,'A | %s | %s\n  TO %s CC %s\n  SUBJ %s\n  ATTACH: %s\n  >> %s'%(ds,fld+'/'+fn,to[:65],cc[:40],subj[:80],atts(m),tl[:900])))
        if isB and any(k in low for k in bk):
            B.append((ds,'B | %s | %s\n  TO %s\n  SUBJ %s\n  >> %s'%(ds,fld+'/'+fn,to[:75],subj[:80],tl[:1500])))
A.sort(); B.sort()
o='=== A: MICHAEL -> WILSON (termination/Tom) ===\n\n'+'\n\n'.join(x[1] for x in A)
o+='\n\n\n=== B: WILSON-AUTHORED (meeting/warning recount) ===\n\n'+'\n\n'.join(x[1] for x in B)
open(r'C:\Users\aaron\clawd-shared\_recount.txt','w',encoding='utf-8').write(o)
print('A michael->wilson:',len(A),'| B wilson-authored:',len(B))
