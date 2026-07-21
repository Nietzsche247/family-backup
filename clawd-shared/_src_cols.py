import sys
sys.path.insert(0, r'C:\Users\Aaron\.claude\skills\omni-litigation-engine\scripts')
from omni_core import load_json_strict, col_map
from openpyxl import load_workbook
s=load_json_strict(r'C:\North_Star_Projects\WILSON_MATTER_WORKING_v1\Wilson.schema.json')
wb=load_workbook(r'C:\North_Star_Projects\WILSON_MATTER_WORKING_v1\Wilson.xlsx')
cm=col_map(s,'SOURCE INDEX')
print('SOURCE INDEX COLS:')
for k,v in cm.items(): print('  %d = %r'%(v,k))
