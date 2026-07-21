import os, time, zipfile
dl=r'C:\Users\aaron\Downloads'
fs=[f for f in os.listdir(dl) if f.lower().startswith('wilson_chat_2026-07-21') or ('chat' in f.lower() and '2026-07-21' in f.lower())]
print('Vault files in Downloads:')
for f in sorted(fs):
    p=os.path.join(dl,f); print('  %10d bytes  %s  %s'%(os.path.getsize(p), time.strftime('%H:%M:%S',time.localtime(os.path.getmtime(p))), f))
# find the zip and verify it opens (central directory intact = complete)
z=[f for f in fs if f.lower().endswith('.zip')]
if z:
    zp=os.path.join(dl,z[0])
    # stability check: size now vs 3s later
    s1=os.path.getsize(zp); time.sleep(3); s2=os.path.getsize(zp)
    print('\nzip size stable:', s1==s2, '(%d -> %d)'%(s1,s2))
    try:
        zf=zipfile.ZipFile(zp); info=zf.infolist()
        print('ZIP OPENS OK - %d entries:'%len(info))
        for i in info[:20]: print('   %14d  %s'%(i.file_size, i.filename))
    except Exception as e:
        print('ZIP OPEN FAILED (may still be writing):', e)
