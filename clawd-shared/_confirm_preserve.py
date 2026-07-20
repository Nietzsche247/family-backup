import hashlib, shutil, zipfile
import pandas as pd

p = r'C:\Users\aaron\Downloads\EstimateReport.xls'
df = pd.read_excel(p, header=0)
print("columns:", list(df.columns))
bc = pd.to_numeric(df['Builder Cost'], errors='coerce').sum()
cp = pd.to_numeric(df['Client Price'], errors='coerce').sum()
print("Builder Cost SUM:", round(bc,2))
print("Client Price SUM:", round(cp,2))
print("row count:", len(df))

# preserve to matter staging + hash
dst = r'C:\North_Star_Projects\WILSON_MATTER_WORKING_v1\staging4_financial\WILSON_BT_EstimateReport_original-estimate_exported_2026-07-20.xls'
shutil.copy2(p, dst)
h = hashlib.sha256(open(dst,'rb').read()).hexdigest()
print("PRESERVED:", dst)
print("SHA256:", h)

# peek snagx
sn = r'C:\Users\aaron\Downloads\2026-07-20_08-00-57.snagx'
print("--- SNAGX ---")
if zipfile.is_zipfile(sn):
    z = zipfile.ZipFile(sn)
    for n in z.namelist():
        print("  member:", n, z.getinfo(n).file_size)
else:
    print("not a zip; first bytes:", open(sn,'rb').read(12))
