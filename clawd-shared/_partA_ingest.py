import os, email, re, shutil, hashlib, time
from email import policy
from email.utils import parsedate_to_datetime
DL=r'C:\Users\aaron\Downloads'; KEY=r'C:\North_Star_Projects\WILSON_MATTER_WORKING_v1\preserved\keydocs'
def sha(p): return hashlib.sha256(open(p,'rb').read()).hexdigest()
def text(m):
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
    h=re.sub(r'(?is)<(script|style).*?</\1>',' ',h); h=re.sub(r'<[^>]+>',' ',h)
    return h.replace('&nbsp;',' ').replace('&amp;','&').replace('&#39;',"'").replace('&gt;','>').replace('&lt;','<')
def top(b):
    for sep in ['\nOn ','\n> ','-----Original','________','Sent from my']: b=b.split(sep)[0]
    return ' '.join(b.split())
# the 3 files
files=[f for f in os.listdir(DL) if f.lower().endswith('.eml') and 'arranties and job' in f.lower()]
files=sorted(files, key=lambda f: os.path.getmtime(os.path.join(DL,f)))
print('found',len(files),'files')
result={}
for f in files:
    p=os.path.join(DL,f); m=email.message_from_bytes(open(p,'rb').read(),policy=policy.default)
    dt=parsedate_to_datetime(m.get('date')); d=dt.date().isoformat() if dt else '?'
    subj=str(m.get('subject','') or ''); frm=str(m.get('from','') or ''); to=str(m.get('to','') or '')
    atts=[pp.get_filename() for pp in m.walk() if pp.get_filename()]
    print('\nFILE %r'%f); print('  date=%s subj=%s'%(d,subj[:50])); print('  from=%s to=%s'%(frm[:40],to[:50])); print('  atts=%s'%atts)
    print('  >>',top(text(m))[:400])
    result[d]=(f,m,atts)
# classify by date and preserve
def preserve(srcdate, dstname):
    f,m,atts=result[srcdate]; src=os.path.join(DL,f); dst=os.path.join(KEY,dstname)
    shutil.copy2(src,dst); return dst, sha(dst), atts, m
print('\n=== PRESERVE ===')
if '2026-07-19' in result:
    d,h,a,m=preserve('2026-07-19','SRC-0118_2026-07-19_Wilson-cornered.eml'); print('SRC-0118 (finalize) sha=',h)
if '2026-07-17' in result:
    d,h,a,m=preserve('2026-07-17','SRC-0121_2026-07-17_Warranties-letter.eml'); print('SRC-0121 sha=',h)
    for pp in m.walk():
        fn=pp.get_filename() or ''
        if fn.lower().endswith('.pdf'):
            pdst=os.path.join(KEY,'SRC-0122_2026-07-17_David-Wilson-warranty-position.pdf')
            open(pdst,'wb').write(pp.get_payload(decode=True)); print('SRC-0122 (attach %s) sha='%fn, sha(pdst))
if '2026-07-20' in result:
    d,h,a,m=preserve('2026-07-20','SRC-0123_2026-07-20_payment-history-reply.eml'); print('SRC-0123 sha=',h)
