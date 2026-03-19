import pandas as pd
from datetime import datetime
from modules.engine import calculate_economics

durations = {'Estudios': 95, 'Perf_Exp': 30, 'Perf_Delim': 50, 'Ing_Plat': 145, 'Inst_Plat': 190, 'Perf_Term': 15}
costs_var = {'Estudios': 20000, 'Perf_Exp': 20000, 'Perf_Delim': 20000, 'Ing_Plat': 100000, 'Inst_Plat': 30000, 'Perf_Term': 50000}
costs_fix = {'Estudios': 20000000, 'Perf_Exp': 10000000, 'Perf_Delim': 20000000, 'Ing_Plat': 100000000, 'Inst_Plat': 0, 'Perf_Term': 8160000}

params = {
    'base_start_date': datetime.strptime("2019-01-01", "%Y-%m-%d"),
    'availability': 0.95,
    'decline_rate': 0.122,
    'reserves': 41.32,
    'price': 63.0,
    'opex': 15.0,
    'tax_rate': 0.5,
    'discount_rate': 0.12,
    'wells_initial_prod': [2505, 2500, 2300, 2600, 2800, 3000, 3100, 2500],
    'costs_var': costs_var,
    'costs_fix': costs_fix,
    'durations': durations,
}

try:
    df, kpis = calculate_economics(params)
    print("KPIs V2 Calculation:")
    for k, v in kpis.items():
        print(f"  {k}: {v}")
        
    print("\nDataFrame tail:")
    print(df[['Year', 'Avail_Prod_MBPD', 'Cum_Prod_MMbbls', 'CAPEX_MMUSD', 'OPEX_MMUSD', 'Cash_Flow_MMUSD']].tail(5))
    print("Test passed successfully.")
except Exception as e:
    import traceback
    traceback.print_exc()
