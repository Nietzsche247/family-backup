import sys, os
try:
    import win32com.client as win32
    import pythoncom
except Exception as e:
    print('PYWIN32_MISSING:', e); sys.exit(2)
path=r'C:\North_Star_Projects\WILSON_MATTER_WORKING_v1\Wilson_repaired.xlsx'
pythoncom.CoInitialize()
try:
    xl=win32.DispatchEx('Excel.Application')
except Exception as e:
    print('EXCEL_LAUNCH_FAILED:', e); sys.exit(3)
xl.Visible=False; xl.DisplayAlerts=False
try: xl.AskToUpdateLinks=False
except: pass
errors=[]
try:
    wb=xl.Workbooks.Open(path, UpdateLinks=0, ReadOnly=False)
    xl.CalculateFullRebuild()
    for ws in wb.Worksheets:
        try: rng=ws.UsedRange
        except: continue
        try:
            ec=rng.SpecialCells(-4123, 16)  # xlCellTypeFormulas, xlErrors
            for cell in ec: errors.append((ws.Name, cell.Address(False,False), str(cell.Text)))
        except Exception: pass
    wb.Save(); wb.Close(SaveChanges=True)
    print('RECALC_OK  formula_error_cells=%d'%len(errors))
    for e in errors[:80]: print('  ERR', e)
finally:
    try: xl.Quit()
    except: pass
    pythoncom.CoUninitialize()
