import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import locale

# Standard primary color for PetroEval AI
PRIMARY_COLOR = "#004A99"
SECONDARY_COLOR = "#006C49"
BACKGROUND_COLOR = "#F8F9FF"
CARD_BG = "#FFFFFF"
TEXT_COLOR = "#0B1C30"

def apply_custom_styles():
    st.markdown(f"""
    <style>
    /* STITCH UI Guidelines Application */
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;700&family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"]  {{
        font-family: 'Inter', sans-serif;
        background-color: {BACKGROUND_COLOR};
        color: {TEXT_COLOR};
    }}
    
    h1, h2, h3, .stMetric label {{
        font-family: 'Manrope', sans-serif !important;
        color: {TEXT_COLOR} !important;
    }}
    
    /* No 1px solid borders */
    div[data-testid="stMetricValue"] {{
        font-family: 'Manrope', sans-serif;
        font-weight: bold;
        color: {PRIMARY_COLOR};
        font-size: 1.4rem !important;
    }}
    
    div[data-testid="stMetricLabel"] {{
        font-size: 0.85rem !important;
    }}
    
    /* Card depth and xl roundedness */
    div[data-testid="stMetric"] {{
        background-color: {CARD_BG};
        padding: 0.5rem 0.8rem;
        border-radius: 1rem;
        box-shadow: 0 8px 24px -4px rgba(11, 28, 48, 0.04);
        border: none;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: #EFF4FF;
        border-right: none !important;
    }}
    
    /* Plotly container clean look */
    .stPlotlyChart {{
        background-color: {CARD_BG};
        border-radius: 1.5rem;
        padding: 10px;
        box-shadow: 0 12px 32px -4px rgba(11, 28, 48, 0.06);
    }}
    
    /* Slider Customization */
    .stSlider > div > div > div > div {{
        background: linear-gradient(90deg, {PRIMARY_COLOR} 0%, {SECONDARY_COLOR} 100%) !important;
    }}
    
    .stSlider > div > div > div > div[data-testid="stThumbValue"] {{
        color: {PRIMARY_COLOR};
        font-weight: 600;
        font-size: 0.9rem;
    }}
    
    .stSlider label {{
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        color: {PRIMARY_COLOR} !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    </style>
    """, unsafe_allow_html=True)

def render_kpis(kpis):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("VPN (Total)", f"$ {kpis['VPN_MMUSD']:,.2f} MM")
    with col2:
        tir_str = f"{kpis['TIR']*100:.1f} %" if kpis['TIR'] else "N/A"
        st.metric("TIR", tir_str)
    with col3:
        st.metric("Eficiencia Inv.", f"{kpis['Inv_Efficiency']:,.2f}")
    with col4:
        st.metric("Retorno (Años)", str(kpis['Payback_Period']))
        
    st.write("")
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("CAPEX Total", f"$ {kpis['Total_CAPEX']:,.2f} MM")
    with col6:
        st.metric("OPEX Total", f"$ {kpis['Total_OPEX']:,.2f} MM")
    with col7:
        st.metric("Prod Acumulada", f"{kpis['Total_Prod']:,.2f} MMBls")
        

def plot_cash_flow(df):
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['Year'], y=df['Cash_Flow_MMUSD'],
        name='Cash Flow',
        marker_color=PRIMARY_COLOR,
        opacity=0.8
    ))
    
    fig.add_trace(go.Scatter(
        x=df['Year'], y=df['Cum_Cash_Flow'],
        name='Cum Cash Flow',
        mode='lines+markers',
        line=dict(color=SECONDARY_COLOR, width=3)
    ))

    fig.update_layout(
        title="Flujo de Caja Anual vs Acumulado",
        font_family="Inter",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode="x unified",
        margin=dict(l=20, r=20, t=40, b=40),
        height=380,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)
    return fig

def plot_production(df_monthly):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Convert string dates to datetime to unlock Plotly's continuous dynamic time axis
    dates = pd.to_datetime(df_monthly['Date'])
    
    fig.add_trace(go.Scatter(
        x=dates, y=df_monthly['Monthly_Prod_MBPD'],
        name='Producción (MBPD)',
        mode='lines',
        line=dict(color=PRIMARY_COLOR, width=3),
        fill='tozeroy',
        fillcolor='rgba(0, 74, 153, 0.1)'
    ), secondary_y=False)
    
    fig.add_trace(go.Scatter(
        x=dates, y=df_monthly['Cum_Prod_MMbbls'],
        name='Acumulada (MMbls)',
        mode='lines',
        line=dict(color='#E06236', width=3)
    ), secondary_y=True)
    
    fig.update_layout(
        title="Pronóstico de Producción",
        font_family="Inter",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode="x unified",
        margin=dict(l=20, r=20, t=40, b=40),
        height=380,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig.update_xaxes(
        title_text="Fecha", 
        automargin=True, 
        tickformat="%b %Y" # Formats ticks as dynamic months, e.g. "Jan 2024"
    )
    fig.update_yaxes(title_text="Producción (MBPD)", secondary_y=False, rangemode="tozero")
    fig.update_yaxes(title_text="Acumulada (MMbls)", secondary_y=True, rangemode="tozero")
    
    return fig

import pandas as pd
import plotly.express as px

def plot_capex_distribution(schedule):
    df_sch = pd.DataFrame(schedule)
    df_agg = df_sch.groupby('Category')['Capex'].sum().reset_index()
    df_agg['Capex_MM'] = df_agg['Capex'] / 1e6
    
    total = df_agg['Capex_MM'].sum()
    
    fig = px.pie(df_agg, values='Capex_MM', names='Category', hole=0.7,
                 color_discrete_sequence=['#004A99', '#006C49', '#E06236', '#F4A261'])
    
    fig.update_layout(
        title="Distribución de Costos (CAPEX)",
        font_family="Inter",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=380,
        margin=dict(l=20, r=20, t=40, b=20),
        annotations=[dict(text=f"${total:,.1f} M<br>TOTAL CAPEX", x=0.5, y=0.5, font_size=16, font_family="Manrope", showarrow=False)]
    )
    return fig

def plot_total_cost_distribution(kpis):
    labels = ['CAPEX', 'OPEX', 'Impuestos']
    values = [kpis['Total_CAPEX'], kpis['Total_OPEX'], kpis['Total_Taxes']]
    
    total = sum(values)
    
    fig = px.pie(names=labels, values=values, hole=0.7,
                 color_discrete_sequence=['#004A99', '#006C49', '#D9534F'])
                 
    fig.update_layout(
        title="Resumen General de Costos",
        font_family="Inter",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=380,
        margin=dict(l=20, r=20, t=40, b=20),
        annotations=[dict(text=f"${total:,.1f} M<br>TOTAL GENERAL", x=0.5, y=0.5, font_size=16, font_family="Manrope", showarrow=False)]
    )
    return fig

def plot_gantt(schedule):
    df_sch = pd.DataFrame(schedule)
    tasks_order = df_sch['Task'].unique().tolist()[::-1] # Plotly draws Y-axis from bottom to top, so reverse chronological
    
    fig = px.timeline(df_sch, x_start="Start", x_end="Finish", y="Task", color="Category",
                      color_discrete_sequence=['#004A99', '#006C49', '#E06236'],
                      height=450)
                      
    fig.update_yaxes(categoryorder='array', categoryarray=tasks_order, title="") 
    fig.update_xaxes(title="")
    fig.update_layout(
        title="Cronograma del Proyecto (Gantt)",
        font_family="Inter",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig
