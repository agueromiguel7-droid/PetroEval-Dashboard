import pandas as pd
import json

file_path = "MEIPO - SOLUCIÓN.xlsm"
try:
    xl = pd.ExcelFile(file_path)
    print("Sheets:", xl.sheet_names)
    for sheet in xl.sheet_names:
        print(f"\n--- Sheet: {sheet} ---")
        df = xl.parse(sheet, nrows=50) # Read first 50 rows
        print(df.head(40).to_string())
except Exception as e:
    print("Error:", e)
