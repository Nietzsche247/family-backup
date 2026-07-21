import os, shutil, hashlib, zipfile, time
DL=r'C:\Users\aaron\Downloads'; M=r'C:\North_Star_Projects\WILSON_MATTER_WORKING_v1'
VE=M+r'\vault_export'; WORK=r'C:\Users\aaron\clawd-shared\_vault_work'
os.makedirs(VE,exist_ok=True); os.makedirs(WORK,exist_ok=True)
files=[f for f in os.listdir(DL) if f.lower().startswith('wilson_chat_2026-07-21')]
print('moving %d master files to vault_export...'%len(files))
for f in files:
    src=os.path.join(DL,f); dst=os.path.join(VE,f)
    if os.path.exists(dst): os.remove(dst)
    shutil.move(src,dst); print('  moved',f)
# read Google's md5 manifest
md5f=[f for f in os.listdir(VE) if f.lower().endswith('.md5')]
if md5f:
    print('\nGoogle checksums (%s):'%md5f[0]); print(open(os.path.join(VE,md5f[0])).read())
# hash the outer zip (our own SHA-256 for provenance)
outer=os.path.join(VE,'WILSON_chat_2026-07-21-1.zip')
print('hashing outer zip (1.4G, be patient)...')
t=time.time(); h=hashlib.sha256()
with open(outer,'rb') as fh:
    for chunk in iter(lambda: fh.read(1024*1024),b''): h.update(chunk)
print('outer zip SHA-256 =', h.hexdigest(), '(%.0fs)'%(time.time()-t))
# extract inner .mbox.zip to WORK
with zipfile.ZipFile(outer) as z:
    inner=z.namelist()[0]; print('\nextracting inner:', inner)
    z.extract(inner, WORK)
innerpath=os.path.join(WORK,inner)
print('extracted %.2f GB'%(os.path.getsize(innerpath)/1e9))
with zipfile.ZipFile(innerpath) as z2:
    for i in z2.infolist()[:10]: print('   inner entry: %14d  %s'%(i.file_size,i.filename))
