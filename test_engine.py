import pandas as pd
from datetime import datetime
from modules.engine import calculate_economics
from modules.gsheets import DEFAULT_CONFIG

activities_mock = [
    {'name': 'Estudios Exploratorios', 'year': 2018, 'capex': 20000000},
    {'name': 'Perforación Exploratoria', 'year': 2019, 'capex': 10000000},
    {'name': 'Pozos Delimitadores', 'year': 2020, 'capex': 20000000},
    {'name': 'Ingeniería Plataforma', 'year': 2021, 'capex': 100000000},
    {'name': 'Instalación Plataforma', 'year': 2022, 'capex': 30000},
    {'name': 'Pozo 1', 'year': 2023, 'capex': 8160000},
    {'name': 'Pozo 2', 'year': 2024, 'capex': 8160000},
    {'name': 'Pozo 3', 'year': 2025, 'capex': 8160000},
    {'name': 'Pozo 4', 'year': 2026, 'capex': 8160000},
    {'name': 'Pozo 5', 'year': 2027, 'capex': 8160000},
]

params = {
    'start_date': datetime.strptime(DEFAULT_CONFIG['start_date'], "%Y-%m-%d"),
    'initial_prod': DEFAULT_CONFIG['initial_prod']['val'],
    'decline_rate': DEFAULT_CONFIG['decline_rate']['val'],
    'availability': DEFAULT_CONFIG['availability']['val'],
    'reserves': DEFAULT_CONFIG['reserves']['val'],
    'price': DEFAULT_CONFIG['price']['val'],
    'opex': DEFAULT_CONFIG['opex']['val'],
    'tax_rate': DEFAULT_CONFIG['tax_rate']['val'],
    'discount_rate': DEFAULT_CONFIG['discount_rate']['val'],
    'activities': activities_mock
}

try:
    df, kpis = calculate_economics(params)
    print("KPIs:")
    for k, v in kpis.items():
        print(f"  {k}: {v}")
    
    print("\nSample DataFrame (Selected columns):")
    print(df[['Year', 'Avail_Prod_MBPD', 'Cum_Prod_MMbbls', 'CAPEX_MMUSD', 'OPEX_MMUSD', 'Cash_Flow_MMUSD']].head(10))
    print("Test passed successfully.")
except Exception as e:
    import traceback
    traceback.print_exc()
