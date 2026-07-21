import zipfile, os, re, time
WORK=r'C:\Users\aaron\clawd-shared\_vault_work'
inner=os.path.join(WORK,'WILSON_chat_2026-07-21_0.mbox.zip')
b64=re.compile(rb'^[A-Za-z0-9+/]{64,}={0,2}[\r\n]*$')
outp=os.path.join(WORK,'text_only.txt'); out=open(outp,'wb')
kept=0; total=0; t=time.time()
with zipfile.ZipFile(inner) as z:
    with z.open('WILSON_chat_2026-07-21_0.mbox') as f:
        for line in f:
            total+=1
            if b64.match(line): continue
            out.write(line); kept+=1
out.close()
print('done in %.0fs'%(time.time()-t))
print('total lines=%d kept=%d dropped=%d'%(total,kept,total-kept))
print('text_only.txt = %.1f MB'%(os.path.getsize(outp)/1e6))
