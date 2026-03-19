import pandas as pd

# 1. Variables Sheet
data_vars = [
    # KEY, DISPLAY_NAME, MIN, MAX, DEFAULT, STEP
    ('start_year_in', 'Año de inicio del proyecto', 2000, 2100, 2019, 1),
    ('proj_dur_in', 'Duración total de explotación', 1, 50, 20, 1),
    ('reserves_in', 'RESERVAS (MMBLS)', 10.0, 200.0, 41.32, 0.1),
    ('price_in', 'PRECIO CRUDO (USD/BL)', 10.0, 200.0, 63.0, 1.0),
    ('opex_in', 'OPEX (USD/BL)', 1.0, 100.0, 15.0, 1.0),
    ('decline_in', 'DECLINACIÓN ANUAL', 0.01, 0.50, 0.122, 0.01),
    ('avail_in', 'DISPONIBILIDAD SISTEMA', 0.5, 1.0, 0.95, 0.01),
    ('rigs_in', 'Cant. de Taladros Disponibles', 1, 8, 1, 1),
]

default_ips = [2505, 2500, 2300, 2600, 2800, 3000, 3100, 2500]
for i in range(8):
    data_vars.append((f'well_{i}_in', f'POZO {i+1} (BPD)', 0, 10000, default_ips[i], 100))

# Costos (Variable / Fijo)
cost_defaults = {
    'Estudios': (20000, 20000000),
    'Perf_Exp': (20000, 10000000),
    'Perf_Delim': (20000, 20000000),
    'Ing_Plat': (100000, 100000000),
    'Inst_Plat': (30000, 0),
    'Perf_Term': (50000, 8160000),
}
cost_bounds = {
    'Estudios': ((0, 100000, 1000), (0, 50000000, 500000)),
    'Perf_Exp': ((0, 100000, 1000), (0, 30000000, 500000)),
    'Perf_Delim': ((0, 100000, 1000), (0, 50000000, 500000)),
    'Ing_Plat': ((0, 200000, 5000), (0, 200000000, 1000000)),
    'Inst_Plat': ((0, 100000, 1000), (0, 10000000, 100000)),
    'Perf_Term': ((0, 150000, 1000), (0, 20000000, 100000))
}

for k in cost_bounds.keys():
    var_min, var_max, var_s = cost_bounds[k][0]
    fix_min, fix_max, fix_s = cost_bounds[k][1]
    def_var, def_fix = cost_defaults[k]
    data_vars.append((f'{k}_var_in', f'{k} (VAR/DÍA)', var_min, var_max, def_var, var_s))
    data_vars.append((f'{k}_fix_in', f'{k} (FIJO)', fix_min, fix_max, def_fix, fix_s))

# Duraciones
dur_defaults = {
    'Estudios': 95, 'Perf_Exp': 30, 'Perf_Delim': 50, 
    'Ing_Plat': 145, 'Inst_Plat': 190, 'Perf_Term': 15
}
dur_bounds = {
    'Estudios': (0, 360, 5), 'Perf_Exp': (0, 180, 1), 'Perf_Delim': (0, 180, 1),
    'Ing_Plat': (0, 360, 5), 'Inst_Plat': (0, 360, 5), 'Perf_Term': (0, 90, 1)
}
for k in dur_bounds.keys():
    d_min, d_max, d_s = dur_bounds[k]
    def_d = dur_defaults[k]
    data_vars.append((f'{k}_dur_in', f'{k} DURACIÓN (DÍAS)', d_min, d_max, def_d, d_s))

df_vars = pd.DataFrame(data_vars, columns=["VariableID", "Nombre Frontend", "Min", "Max", "Average/Default", "Paso"])

# 2. Usuarios Sheet
data_users = [
    ("Cliente1", "Miguel Aguero", "$2b$12$kwbFvF4ys83VW2qCKu63Q.BMh1IvDT/jxwRaJWDYiDNCU1LvkuyzW", "28/02/2026", True, "agueromiguel7@gmail.com"),
    ("Cliente2", "Michele Leccese", "$2b$12$xgi8jPICQbn0rAsiPrPSlult.wHArE.hQLmAc1ToV7NX2Kd65ouiy", "28/02/2026", True, "micheleleccesepetrucci@gmail.com"),
    ("Cliente3", "Jose Fariñas", "$2b$12$Dg9W7.afTRxnOBREDS4i8uQfB83qjKgGnGKnppiJIVXQNmST6isXW", "28/02/2026", True, "Farinasjg1@gmail.com")
]
df_users = pd.DataFrame(data_users, columns=["username", "name", "password_hash", "expiration_date", "active", "email"])

# Export
with pd.ExcelWriter("Plantilla_GoogleDrive_PetroEval.xlsx") as writer:
    df_vars.to_excel(writer, sheet_name="Variables", index=False)
    df_users.to_excel(writer, sheet_name="Usuarios", index=False)

print("Excel Template Generated Successfully!")
