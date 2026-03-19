import streamlit as st
from datetime import datetime
import pandas as pd
from PIL import Image
import os

from modules.gsheets import get_config, check_login
from modules.engine import calculate_economics
from modules.ui_components import (
    apply_custom_styles, render_kpis, plot_cash_flow, plot_production,
    plot_gantt, plot_capex_distribution, plot_total_cost_distribution
)

st.set_page_config(
    page_title="PetroEval AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_styles()

# ----------------- ZOOM LOGIC -----------------
# El menú de zoom se movió debajo del logo del sidebar

# ----------------- LOGIN LOGIC -----------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        logo_path = "mi_logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=150)
            
        st.title("Acceso de Usuario")
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        if st.button("Iniciar Sesión", type="primary"):
            success, msg = check_login(username, password)
            if success:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error(msg)
    st.stop()

# ----------------- MAIN APP -----------------

# Sidebar Configuration
with st.sidebar:
    logo_path = "mi_logo.png"
    if os.path.exists(logo_path):
        st.image(logo_path, width=200)

    if "simulating" not in st.session_state:
        st.session_state.simulating = False

    st.markdown("### 🎲 Simulación Montecarlo")
    
    col_sim, col_res = st.columns(2)
    with col_sim:
        btn_text = "⏹ Detener" if st.session_state.simulating else "▶ Iniciar auto"
        if st.button(btn_text, use_container_width=True, type="primary" if not st.session_state.simulating else "secondary"):
            st.session_state.simulating = not st.session_state.simulating
            st.rerun()
            
    with col_res:
        if st.button("🔄 Resetear", use_container_width=True):
            st.session_state.simulating = False
            for k in list(st.session_state.keys()):
                if k.endswith('_in'):
                    del st.session_state[k]
            st.rerun()

    if st.session_state.simulating:
        import random
        for k, cfg in config_dict.items():
            if k in ['start_year_in', 'proj_dur_in']: continue
            min_v, max_v, step_v = cfg['min'], cfg['max'], cfg['step']
            try: steps = int(round((max_v - min_v) / step_v))
            except: steps = 1
            chosen_step = random.randint(0, steps)
            val = min_v + chosen_step * step_v
            if isinstance(step_v, int):
                val = int(round(val))
            else:
                val = round(val, 4)
            st.session_state[k] = val
    st.markdown("---")
        
    zoom_factor = st.slider("Ajuste de Zoom (%)", min_value=50, max_value=150, value=85, step=5)
    st.markdown(f"<style> .stApp {{ zoom: {zoom_factor}%; }} </style>", unsafe_allow_html=True)
    
    st.markdown("### Configuración del Proyecto")
    with st.expander("🚀 Inicio y Duración", expanded=False):
        start_year = st.number_input("Año de inicio del proyecto", min_value=2000, max_value=2100, value=2019)
        project_duration = st.number_input("Duración total de explotación (años)", min_value=1, max_value=50, value=20)
    
    tabs = st.tabs(["Económicos", "Pozos", "Costos", "Tiempos"])
    
    with tabs[0]:
        reserves_input = st.slider("RESERVAS (MMBLS)", min_value=10.0, max_value=200.0, value=41.32, step=0.1, key="reserves_in")
        price_input = st.slider("PRECIO CRUDO (USD/BL)", min_value=10.0, max_value=200.0, value=63.0, step=1.0, key="price_in")
        opex_input = st.slider("OPEX (USD/BL)", min_value=1.0, max_value=100.0, value=15.0, step=1.0, key="opex_in")
        decline_rate_input = make_slider("decline_in")
        availability_input = make_slider("avail_in")

    with tabs[1]:
        st.markdown("#### Producción Inicial (BPD)")
        num_rigs = make_slider("rigs_in", is_number=True)
        wells_ip = []
        default_ips = [2505, 2500, 2300, 2600, 2800, 3000, 3100, 2500]
        for i in range(8):
            val = st.slider(f"POZO {i+1}", min_value=0, max_value=10000, value=default_ips[i], step=100, key=f"well_{i}_in")
            wells_ip.append(val)

    with tabs[2]:
        st.markdown("#### Costos (Variables / Fijos)")
        costs_var = {}
        costs_fix = {}
        
        costs_var['Estudios'] = st.slider("ESTUDIOS (VAR/DÍA)", min_value=0, max_value=100000, value=20000, step=1000, key="Estudios_var_in")
        costs_fix['Estudios'] = st.slider("ESTUDIOS (FIJO)", min_value=0, max_value=50000000, value=20000000, step=500000, key="Estudios_fix_in")
        
        costs_var['Perf_Exp'] = st.slider("PERF. EXPLORATORIA (VAR/D)", min_value=0, max_value=100000, value=20000, step=1000, key="Perf_Exp_var_in")
        costs_fix['Perf_Exp'] = st.slider("PERF. EXPLORATORIA (FIJO)", min_value=0, max_value=30000000, value=10000000, step=500000, key="Perf_Exp_fix_in")
        
        costs_var['Perf_Delim'] = st.slider("PERF. DELIMITADOR (VAR/D)", min_value=0, max_value=100000, value=20000, step=1000, key="Perf_Delim_var_in")
        costs_fix['Perf_Delim'] = st.slider("PERF. DELIMITADOR (FIJO)", min_value=0, max_value=50000000, value=20000000, step=500000, key="Perf_Delim_fix_in")
        
        costs_var['Ing_Plat'] = st.slider("ING. PLATAFORMA (VAR/D)", min_value=0, max_value=200000, value=100000, step=5000, key="Ing_Plat_var_in")
        costs_fix['Ing_Plat'] = st.slider("ING. PLATAFORMA (FIJO)", min_value=0, max_value=200000000, value=100000000, step=1000000, key="Ing_Plat_fix_in")
        
        costs_var['Inst_Plat'] = st.slider("INST. PLATAFORMA (VAR/D)", min_value=0, max_value=100000, value=30000, step=1000, key="Inst_Plat_var_in")
        costs_fix['Inst_Plat'] = st.slider("INST. PLATAFORMA (FIJO)", min_value=0, max_value=10000000, value=0, step=100000, key="Inst_Plat_fix_in")
        
        costs_var['Perf_Term'] = st.slider("PERF. POZOS (VAR/D)", min_value=0, max_value=150000, value=50000, step=1000, key="Perf_Term_var_in")
        costs_fix['Perf_Term'] = st.slider("PERF. POZOS (FIJO)", min_value=0, max_value=20000000, value=8160000, step=100000, key="Perf_Term_fix_in")

    with tabs[3]:
        st.markdown("#### Duraciones (días)")
        durations = {}
        durations['Estudios'] = make_slider("Estudios_dur_in")
        durations['Perf_Exp'] = make_slider("Perf_Exp_dur_in")
        durations['Perf_Delim'] = make_slider("Perf_Delim_dur_in")
        durations['Ing_Plat'] = make_slider("Ing_Plat_dur_in")
        durations['Inst_Plat'] = make_slider("Inst_Plat_dur_in")
        durations['Perf_Term'] = make_slider("Perf_Term_dur_in")
        
    st.markdown("---")
    if st.button("Cerrar Sesión"):
        st.session_state["authenticated"] = False
        st.rerun()


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



params = {
    'start_year': start_year,
    'project_duration': project_duration,
    'num_rigs': num_rigs,
    'base_start_date': datetime.strptime("2019-01-01", "%Y-%m-%d"), # This might need adjustment based on start_year
    'availability': availability_input,
    'decline_rate': decline_rate_input,
    'reserves': reserves_input,
    'price': price_input,
    'opex': opex_input,
    'tax_rate': 0.50, # Using config as per original
    'discount_rate': 0.12, # Using config as per original
    'wells_initial_prod': wells_ip,
    'costs_var': costs_var,
    'costs_fix': costs_fix,
    'durations': durations,
}

df, kpis, schedule, df_monthly = calculate_economics(params)

# Header
st.title("Project Evaluation Dashboard")
st.markdown("Evaluación Económica de Campo Petrolero PetroEval AI")

# KPIs
render_kpis(kpis)

# Charts
st.markdown("---")
# Plotting
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(plot_production(df_monthly), use_container_width=True)
with col2:
    st.plotly_chart(plot_cash_flow(df), use_container_width=True)
    
# Gantt Chart and Cost Charts
st.plotly_chart(plot_gantt(schedule), use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(plot_capex_distribution(schedule), use_container_width=True)
with col4:
    st.plotly_chart(plot_total_cost_distribution(kpis), use_container_width=True)

with st.expander("Ver Datos de Evaluación Detallados"):
    display_df = df.copy()
    display_df['Year'] = display_df['Year'].astype(str)
    currency_cols = ['CAPEX_MMUSD', 'Revenue_MMUSD', 'OPEX_MMUSD', 'Taxes_MMUSD', 'Cash_Flow_MMUSD', 'Cum_Cash_Flow']
    for col in currency_cols:
        display_df[col] = display_df[col].round(2)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

import time
if st.session_state.get('simulating', False):
    time.sleep(1.0)
    st.rerun()
