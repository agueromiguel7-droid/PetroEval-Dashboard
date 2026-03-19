import re

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Inject make_slider function after config_dict = get_config()
make_slider_func = '''
config_dict = get_config()

def make_slider(key_id, is_number=False):
    cfg = config_dict.get(key_id)
    if not cfg:
        st.warning(f"Clave {key_id} no encontrada.")
        return 0
    
    min_v, max_v, val, step = cfg['min'], cfg['max'], cfg['val'], cfg['step']
    if step.is_integer():
        min_v, max_v, val, step = int(min_v), int(max_v), int(val), int(step)
    
    if is_number:
        return st.number_input(cfg['name'], min_value=min_v, max_value=max_v, value=val, step=step, key=key_id)
    else:
        return st.slider(cfg['name'], min_value=min_v, max_value=max_v, value=val, step=step, key=key_id)

'''
text = text.replace('config = get_config()', make_slider_func)
text = text.replace("config['tax_rate']['val']", "0.50")
text = text.replace("config['discount_rate']['val']", "0.12")

# 2. Patch SIM_CONFIG loop 
sim_old = '''        SIM_CONFIG = {
            'reserves_in': (10.0, 200.0, 0.1),
            'price_in': (10.0, 200.0, 1.0),
            'opex_in': (1.0, 100.0, 1.0),
            'decline_in': (0.01, 0.50, 0.01),
            'avail_in': (0.5, 1.0, 0.01),
            'rigs_in': (1, 8, 1),
        }
        for i in range(8):
            SIM_CONFIG[f'well_{i}_in'] = (0, 10000, 100)

        cost_bounds = {
            'Estudios': ((0, 100000, 1000), (0, 50000000, 500000)),
            'Perf_Exp': ((0, 100000, 1000), (0, 30000000, 500000)),
            'Perf_Delim': ((0, 100000, 1000), (0, 50000000, 500000)),
            'Ing_Plat': ((0, 200000, 5000), (0, 200000000, 1000000)),
            'Inst_Plat': ((0, 100000, 1000), (0, 10000000, 100000)),
            'Perf_Term': ((0, 150000, 1000), (0, 20000000, 100000))
        }
        for k, (var_b, fix_b) in cost_bounds.items():
            SIM_CONFIG[f'{k}_var_in'] = var_b
            SIM_CONFIG[f'{k}_fix_in'] = fix_b

        dur_bounds = {
            'Estudios': (0, 360, 5),
            'Perf_Exp': (0, 180, 1),
            'Perf_Delim': (0, 180, 1),
            'Ing_Plat': (0, 360, 5),
            'Inst_Plat': (0, 360, 5),
            'Perf_Term': (0, 90, 1)
        }
        for k, b in dur_bounds.items():
            SIM_CONFIG[f'{k}_dur_in'] = b

        for k, (min_v, max_v, step_v) in SIM_CONFIG.items():
            steps = int(round((max_v - min_v) / step_v))'''

sim_new = '''        for k, cfg in config_dict.items():
            if k in ['start_year_in', 'proj_dur_in']: continue
            min_v, max_v, step_v = cfg['min'], cfg['max'], cfg['step']
            try: steps = int(round((max_v - min_v) / step_v))
            except: steps = 1'''

text = text.replace(sim_old, sim_new)

# 3. Patch explicitly coded sliders
text = re.sub(r'st\.slider\([^)]*, key="([^"]+)"\)', r'make_slider("\1")', text)
text = re.sub(r'st\.number_input\([^)]*, key="([^"]+)"\)', r'make_slider("\1", is_number=True)', text)
text = re.sub(r'st\.slider\([^)]*key="([^"]+)"\)', r'make_slider("\1")', text)
text = re.sub(r'st\.number_input\([^)]*key="([^"]+)"\)', r'make_slider("\1", is_number=True)', text)

# Write output
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Patching successful!")
