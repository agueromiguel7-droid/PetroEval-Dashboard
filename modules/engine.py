import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import numpy_financial as npf

def calculate_economics(params):
    # 1. Timeline and Schedule Building
    schedule = []
    start = datetime(params['start_year'], 1, 1)
    
    dur = params['durations']
    var_cost = params['costs_var']
    fix_cost = params['costs_fix']
    
    # Sequence
    est_end = start + timedelta(days=dur['Estudios'])
    schedule.append({'Task': 'Estudios Exploratorios', 'Category': 'Estudios', 'Start': start, 'Finish': est_end, 
                     'Capex': dur['Estudios'] * var_cost['Estudios'] + fix_cost['Estudios']})
                     
    pex_end = est_end + timedelta(days=dur['Perf_Exp'])
    schedule.append({'Task': 'Perforación Exploratoria', 'Category': 'Perforación', 'Start': est_end, 'Finish': pex_end, 
                     'Capex': dur['Perf_Exp'] * var_cost['Perf_Exp'] + fix_cost['Perf_Exp']})
                     
    pdel_end = pex_end + timedelta(days=dur['Perf_Delim'])
    schedule.append({'Task': 'Pozos Delimitadores', 'Category': 'Perforación', 'Start': pex_end, 'Finish': pdel_end, 
                     'Capex': dur['Perf_Delim'] * var_cost['Perf_Delim'] + fix_cost['Perf_Delim']})
                     
    ing_end = pdel_end + timedelta(days=dur['Ing_Plat'])
    schedule.append({'Task': 'Ingeniería Plataforma', 'Category': 'Infraestructura', 'Start': pdel_end, 'Finish': ing_end, 
                     'Capex': dur['Ing_Plat'] * var_cost['Ing_Plat'] + fix_cost['Ing_Plat']})
                     
    inst_end = ing_end + timedelta(days=dur['Inst_Plat'])
    schedule.append({'Task': 'Instalación Plataforma', 'Category': 'Infraestructura', 'Start': ing_end, 'Finish': inst_end, 
                     'Capex': dur['Inst_Plat'] * var_cost['Inst_Plat'] + fix_cost['Inst_Plat']})
                     
    # Multi-Rig Well Drilling
    rigs_avail = [inst_end] * params['num_rigs']
    well_ends = []
    
    for i in range(8):
        rig_id = int(np.argmin(rigs_avail))
        w_start = rigs_avail[rig_id]
        w_end = w_start + timedelta(days=dur['Perf_Term'])
        rigs_avail[rig_id] = w_end
        
        schedule.append({'Task': f'Pozo {i+1}', 'Category': 'Perforación', 'Start': w_start, 'Finish': w_end, 
                         'Capex': dur['Perf_Term'] * var_cost['Perf_Term'] + fix_cost['Perf_Term'], 'Rig': f'Taladro {rig_id+1}'})
        well_ends.append(w_end)
        
    # 2. CAPEX Distribution per Year
    years = list(range(params['start_year'], params['start_year'] + params['project_duration']))
    df = pd.DataFrame({'Year': years})
    
    capex_per_year = {y: 0.0 for y in years}
    for task in schedule:
        capex = task['Capex']
        days = (task['Finish'] - task['Start']).days
        if days <= 0:
            y = task['Start'].year
            if y in capex_per_year: capex_per_year[y] += capex
            continue
            
        daily_c = capex / days
        curr = task['Start']
        while curr < task['Finish']:
            y = curr.year
            if y in capex_per_year:
                capex_per_year[y] += daily_c
            curr += timedelta(days=1)
            
    df['CAPEX_MMUSD'] = df['Year'].map(capex_per_year) / 1e6
    
    # 3. Continuous Staggered Production
    df_monthly_list = []
    total_avail_prod_mbpd = [0.0] * len(years)
    cum_prod_mmbls = [0.0] * len(years)
    
    well_rates = params['wells_initial_prod'].copy() # BPD
    D_daily = params['decline_rate'] / 365.0
    reserves_bbl = params['reserves'] * 1e6
    total_extracted = 0.0
    
    for y_idx, y in enumerate(years):
        y_total_prod_bbl = 0.0
        
        for month in range(1, 13):
            month_start = datetime(y, month, 1)
            if month == 12:
                month_end = datetime(y, 12, 31)
            else:
                month_end = datetime(y, month + 1, 1) - timedelta(days=1)
                
            m_total_prod_bbl = 0.0
            
            for i in range(8):
                w_end = well_ends[i]
                if month_end < w_end:
                    continue # Well not producing this month
                
                prod_start = max(month_start, w_end)
                days_prod = (month_end - prod_start).days + 1
                if days_prod <= 0:
                    continue
                    
                q_i = well_rates[i]
                if D_daily > 0:
                    prod_bbl = (q_i / D_daily) * (1 - np.exp(-D_daily * days_prod))
                else:
                    prod_bbl = q_i * days_prod
                    
                well_rates[i] = q_i * np.exp(-D_daily * days_prod)
                m_total_prod_bbl += prod_bbl
                
            m_total_prod_bbl *= params['availability']
            
            if total_extracted + m_total_prod_bbl > reserves_bbl:
                m_total_prod_bbl = max(0, reserves_bbl - total_extracted)
                
            total_extracted += m_total_prod_bbl
            y_total_prod_bbl += m_total_prod_bbl
            
            days_in_month = (month_end - month_start).days + 1
            df_monthly_list.append({
                'Date': month_start.strftime("%Y-%m"),
                'Monthly_Prod_MBPD': m_total_prod_bbl / days_in_month / 1000.0,
                'Cum_Prod_MMbbls': total_extracted / 1e6
            })
        
        total_avail_prod_mbpd[y_idx] = y_total_prod_bbl / 1000.0 / 365.0
        cum_prod_mmbls[y_idx] = total_extracted / 1e6
        
    df_monthly = pd.DataFrame(df_monthly_list)
    df['Avail_Prod_MBPD'] = total_avail_prod_mbpd
    df['Cum_Prod_MMbbls'] = cum_prod_mmbls
    
    df['Revenue_MMUSD'] = (df['Avail_Prod_MBPD'] * 365 * 1000.0) * params['price'] / 1e6
    df['OPEX_MMUSD'] = (df['Avail_Prod_MBPD'] * 365 * 1000.0) * params['opex'] / 1e6
    df['Taxes_MMUSD'] = df['Revenue_MMUSD'] * params['tax_rate']
    df['Cash_Flow_MMUSD'] = df['Revenue_MMUSD'] - df['OPEX_MMUSD'] - df['CAPEX_MMUSD'] - df['Taxes_MMUSD']
    df['Cum_Cash_Flow'] = df['Cash_Flow_MMUSD'].cumsum()
    
    # Financials
    npv = npf.npv(params['discount_rate'], df['Cash_Flow_MMUSD'].values)
    try:
        tir = npf.irr(df['Cash_Flow_MMUSD'].values)
    except:
        tir = np.nan
        
    pv_capex = npf.npv(params['discount_rate'], df['CAPEX_MMUSD'].values)
    inv_efficiency = npv / pv_capex if pv_capex != 0 else 0
    
    payback_period = "N/A"
    for idx, row in df.iterrows():
        if row['Cum_Cash_Flow'] > 0:
            prev_ccf = df.iloc[idx-1]['Cum_Cash_Flow'] if idx > 0 else 0
            if prev_ccf < 0:
                fraction = abs(prev_ccf) / row['Cash_Flow_MMUSD'] if row['Cash_Flow_MMUSD'] > 0 else 0
                payback_period = round(idx + fraction, 2)
                break
                
    kpis = {
        'VPN_MMUSD': npv,
        'TIR': tir,
        'Total_CAPEX': df['CAPEX_MMUSD'].sum(),
        'Total_OPEX': df['OPEX_MMUSD'].sum(),
        'Total_Taxes': df['Taxes_MMUSD'].sum(),
        'Total_Prod': df['Cum_Prod_MMbbls'].iloc[-1],
        'Inv_Efficiency': inv_efficiency,
        'Payback_Period': payback_period
    }
    
    return df, kpis, schedule, df_monthly
