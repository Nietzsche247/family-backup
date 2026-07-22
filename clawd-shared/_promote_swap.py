import os, shutil, hashlib
M=r'C:\North_Star_Projects\WILSON_MATTER_WORKING_v1'; DL=r'C:\Users\aaron\Downloads'
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
    return h.hexdigest()
assert not os.path.exists(M+r'\~$Wilson.xlsx'), 'Wilson.xlsx open in Excel'
# 1) backup + promote verified copy
bk=M+r'\Wilson_prewrite_backup_2026-07-21_RECONREPAIR.xlsx'
shutil.copy2(M+r'\Wilson.xlsx', bk); print('backup of pre-repair authoritative ->', os.path.basename(bk))
shutil.copy2(M+r'\Wilson_repaired.xlsx', M+r'\Wilson.xlsx'); print('PROMOTED Wilson_repaired.xlsx -> Wilson.xlsx')
wsha=sha(M+r'\Wilson.xlsx'); print('Wilson.xlsx SHA-256 =', wsha)
# 2) locate v3 strategy in Downloads
EXPECT='4a83b3b044622c52cea4c9e36060ca94b2b9bc98d79ac899d2022fd8e040ef81'
cand=[f for f in os.listdir(DL) if 'strategy' in f.lower() and 'v3' in f.lower() and f.lower().endswith('.xlsx')]
if not cand: cand=[f for f in os.listdir(DL) if 'counsel_strategy' in f.lower() and f.lower().endswith('.xlsx')]
print('\nv3 candidates in Downloads:', cand)
if cand:
    src=os.path.join(DL,cand[0]); vsha=sha(src)
    print('found:', cand[0]); print('  its SHA-256 =', vsha)
    print('  EXPECTED    =', EXPECT)
    print('  MATCH =', vsha.lower()==EXPECT.lower())
    if vsha.lower()==EXPECT.lower():
        dst=M+r'\Wilson_Counsel_Strategy_v3.xlsx'
        shutil.move(src,dst); print('  MOVED to matter folder ->', os.path.basename(dst))
    else:
        print('  *** SHA MISMATCH - NOT MOVING; strategy swap halted ***')
else:
    print('  *** v3 file not found in Downloads ***')
# 3) get the stale frozen strategy out of the way (so it cannot be bundled)
old=M+r'\Wilson_Counsel_Strategy.xlsx'
if os.path.exists(old):
    try:
        arch=M+r'\Wilson_Counsel_Strategy_SUPERSEDED_2026-07-17.xlsx'
        if os.path.exists(arch): os.remove(arch)
        shutil.move(old,arch); print('\nstale frozen strategy renamed ->', os.path.basename(arch))
    except Exception as e:
        print('\ncould not rename stale strategy (likely still open in Excel):', e, '- will exclude from bundle by name regardless')
else:
    print('\nold frozen strategy already gone')
