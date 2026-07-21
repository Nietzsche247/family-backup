import os, re, quopri, hashlib
WORK=r'C:\Users\aaron\clawd-shared\_vault_work'; KEY=r'C:\North_Star_Projects\WILSON_MATTER_WORKING_v1\preserved\keydocs'
raw=open(os.path.join(WORK,'text_only.txt'),'rb').read(); txt=quopri.decodestring(raw).decode('utf-8','replace')
ROOMS={'AAAALofXX3I':'Christine & Ownership','AAAA5WGJYgc':'Managers'}
bounds=sorted((m.start(),ROOMS[m.group(1)]) for m in re.finditer(r'(AAAALofXX3I|AAAA5WGJYgc)-MBI-FLAT',txt))
def room_at(pos):
    r='?'
    for p,nm in bounds:
        if p<=pos: r=nm
        else: break
    return r
def strip(s):
    s=re.sub(r'<[^>]+>',' ',s); 
    for a,b in [('\xa0',' '),('&amp;','&'),('&#39;',"'"),('&gt;','>'),('&lt;','<'),('&quot;','"')]: s=s.replace(a,b)
    return ' '.join(s.split())
MON={'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}
pat=re.compile(r'font-weight:700">([^<]+?)[\s\u00a0]*</span>\s*([A-Z][a-z]+ \d{1,2}, \d{4}[^<]*?)</div>\s*<div style="[^"]*white-space:pre-wrap[^"]*">(.*?)</div>',re.S)
KW=re.compile(r'\btom\b|wilson|\bdave\b|delaney|fired|firing|terminat|no longer|authorized|represent|subcontractor|\bsubs?\b|warn|meeting|corner',re.I)
rows=[]
for m in pat.finditer(txt):
    sender=m.group(1).strip(); ts=m.group(2).strip(); body=strip(m.group(3))
    mm=re.match(r'([A-Z][a-z]+) (\d{1,2}), (\d{4})',ts)
    if not mm: continue
    mon=MON.get(mm.group(1),0); day=int(mm.group(2)); yr=int(mm.group(3))
    if yr==2025 and mon==5 and 8<=day<=20 and KW.search(body):
        rows.append((day, int(re.search(r'at (\d+):(\d+):(\d+)',ts).group(1)) if re.search(r'at (\d+):',ts) else 0, ts, room_at(m.start()), sender.split('@')[0], body))
rows.sort(key=lambda x:(x[0],x[1]))
hdr=("WILSON MATTER - CHAT EXTRACT (SRC-0131)\nSource: SRC-0130 = Google Vault Chat export WILSON_chat_2026-07-21 (matter OMNI-LIT-2026-001)\n"
     "Rooms: 'Christine & Ownership' (AAAALofXX3I) and 'Managers' (AAAA5WGJYgc)\n"
     "Filter: 2025-05-08 to 2025-05-20, messages referencing Tom / Wilson / the warning meeting / termination.\n"
     "Attachments stripped; text only. Full authenticated export = SRC-0130 (preserved separately, 1.3 GB).\n"+('='*70)+'\n')
body='\n'.join('[%s | %s]\n  %s: %s'%(ts,rm,snd,bd) for _,_,ts,rm,snd,bd in rows)
outp=os.path.join(KEY,'SRC-0131_2025-05_Tom-termination-Wilson-warning-chat.txt')
open(outp,'w',encoding='utf-8').write(hdr+body)
print('SRC-0131 written: %d messages, %d bytes'%(len(rows),os.path.getsize(outp)))
print('sha=',hashlib.sha256(open(outp,'rb').read()).hexdigest())
# free the 1.4GB inner zip (master export stays in vault_export)
big=os.path.join(WORK,'WILSON_chat_2026-07-21_0.mbox.zip')
if os.path.exists(big): sz=os.path.getsize(big); os.remove(big); print('freed %.2f GB (%s)'%(sz/1e9, big))
