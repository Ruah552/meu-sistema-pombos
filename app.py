import streamlit as st
import pandas as pd
from math import radians, cos, sin, asin, sqrt

# --- 1. MOTOR DE CÁLCULO (PRECISÃO TOTAL) ---
def haversine(lat1, lon1, lat2, lon2):
    try:
        # Conversão para radianos
        lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
        dlon, dlat = lon2 - lon1, lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        return c * 6371 * 1000  # Distância em Metros
    except: return 0.0

def calcular_vel(dist_m, hs, ms, ss, hc, mc, sc):
    try:
        t_solta = hs * 3600 + ms * 60 + ss
        t_chegada = hc * 3600 + mc * 60 + sc
        tempo_voo_min = (t_chegada - t_solta) / 60
        return round(dist_m / tempo_voo_min, 3) if tempo_voo_min > 0 else 0.0
    except: return 0.0

# --- 2. INTERFACE E MENU ---
st.set_page_config(page_title="SGC Oficial", layout="wide")
st.sidebar.title("🕊️ SGC - Gestão Columbófila")

modalidades = ["Filhotes", "Velocidade Adultos", "Meio Fundo Adultos", "Fundo Adultos", "Grande Fundo Adultos"]
menu = st.sidebar.radio("Navegação", ["⚙️ Configurar Prova", "🚀 Lançar Chegadas (3+3)", "📊 Classificação & Geral"])

# --- 3. CONFIGURAÇÃO (PARAMETRIZAÇÃO) ---
if menu == "⚙️ Configurar Prova":
    st.header("⚙️ Parametrização da Solta")
    col1, col2 = st.columns(2)
    with col1:
        mod = st.selectbox("Modalidade", modalidades)
        cidade = st.text_input("Cidade da Solta", "Ex: Portalegre")
        lat_s = st.text_input("Latitude Solta (GPS)", "39.2921")
        lon_s = st.text_input("Longitude Solta (GPS)", "-7.4289")
    with col2:
        st.write("**Hora da Solta**")
        c1, c2, c3 = st.columns(3)
        h_solta = c1.number_input("H", 0, 23, 7)
        m_solta = c2.number_input("M", 0, 59, 0)
        s_solta = c3.number_input("S", 0, 59, 0)
        p_ini = st.number_input("Pontuação Inicial", value=100.0)
        dec = st.number_input("Decréscimo", value=1.0, step=0.1)

    if st.button("💾 Gravar Prova"):
        st.session_state[f'config_{mod}'] = {
            "cidade": cidade, "lat": lat_s, "lon": lon_s,
            "h": h_solta, "m": m_solta, "s": s_solta, "p_ini": p_ini, "dec": dec
        }
        st.success(f"Prova de {mod} em {cidade} configurada!")

# --- 4. LANÇAMENTO (REGRA 3+3) ---
elif menu == "🚀 Lançar Chegadas (3+3)":
    mod_l = st.selectbox("Lançar para:", modalidades)
    if f'config_{mod_l}' not in st.session_state:
        st.error("⚠️ Configure a prova primeiro!")
    else:
        conf = st.session_state[f'config_{mod_l}']
        st.header(f"🚀 Lançamento: {mod_l} - {conf['cidade']}")
        
        with st.expander("Dados do Sócio", expanded=True):
            c_soc, c_lat, c_lon = st.columns(3)
            socio = c_soc.text_input("Nome do Sócio")
            lat_p = c_lat.text_input("Lat. Pombal")
            lon_p = c_lon.text_input("Lon. Pombal")
            dist = haversine(conf['lat'], conf['lon'], lat_p, lon_p)
            st.metric("Distância Real", f"{dist/1000:.3f} Km")

        # Entrada para 6 pombos
        for i in range(1, 7):
            tipo = "PONTUA" if i <= 3 else "EMPURRA"
            cor = "blue" if i <= 3 else "orange"
            st.markdown(f"---")
            st.markdown(f"**Pombo {i} - :{cor}[{tipo}]**")
            ca, ch, cm, cs = st.columns([2, 1, 1, 1])
            with ca: ani = st.text_input("Anilha (milhão/ano)", key=f"ani_{i}_{mod_l}")
            with ch: h_c = ch.number_input("HH", 0, 23, key=f"hc_{i}_{mod_l}")
            with cm: m_c = cm.number_input("MM", 0, 59, key=f"mc_{i}_{mod_l}")
            with cs: s_c = cs.number_input("SS", 0, 59, key=f"sc_{i}_{mod_l}")

# --- 5. APURAMENTO (VERTICAL E HORIZONTAL) ---
elif menu == "📊 Classificação & Geral":
    st.header("📊 Apuramentos Oficiais")
    tipo_apuramento = st.selectbox("Ver Ranking:", ["GERAL ABSOLUTO"] + modalidades)
    
    tab1, tab2 = st.tabs(["🏆 Concorrentes (Sócios)", "🕊️ Pombo Ás (Individual)"])
    
    with tab1:
        st.subheader(f"Ranking de Sócios: {tipo_apuramento}")
        st.info("Soma dos pontos dos 3 designados (PONTUA) de todas as provas.")
        # Simulação de tabela consolidada
        st.table(pd.DataFrame({"Lugar": [1], "Sócio": ["Aguardando Dados"], "Pontos": [0.0]}))

    with tab2:
        st.subheader(f"Ranking Individual: {tipo_apuramento}")
        st.info("Soma da pontuação por anilha em todas as 'gavetas' (modalidades).")
        # Simulação de tabela de pombos
        st.table(pd.DataFrame({"Lugar": [1], "Anilha": ["Aguardando Dados"], "Pontos": [0.0]}))
