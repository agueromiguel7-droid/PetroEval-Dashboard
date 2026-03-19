import pandas as pd
import json

file_path = "MEIPO - SOLUCIÓN.xlsm"
output_file = "excel_dump.txt"
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        xl = pd.ExcelFile(file_path)
        f.write(f"Sheets: {xl.sheet_names}\n")
        for sheet in xl.sheet_names:
            f.write(f"\n--- Sheet: {sheet} ---\n")
            df = xl.parse(sheet, nrows=50)
            f.write(df.to_string())
except Exception as e:
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Error: {e}")
