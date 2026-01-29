import streamlit as st
import pandas as pd
from math import radians, cos, sin, asin, sqrt

# --- CONFIGURAÇÃO E MOTOR DE CÁLCULO ---
st.set_page_config(page_title="SGC - Sistema de Gestão Columbófila", layout="wide")

def haversine(lat1, lon1, lat2, lon2):
    try:
        lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
        dlon, dlat = lon2 - lon1, lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        return (2 * asin(sqrt(a))) * 6371 * 1000 # Metros
    except: return 0.0

# --- ESTADO DO SISTEMA (PARA NÃO PERDER DADOS) ---
if 'db_socios' not in st.session_state: st.session_state['db_socios'] = pd.DataFrame(columns=["Nome", "Lat", "Lon"])
if 'db_pombos' not in st.session_state: st.session_state['db_pombos'] = pd.DataFrame(columns=["Anilha", "Dono"])

st.title("🕊️ SGC - Sistema de Gestão Columbófila")

# --- MENU LATERAL COMPLETO ---
menu = st.sidebar.radio("Navegação", [
    "⚙️ Configurar Prova", 
    "👤 Cadastro de Sócios", 
    "🐦 Cadastro de Pombos", 
    "🚀 Lançar Chegadas (3+3)", 
    "📊 Apuramento & Geral"
])

modalidades = ["Filhotes", "Velocidade Adultos", "Meio Fundo Adultos", "Fundo Adultos", "Grande Fundo Adultos"]

# --- 1. CADASTRO DE SÓCIOS ---
if menu == "👤 Cadastro de Sócios":
    st.header("👤 Cadastro de Pombais")
    with st.form("cad_socio"):
        n = st.text_input("Nome do Sócio")
        la = st.text_input("Latitude (GPS)")
        lo = st.text_input("Longitude (GPS)")
        if st.form_submit_button("Salvar Sócio"):
            novo = pd.DataFrame([{"Nome": n, "Lat": la, "Lon": lo}])
            st.session_state['db_socios'] = pd.concat([st.session_state['db_socios'], novo], ignore_index=True)
            st.success(f"Sócio {n} cadastrado!")

# --- 2. CADASTRO DE POMBOS (AQUI CADASTRA OS POMBOS!) ---
elif menu == "🐦 Cadastro de Pombos":
    st.header("🐦 Registo de Anilhas")
    with st.form("cad_pombo"):
        ani = st.text_input("Anilha (Ex: 2004466/26)")
        dono = st.selectbox("Dono do Pombo", st.session_state['db_socios']['Nome'].tolist() if not st.session_state['db_socios'].empty else ["Cadastre um sócio primeiro"])
        if st.form_submit_button("Vincular Pombo"):
            novo_p = pd.DataFrame([{"Anilha": ani, "Dono": dono}])
            st.session_state['db_pombos'] = pd.concat([st.session_state['db_pombos'], novo_p], ignore_index=True)
            st.success(f"Pombo {ani} vinculado a {dono}!")
    st.write("### Pombos Registados")
    st.dataframe(st.session_state['db_pombos'])

# --- 3. CONFIGURAR PROVA ---
elif menu == "⚙️ Configurar Prova":
    st.header("⚙️ Configuração da Solta")
    col1, col2 = st.columns(2)
    with col1:
        m_sel = st.selectbox("Modalidade", modalidades)
        cid = st.text_input("Cidade")
        lat_s = st.text_input("Lat Solta")
        lon_s = st.text_input("Lon Solta")
    with col2:
        st.write("Hora Solta")
        c1, c2, c3 = st.columns(3)
        h_s, m_s, s_s = c1.number_input("H",0,23), c2.number_input("M",0,59), c3.number_input("S",0,59)
        p_in = st.number_input("Pontos 1º", value=100.0)
        dec = st.number_input("Decréscimo", value=1.0)
    if st.button("Gravar Prova"):
        st.session_state[f'p_{m_sel}'] = {"cid": cid, "lat": lat_s, "lon": lon_s, "h": h_s, "m": m_s, "s": s_s, "p": p_in, "d": dec}
        st.success(f"Prova de {m_sel} gravada!")

# --- 4. LANÇAR (REGRA 3+3) ---
elif menu == "🚀 Lançar Chegadas (3+3)":
    mod_at = st.selectbox("Lançar para:", modalidades)
    if f'p_{mod_at}' in st.session_state:
        st.header(f"🚀 Lançamento: {mod_at}")
        s_sel = st.selectbox("Sócio", st.session_state['db_socios']['Nome'].tolist())
        # Aqui o sistema busca a coordenada do sócio no banco de dados automaticamente
        dados_s = st.session_state['db_socios'][st.session_state['db_socios']['Nome'] == s_sel].iloc[0]
        
        for i in range(1, 7):
            tipo = "PONTUA" if i <= 3 else "EMPURRA"
            st.markdown(f"**Pombo {i} ({tipo})**")
            c_a, c_h, c_m, c_s = st.columns([2, 1, 1, 1])
            with c_a: st.selectbox("Anilha", st.session_state['db_pombos'][st.session_state['db_pombos']['Dono'] == s_sel]['Anilha'].tolist(), key=f"a_{i}")
            # ... campos de tempo
    else: st.warning("Configure a prova primeiro!")

# --- 5. APURAMENTO GERAL ---
elif menu == "📊 Apuramento & Geral":
    st.header("🏆 Classificações Gerais e por Modalidade")
    st.info("Aqui a calculadora financeira junta as 'gavetas' e apura o Campeão Geral de Concorrentes e de Pombos.")
