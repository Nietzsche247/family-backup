import os, re, quopri
WORK=r'C:\Users\aaron\clawd-shared\_vault_work'
raw=open(os.path.join(WORK,'text_only.txt'),'rb').read()
txt=quopri.decodestring(raw).decode('utf-8','replace')
ROOMS={'AAAALofXX3I':'Christine & Ownership','AAAA5WGJYgc':'Managers'}
# room boundaries by position
bounds=[]
for m in re.finditer(r'(AAAALofXX3I|AAAA5WGJYgc)-MBI-FLAT', txt):
    bounds.append((m.start(), ROOMS[m.group(1)]))
bounds.sort()
def room_at(pos):
    r='?'
    for p,nm in bounds:
        if p<=pos: r=nm
        else: break
    return r
def strip(s):
    s=re.sub(r'<[^>]+>',' ',s); s=s.replace('\xa0',' ').replace('&amp;','&').replace('&#39;',"'").replace('&gt;','>').replace('&lt;','<').replace('&quot;','"')
    return ' '.join(s.split())
MON={'January':1,'February':2,'March':3,'April':4,'May':5,'June':6,'July':7,'August':8,'September':9,'October':10,'November':11,'December':12}
pat=re.compile(r'font-weight:700">([^<]+?)[\s\u00a0]*</span>\s*([A-Z][a-z]+ \d{1,2}, \d{4}[^<]*?)</div>\s*<div style="[^"]*white-space:pre-wrap[^"]*">(.*?)</div>', re.S)
KW=re.compile(r'tom|delaney|wilson|corner|warn|terminat|criminal|cortaro|7251|fired|let go|deviant', re.I)
out=[]; allmsgs=0; win=[]
for m in pat.finditer(txt):
    allmsgs+=1
    sender=m.group(1).strip(); ts=m.group(2).strip(); body=strip(m.group(3))
    mm=re.match(r'([A-Z][a-z]+) (\d{1,2}), (\d{4})', ts)
    if not mm: continue
    mon=MON.get(mm.group(1),0); day=int(mm.group(2)); yr=int(mm.group(3))
    rm=room_at(m.start())
    inwin = (yr==2025 and mon==5 and 12<=day<=26)
    kwhit = (yr==2025 and 4<=mon<=6 and KW.search(body))
    if inwin or kwhit:
        out.append((yr,mon,day,ts,rm,sender,body,'WIN' if inwin else 'KW'))
print('total chat messages parsed:', allmsgs)
print('matches (May 12-26 2025 OR Apr-Jun 2025 keyword):', len(out))
out.sort(key=lambda x:(x[0],x[1],x[2]))
lines=[]
for yr,mon,day,ts,rm,sender,body,tag in out:
    lines.append('[%s | %s] %s\n    %s: %s'%(tag,rm,ts,sender.split('@')[0],body[:600]))
open(os.path.join(WORK,'matches_5-19.txt'),'w',encoding='utf-8').write('\n\n'.join(lines))
print('\n'.join(lines[:60]) if lines else '(none)')
