import email, re
from email import policy
SRC=r'C:\North_Star_Projects\WILSON_MATTER_WORKING_v1\preserved\keydocs\SRC-0123_2026-07-20_payment-history-reply.eml'
m=email.message_from_bytes(open(SRC,'rb').read(),policy=policy.default)
html=''
for p in m.walk():
    if p.get_content_type()=='text/html':
        try: html+=p.get_content()
        except: pass
# order the cids as extracted
cids=['ii_mrtfd47i0','ii_mrtfj5al2','ii_mrtflgmu3','ii_mrtfnk9y4','ii_mrtfsu1c5','ii_mrtftirg6','ii_mrtfu7fh7']
# replace <img ... cid ...> with a marker [IMG-N]
def repl(mm):
    tag=mm.group(0)
    for i,cid in enumerate(cids,1):
        if cid in tag: return ' [[IMG-%d]] '%i
    return ' [[IMG-?]] '
h2=re.sub(r'<img[^>]*>',repl,html,flags=re.I)
h2=re.sub(r'(?is)<(script|style).*?</\1>',' ',h2); h2=re.sub(r'<br[^>]*>','\n',h2,flags=re.I); h2=re.sub(r'</(p|div|li|tr)>','\n',h2,flags=re.I)
h2=re.sub(r'<[^>]+>',' ',h2)
h2=h2.replace('&nbsp;',' ').replace('&amp;','&').replace('&#39;',"'").replace('&gt;','>').replace('&lt;','<').replace('&quot;','"')
h2='\n'.join(ln.strip() for ln in h2.split('\n') if ln.strip())
print(h2[:2500])
