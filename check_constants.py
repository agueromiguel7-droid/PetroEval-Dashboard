import openpyxl

file_path = "MEIPO - SOLUCIÓN.xlsm"

try:
    wb = openpyxl.load_workbook(file_path, data_only=True)
    sheet = wb["Eval. Econ. Proy"]
    
    cells_to_check = ['D45', 'C65', 'C55', 'C56', 'C54', 'C49', 'C50', 'C52', 'C51']
    print("Constants Check:")
    for c in cells_to_check:
        print(f"{c}: {sheet[c].value}")
        
except Exception as e:
    print(f"Error: {e}")
