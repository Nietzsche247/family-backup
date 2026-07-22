import os, re
SD=r'C:\Users\Aaron\.claude\skills\omni-litigation-engine\scripts'
for f in sorted(os.listdir(SD)):
    if not f.endswith('.py'): continue
    p=os.path.join(SD,f)
    txt=open(p,encoding='utf-8',errors='replace').read()
    lines=txt.splitlines()
    doc=''
    m=re.search(r'^\s*(?:"""|\'\'\')(.*?)(?:"""|\'\'\')', txt, re.S|re.M)
    if m: doc=' '.join(m.group(1).split())[:150]
    if not doc:
        for ln in lines[:12]:
            if ln.strip().startswith('#') and len(ln.strip())>3:
                doc=ln.strip('# ').strip()[:150]; break
    args=re.findall(r'add_argument\(\s*["\']([^"\']+)["\']', txt)
    print('%-24s %5d lines | %s'%(f, len(lines), doc or '(no docstring)'))
    if args: print('%-24s   args: %s'%('', ', '.join(args[:12])))
