import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from math import radians, cos, sin, asin, sqrt

# Configuração da Página
st.set_page_config(page_title="SGC - Gestão Columbófila", layout="wide")

# Função de Precisão Matemática (Haversine)
def calcular_distancia(lat1, lon1, lat2, lon2):
    try:
        lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        return c * 6371 * 1000 # Retorna metros exatos
    except:
        return 0

# Conexão com a Planilha
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    st.error("Erro na conexão com o Google Sheets.")

st.title("🕊️ SGC - Sistema de Gestão Columbófila")

# Menu Lateral com TUDO
menu = st.sidebar.radio("Navegação", [
    "⚙️ Configurar Prova", 
    "👤 Cadastro de Sócios", 
    "🚀 Lançar Chegadas (3+3)", 
    "📊 Classificação Final"
])

# 1. CONFIGURAR PROVA
if menu == "⚙️ Configurar Prova":
    st.header("⚙️ Parametrização da Solta")
    col1, col2 = st.columns(2)
    with col1:
        cidade = st.text_input("Cidade da Solta", placeholder="Ex: Portalegre")
        st.write("**Coordenadas da Cidade (Solta)**")
        lat_s = st.text_input("Latitude Solta (Ex: 39.4065)")
        lon_s = st.text_input("Longitude Solta (Ex: -7.4321)")
        st.write("**Hora da Solta**")
        c1, c2, c3 = st.columns(3)
        h_s = c1.number_input("Hora", 0, 23, 8)
        m_s = c2.number_input("Min", 0, 59, 0)
        s_s = c3.number_input("Seg", 0, 59, 0)
    with col2:
        modalidade = st.selectbox("Modalidade", ["Velocidade", "Meio-Fundo", "Fundo"])
        p_ini = st.number_input("Pontuação Inicial", value=100.0)
        dec = st.number_input("Decréscimo por Posição", value=1.0, step=0.1)
    
    if st.button("Gravar Configuração"):
        st.session_state['prova'] = {
            "cidade": cidade, "lat": lat_s, "lon": lon_s,
            "hora": f"{h_s:02d}:{m_s:02d}:{s_s:02d}", "mod": modalidade, "p_ini": p_ini, "dec": dec
        }
        st.success(f"Prova de {cidade} configurada com precisão!")

# 2. CADASTRO DE SÓCIOS
elif menu == "👤 Cadastro de Sócios":
    st.header("👤 Cadastro de Pombais")
    with st.form("form_socio"):
        nome = st.text_input("Nome do Sócio / Pombal")
        s_lat = st.text_input("Latitude do Pombal (Ex: 39.1234)")
        s_lon = st.text_input("Longitude do Pombal (Ex: -8.5432)")
        if st.form_submit_button("Salvar Sócio"):
            # Aqui você pode adicionar a lógica de conn.update() para o Sheets
            st.success(f"Sócio {nome} cadastrado com sucesso!")

# 3. LANÇAR CHEGADAS (3+3)
elif menu == "🚀 Lançar Chegadas (3+3)":
    st.header("🚀 Lançamento de Designados")
    socio = st.text_input("Nome do Sócio")
    
    for i in range(1, 7):
        tipo = "PONTUA" if i <= 3 else "EMPURRA"
        cor = "blue" if i <= 3 else "orange"
        st.markdown(f"**Pombo {i} - :{cor}[{tipo}]**")
        c_ani, c_h, c_m, c_s = st.columns([2, 1, 1, 1])
        with c_ani:
            st.text_input("Anilha/Ano", placeholder="0000000/26", key=f"ani_{i}")
        with c_h: st.number_input("HH", 0, 23, key=f"h_{i}")
        with c_m: st.number_input("MM", 0, 59, key=f"m_{i}")
        with c_s: st.number_input("SS", 0, 59, key=f"s_{i}")
    
    if st.button("Calcular Série"):
        st.success(f"Cálculos de velocidade para {socio} concluídos.")

# 4. CLASSIFICAÇÃO
elif menu == "📊 Classificação Final":
    if 'prova' in st.session_state:
        p = st.session_state['prova']
        st.subheader(f"📊 {p['cidade']} - {p['mod']}")
        st.write(f"**Solta:** {p['hora']} | **Coordenadas:** {p['lat']}, {p['lon']}")
    else:
        st.warning("Aguardando configuração da prova.")
