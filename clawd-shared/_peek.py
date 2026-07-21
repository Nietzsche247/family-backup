import zipfile, os
WORK=r'C:\Users\aaron\clawd-shared\_vault_work'
inner=os.path.join(WORK,'WILSON_chat_2026-07-21_0.mbox.zip')
with zipfile.ZipFile(inner) as z:
    with z.open('WILSON_chat_2026-07-21_0.mbox') as f:
        data=f.read(9000)
open(r'C:\Users\aaron\clawd-shared\_peek.txt','w',encoding='utf-8').write(data.decode('latin-1'))
print('wrote', len(data),'bytes to _peek.txt')
