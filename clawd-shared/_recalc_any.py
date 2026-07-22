import sys, os
try:
    import win32com.client as win32
    import pythoncom
except Exception as e:
    print('PYWIN32_MISSING:', e); sys.exit(2)
path=sys.argv[1]
pythoncom.CoInitialize()
xl=win32.DispatchEx('Excel.Application'); xl.Visible=False; xl.DisplayAlerts=False
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
            ec=rng.SpecialCells(-4123, 16)
            for cell in ec: errors.append((ws.Name, cell.Address(False,False), str(cell.Text)))
        except Exception: pass
    # echo the EXECUTIVE metric block so counsel-visible numbers are confirmed
    try:
        ex=wb.Worksheets('EXECUTIVE')
        print('EXECUTIVE metrics after recalc:')
        for r in range(15,23):
            print('   %-24s %s'%(str(ex.Cells(r,1).Value), str(ex.Cells(r,2).Text)))
    except Exception as e: print('metric echo skipped:',e)
    wb.Save(); wb.Close(SaveChanges=True)
    print('RECALC_OK  formula_error_cells=%d'%len(errors))
    for e in errors[:60]: print('  ERR',e)
finally:
    try: xl.Quit()
    except: pass
    pythoncom.CoUninitialize()
