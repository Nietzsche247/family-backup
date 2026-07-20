import sys, glob, os, re
out = []
def log(*a): out.append(' '.join(str(x) for x in a))

# 1. Change order grid
xp = r'C:\Users\aaron\Downloads\ChangeOrders.xlsx'
log("=== ChangeOrders.xlsx ===")
try:
    import openpyxl
    wb = openpyxl.load_workbook(xp, read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    log("sheet:", ws.title, "rows:", len(rows))
    log("HEADER:", rows[0])
    for r in rows:
        s = ' '.join(str(c) for c in r if c is not None)
        if any(t in s for t in ['Ramada','Schneider','Landscap','Softn','POND','Flipping','gate','Total','Subtotal','538,179','63,917','114,857','3,061','1,279','338,450']):
            log("ROW:", [c for c in r if c is not None])
    wb.close()
except Exception as e:
    log("openpyxl ERR:", repr(e))
    try:
        import pandas as pd
        for d in pd.read_html(xp)[:1]:
            log(d.head(60).to_string())
    except Exception as e2:
        log("read_html ERR:", repr(e2))

# 2. Buildertrend PDFs
def pdftext(p):
    try:
        import pdfplumber
        with pdfplumber.open(p) as pdf:
            return "\n".join((pg.extract_text() or "") for pg in pdf.pages)
    except Exception:
        try:
            from pypdf import PdfReader
        except Exception:
            from PyPDF2 import PdfReader
        r = PdfReader(p)
        return "\n".join((pg.extract_text() or "") for pg in r.pages)

for p in sorted(glob.glob(r'C:\Users\aaron\Downloads\Buildertrend*.pdf')):
    log("\n=== " + os.path.basename(p) + " (" + str(os.path.getsize(p)) + " bytes) ===")
    try:
        t = re.sub(r'[ \t]+',' ', pdftext(p))
        log(t[:1600])
    except Exception as e:
        log("PDF ERR:", repr(e))

open(r'C:\Users\aaron\clawd-shared\_co_dump.txt','w',encoding='utf-8').write("\n".join(out))
print("done lines:", len(out))
