import sys
out = []
p = r'C:\Users\aaron\Downloads\EstimateReport.xls'
try:
    import pandas as pd
except Exception as e:
    open(r'C:\Users\aaron\clawd-shared\_estimate_dump.txt','w',encoding='utf-8').write("NO pandas: "+repr(e))
    print("no pandas"); sys.exit()
try:
    import xlrd
    have_xlrd = True
except Exception:
    have_xlrd = False
out.append("xlrd_installed=" + str(have_xlrd))
try:
    xls = pd.ExcelFile(p)
    out.append("SHEETS: " + str(xls.sheet_names))
    for sn in xls.sheet_names:
        df = xls.parse(sn, header=None)
        out.append("\n=== %s shape=%s ===" % (sn, df.shape))
        for i, row in df.head(120).iterrows():
            vals = [str(x) for x in row.tolist() if str(x) not in ('nan','NaT','None','')]
            if vals:
                out.append(("r%d: " % i) + " | ".join(vals))
except Exception as e:
    out.append("PARSE ERR: " + repr(e))
open(r'C:\Users\aaron\clawd-shared\_estimate_dump.txt','w',encoding='utf-8').write("\n".join(out))
print("done", len(out))
