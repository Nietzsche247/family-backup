import os, re, email
from email import policy

ROOT = r'C:\North_Star_Projects\Litigation-Wilson\preserved\mail'
folders = ['aaron','allysa.redmon','build','christine.stewart','construction','martin','michael','scott.culver','veronica.leyva']
rx_wil = re.compile(r'wilson|davidwilson0', re.I)
rx_auth = re.compile(r'davidwilson0@yahoo', re.I)
rx_priv = re.compile(r'thomae|kimminau|defenselawtucson|jake@defense|@e\.read|read\.ai', re.I)
kwmap = [('tommy',re.compile(r'\btommy\b',re.I)),('trust',re.compile(r'trust',re.I)),
         ('warn',re.compile(r'\bwarn',re.I)),('banned/ban',re.compile(r'\bban(ned|s|)\b',re.I)),
         ('not authorized',re.compile(r'not authoriz',re.I)),('do not/don\'t',re.compile(r"do not|don't|dont",re.I)),
         ('garage',re.compile(r'garage',re.I)),('overlay',re.compile(r'overlay',re.I)),
         ('auction',re.compile(r'auction',re.I)),('hire',re.compile(r'\bhir(e|ed|ing)\b',re.I)),
         ('deal with',re.compile(r'deal with',re.I))]
seen=set(); A=[]; B=[]
def snip(t, rx, w=190):
    m=rx.search(t)
    if not m: return t[:260].strip()
    s=max(0,m.start()-w); e=min(len(t),m.end()+w); return ' '.join(t[s:e].split())
for fld in folders:
    d=os.path.join(ROOT,fld)
    for fn in os.listdir(d):
        if not fn.endswith('.eml'): continue
        p=os.path.join(d,fn)
        try:
            with open(p,'rb') as f: head=f.read(700000)
        except: continue
        low=head.lower()
        if b'wilson' not in low and b'tommy' not in low: continue
        try: m=email.message_from_bytes(open(p,'rb').read(),policy=policy.default)
        except: continue
        mid=str(m.get('message-id','') or fn)
        if mid in seen: continue
        seen.add(mid)
        subj=str(m.get('subject','') or ''); frm=str(m.get('from','') or ''); to=str(m.get('to','') or ''); cc=str(m.get('cc','') or ''); date=str(m.get('date','') or '')
        b=''
        try:
            for part in m.walk():
                if part.get_content_type()=='text/plain':
                    try: b+=(part.get_content() or '')[:100000]
                    except: pass
        except: pass
        hdrs=frm+' '+to+' '+cc+' '+subj; hay=hdrs+'\n'+b
        if not rx_wil.search(hay): continue
        priv=bool(rx_priv.search(hdrs))
        khits=[name for name,rx in kwmap if rx.search(subj+'\n'+b)]
        if rx_auth.search(frm):
            rx1=next((rx for name,rx in kwmap if name in khits), None)
            sn='[PRIV]' if priv else snip(b or subj, rx1 or rx_wil)
            A.append('WILSON-> %s/%s | %s | TO %s\n   SUBJ %s | kw:%s\n   >> %s' % (fld,fn,date,(to+' cc:'+cc)[:70],subj[:70],','.join(khits) or '-',sn[:380]))
        elif khits:
            rx1=next(rx for name,rx in kwmap if name in khits)
            sn='[PRIV]' if priv else snip(b or subj, rx1)
            B.append('[%s]%s %s/%s | %s | FROM %s -> %s\n   SUBJ %s\n   >> %s' % (','.join(khits),' [PRIV]' if priv else '',fld,fn,date,frm[:38],(to+' cc:'+cc)[:60],subj[:65],sn[:340]))
o=['##### BUCKET A: WILSON-AUTHORED EMAILS (%d) #####'%len(A)]+(A or ['(none)'])+['','##### BUCKET B: WILSON-CONTEXT + TOM/WARNING KEYWORDS (%d) #####'%len(B)]+(B or ['(none)'])
open(r'C:\Users\aaron\clawd-shared\_wilson_focus.txt','w',encoding='utf-8').write('\n\n'.join(o))
print('wilson-authored=%d  wilson-context-kw=%d'%(len(A),len(B)))
