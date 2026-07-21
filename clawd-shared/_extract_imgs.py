import os, email
from email import policy
SRC=r'C:\North_Star_Projects\WILSON_MATTER_WORKING_v1\preserved\keydocs\SRC-0123_2026-07-20_payment-history-reply.eml'
OUT=r'C:\North_Star_Projects\WILSON_MATTER_WORKING_v1\preserved\keydocs'
m=email.message_from_bytes(open(SRC,'rb').read(),policy=policy.default)
# collect the body HTML to see image order/context
html=''
for p in m.walk():
    if p.get_content_type()=='text/html':
        try: html+=p.get_content()
        except: pass
imgs=[p for p in m.walk() if (p.get_content_type() or '').startswith('image/')]
print('image parts:',len(imgs))
try:
    from PIL import Image
    import io
    havePIL=True
except: havePIL=False
paths=[]
for i,p in enumerate(imgs,1):
    data=p.get_payload(decode=True)
    ext=(p.get_content_subtype() or 'png')
    fn='SRC-0123_img_%d.%s'%(i,ext); fp=os.path.join(OUT,fn)
    open(fp,'wb').write(data); paths.append(fp)
    dim=''
    if havePIL:
        try:
            im=Image.open(io.BytesIO(data)); dim='%dx%d'%im.size; 
            im2=Image.open(io.BytesIO(data)); # aspect
            ar=im.size[0]/im.size[1]; dim+= '  aspect %.2f (%s)'%(ar, 'WIDE/invoice-like' if ar>1.1 else ('TALL/phone-like' if ar<0.8 else 'square-ish'))
        except Exception as e: dim='(dim err %s)'%e
    cid=p.get('Content-ID','') 
    print('  img %d: %s  %d bytes  %s  cid=%s'%(i,fn,len(data),dim,cid))
print('\nsaved %d images to keydocs'%len(paths))
