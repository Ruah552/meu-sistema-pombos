import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from math import radians, cos, sin, asin, sqrt

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="SGC - Oficial", layout="wide")

def calcular_distancia(lat1, lon1, lat2, lon2):
    try:
        lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
        dlon, dlat = lon2 - lon1, lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        return (2 * asin(sqrt(a))) * 6371 * 1000 # Metros
    except: return 0

# --- CONEXÃO GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)
df_socios = conn.read(worksheet="Socios") # Precisa ter uma aba chamada 'Socios'

st.title("🕊️ SGC - Sistema de Gestão Columbófila")

menu = st.sidebar.radio("Navegação", ["⚙️ Prova", "👤 Sócios", "🚀 Lançar", "📊 Tabela"])

# 1. PROVA (Parametrização)
if menu == "⚙️ Prova":
    st.header("⚙️ Configuração da Solta")
    col1, col2 = st.columns(2)
    with col1:
        cid = st.text_input("Cidade", "Portalegre")
        lat_s = st.text_input("Lat Solta", "39.2921")
        lon_s = st.text_input("Lon Solta", "-7.4289")
    with col2:
        st.write("Hora Solta")
        h, m, s = st.columns(3)
        hs = h.number_input("H", 0, 23, 7)
        ms = m.number_input("M", 0, 59, 0)
        ss = s.number_input("S", 0, 59, 0)
    if st.button("Gravar Prova"):
        st.session_state['p'] = {"cid": cid, "lat": lat_s, "lon": lon_s, "h": hs, "m": ms, "s": ss}

# 2. LANÇAR (Regra 3+3 com dados do Sheets)
elif menu == "🚀 Lançar":
    if not df_socios.empty:
        socio_escolhido = st.selectbox("Selecione o Sócio", df_socios['Nome'].tolist())
        dados_s = df_socios[df_socios['Nome'] == socio_escolhido].iloc[0]
        
        st.write(f"**Coordenadas do Pombal:** {dados_s['Latitude']}, {dados_s['Longitude']}")
        
        chegadas = []
        for i in range(1, 7):
            tipo = "PONTUA" if i <= 3 else "EMPURRA"
            st.markdown(f"**Pombo {i} ({tipo})**")
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            anilha = c1.text_input("Anilha", key=f"ani_{i}", placeholder="2004466/26")
            hc = c2.number_input("H", 0, 23, key=f"h_{i}")
            mc = c3.number_input("M", 0, 59, key=f"m_{i}")
            sc = c4.number_input("S", 0, 59, key=f"s_{i}")
            # Cálculo de velocidade aqui...
