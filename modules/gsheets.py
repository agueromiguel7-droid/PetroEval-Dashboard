import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import bcrypt

def init_connection():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn
    except Exception as e:
        return None

@st.cache_data(ttl=600)
def get_config():
    """Fetches configuration from Google Sheets 'Variables' tab"""
    conn = init_connection()
    config_dict = {}
    
    # Definimos el fallback mock por si no hay conexión
    # (Usando algunos valores por defecto para que no falle)
    mock_data = [
        ('start_year_in', 'Año inicio', 2000, 2100, 2019, 1),
        ('proj_dur_in', 'Duración Total', 1, 50, 20, 1),
        ('reserves_in', 'RESERVAS', 10.0, 200.0, 41.32, 0.1),
        ('price_in', 'PRECIO', 10.0, 200.0, 63.0, 1.0),
        ('opex_in', 'OPEX', 1.0, 100.0, 15.0, 1.0),
        ('decline_in', 'DECLINACIÓN', 0.01, 0.50, 0.122, 0.01),
        ('avail_in', 'DISP', 0.5, 1.0, 0.95, 0.01),
        ('rigs_in', 'Taladros', 1, 8, 1, 1),
    ]
    for i in range(8): mock_data.append((f'well_{i}_in', f'POZO {i+1}', 0, 10000, 2500, 100))
    for k in ['Estudios', 'Perf_Exp', 'Perf_Delim', 'Ing_Plat', 'Inst_Plat', 'Perf_Term']:
        mock_data.append((f'{k}_var_in', f'{k}', 0, 100000, 20000, 1000))
        mock_data.append((f'{k}_fix_in', f'{k}', 0, 50000000, 10000000, 1000000))
        mock_data.append((f'{k}_dur_in', f'{k}', 0, 360, 50, 5))
        
    for m in mock_data:
        config_dict[m[0]] = {'min': m[2], 'max': m[3], 'val': m[4], 'step': m[5], 'name': m[1]}

    if conn is not None:
        try:
            df = conn.read(worksheet="Variables")
            if not df.empty:
                # Si hay datos de GS, sobreescribir config
                config_dict_gs = {}
                for _, row in df.iterrows():
                    vid = str(row['VariableID'])
                    if vid and vid != 'nan':
                        config_dict_gs[vid] = {
                            'min': float(row['Min']),
                            'max': float(row['Max']),
                            'val': float(row['Average/Default']),
                            'step': float(row['Paso']) if pd.notnull(row['Paso']) else 1.0,
                            'name': str(row['Nombre Frontend'])
                        }
                return config_dict_gs
        except Exception as e:
            st.error(f"Error cargando base 'Variables' en la nube: {e}")
            
    return config_dict

@st.cache_data(ttl=60)
def get_users():
    conn = init_connection()
    if conn is not None:
        try:
            df = conn.read(worksheet="Usuarios")
            return df
        except Exception as e:
            st.error(f"Error cargando accesos 'Usuarios' en la nube: {e}")
    # Fallback
    return pd.DataFrame([{"username": "admin", "password_hash": "$2b$12$kwbFvF4ys83VW2qCKu63Q.BMh1IvDT/jxwRaJWDYiDNCU1LvkuyzW", "expiration_date": "31/12/2030", "active": True}])

def check_login(username, password):
    users = get_users()
    if users.empty: return False, "No hay usuarios."
    
    if 'active' in users.columns:
        active_users = users[users['active'] == True]
        if active_users.empty:
            active_users = users[users['active'].astype(str).str.upper() == 'TRUE']
    else:
        active_users = users

    user_row = active_users[active_users['username'] == username]
    
    if not user_row.empty:
        hashed = str(user_row['password_hash'].values[0]).strip()
        try:
            if bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8')):
                exp_str = str(user_row['expiration_date'].values[0])
                try: expiration = pd.to_datetime(exp_str, format="%d/%m/%Y")
                except: expiration = pd.to_datetime(exp_str)

                if datetime.now() <= expiration:
                    return True, "Login exitoso"
                else:
                    return False, "Usuario expirado."
            else:
                return False, "Contraseña incorrecta."
        except Exception as e:
            return False, f"Error validando credenciales bcrypt: {e}"
    return False, "Usuario inválido o inactivo."
