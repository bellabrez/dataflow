from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.styles import Font, Fill


wb = load_workbook(filename="2P_log_test.xlsx", read_only=False)
#ws = wb['big_data']
#wb = Workbook()
#wb = wb.load()

# grab the active worksheet
ws = wb.active

col = ws.column_dimensions['B']
col.font = Font(bold=True)

# Data can be assigned directly to cells
ws['A1'] = 42

# Rows can also be appended
ws.append([1, 2, 3])

col = ws.column_dimensions['B']
col.font = Font(bold=True)

# Save the file
wb.save("2P_log_test_out.xlsx")