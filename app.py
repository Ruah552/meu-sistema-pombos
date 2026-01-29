import streamlit as st
import pandas as pd
from math import radians, cos, sin, asin, sqrt
import io

# --- MOTOR DE CÁLCULO (PRECISÃO GPS) ---
def haversine(lat1, lon1, lat2, lon2):
    try:
        lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
        a = sin((lat2-lat1)/2)**2 + cos(lat1) * cos(lat2) * sin((lon2-lon1)/2)**2
        return (2 * asin(sqrt(a))) * 6371 * 1000 
    except: return 0.0

def calc_vel(dist_m, hs, ms, ss, hc, mc, sc):
    try:
        t_voo_min = ((hc*3600 + mc*60 + sc) - (hs*3600 + ms*60 + ss)) / 60
        return round(dist_m / t_voo_min, 3) if t_voo_min > 0 else 0.0
    except: return 0.0

# --- INICIALIZAÇÃO DA MEMÓRIA DO CLUBE ---
if 'db_socios' not in st.session_state: st.session_state['db_socios'] = pd.DataFrame(columns=["Nome", "Lat", "Lon"])
if 'db_pombos' not in st.session_state: st.session_state['db_pombos'] = pd.DataFrame(columns=["Anilha", "Dono"])
if 'historico' not in st.session_state: 
    st.session_state['historico'] = pd.DataFrame(columns=["Prova", "Modalidade", "Sócio", "Anilha", "Velocidade", "Pontos", "Tipo"])

st.set_page_config(page_title="SGC - Limeirense 1951", layout="wide")

# --- CABEÇALHO TRADICIONAL ---
st.markdown(f"""
    <div style="text-align: center; border: 4px solid #1b5e20; border-radius: 15px; padding: 20px; background-color: #f1f8e9; margin-bottom: 20px;">
        <h1 style="margin: 0; color: #1b5e20; font-family: 'Verdana';">Clube Columbófilo Limeirense</h1>
        <h3 style="margin: 0; color: #333;">Desde 1951 cultivando a tradição</h3>
        <p style="font-weight: bold; color: #2e7d32; margin-top: 10px;">SISTEMA DE GESTÃO - 10 PROVAS / 5 MODALIDADES</p>
    </div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("PAINEL DE CONTROLE", [
    "⚙️ Configurar Prova", 
    "👤 Gestão de Sócios", 
    "🐦 Cadastro de Anilhas", 
    "🚀 Lançar Resultados (3+3)", 
    "✏️ Corrigir Histórico", 
    "📊 Apuramento Geral",
    "📑 Mapas para Impressão"
])

modalidades = ["Filhotes", "Velocidade Adultos", "Meio Fundo Adultos", "Fundo Adultos", "Grande Fundo Adultos"]

# --- 1. CONFIGURAÇÃO (PONTOS AJUSTÁVEIS) ---
if menu == "⚙️ Configurar Prova":
    st.header("⚙️ Configurar Nova Solta")
    with st.container(border=True):
        m_sel = st.selectbox("Modalidade", modalidades)
        c1, c2 = st.columns(2)
        with c1:
            cid = st.text_input("Cidade da Solta")
            lat_s, lon_s = st.text_input("Lat (Solta)"), st.text_input("Lon (Solta)")
        with c2:
            p_ini = st.number_input("Pontos para o 1º Colocado", value=1000.0)
            p_dec = st.number_input("Perda por posição (Decréscimo)", value=1.0)
            st.write("**Horário da Solta**")
            hs, ms, ss = st.columns(3)
            h_s = hs.number_input("HH",0,23, key="h_s")
            m_s = ms.number_input("MM",0,59, key="m_s")
            s_s = ss.number_input("SS",0,59, key="s_s")
    if st.button("💾 Salvar Configuração de Prova", use_container_width=True):
        st.session_state[f'conf_{m_sel}'] = {"cid":cid, "lat":lat_s, "lon":lon_s, "h":h_s, "m":m_s, "s":s_s, "p":p_ini, "d":p_dec}
        st.success(f"Configuração para {m_sel} salva com sucesso!")

# --- 2. LANÇAMENTO (EVOLUÍDO COM VISIBILIDADE ALTA) ---
elif menu == "🚀 Lançar Resultados (3+3)":
    mod_v = st.selectbox("Lançar para:", modalidades)
    if f'conf_{mod_v}' not in st.session_state:
        st.error("Configure a prova primeiro!")
    else:
        conf = st.session_state[f'conf_{mod_v}']
        n_prova = st.number_input("Número da Prova (1 a 10)", 1, 10)
