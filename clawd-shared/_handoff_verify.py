import os, hashlib, zipfile, re
M=r'C:\North_Star_Projects\WILSON_MATTER_WORKING_v1'
P=M+r'\HANDOFF_MASTER_2026-07-21.md'
txt=open(P,encoding='utf-8').read()
print('file      :', os.path.basename(P))
print('size      : %.1f KB'%(os.path.getsize(P)/1024))
print('lines     :', len(txt.splitlines()))
print('sections  :', len(re.findall(r'^## ', txt, re.M)))
print('tables    :', txt.count('|---'))
# style guards
print('\nSTYLE CHECK')
print('  em dashes        :', txt.count('\u2014') or 'none')
print('  the word "fast"  :', len(re.findall(r'\bfast\b', txt, re.I)) or 'none')
# section headers present
for h in re.findall(r'^## .*$', txt, re.M): print('   ', h)
# bundle integrity
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
    return h.hexdigest()
b=M+r'\WILSON_evidence_bundle_2026-07-21.zip'
with zipfile.ZipFile(b) as z: names=z.namelist()
print('\nBUNDLE INTEGRITY')
print('  SHA-256          :', sha(b))
print('  files            :', len(names))
print('  handoff_master in :', 'YES - PROBLEM' if any('handoff_master' in n.lower() for n in names) else 'NO - correct, internal only')
print('  Wilson.xlsx SHA  :', sha(M+r'\Wilson.xlsx'))
