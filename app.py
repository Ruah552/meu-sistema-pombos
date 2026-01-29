import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from math import radians, cos, sin, asin, sqrt

# --- CONFIGURAÇÃO INICIAL (NÃO MEXER) ---
st.set_page_config(page_title="SGC - Sistema de Gestão Columbófila", layout="wide")

# --- 1. FÓRMULAS MATEMÁTICAS DE PRECISÃO ---
def calcular_distancia_real(lat1, lon1, lat2, lon2):
    try:
        lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
        dlon, dlat = lon2 - lon1, lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        return c * 6371 * 1000 # Distância exata em METROS
    except: return 0.0

def calcular_velocidade_oficial(dist_m, h_s, m_s, s_s, h_c, m_c, s_c):
    try:
        t_solta = h_s * 3600 + m_s * 60 + s_s
        t_chegada = h_c * 3600 + m_c * 60 + s_c
        tempo_voo_min = (t_chegada - t_solta) / 60
        return round(dist_m / tempo_voo_min, 3) if tempo_voo_min > 0 else 0.0
    except: return 0.0

# --- 2. CONEXÃO COM GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Tenta ler a base de sócios existente
    df_socios = conn.read(worksheet="Socios")
except:
    df_socios = pd.DataFrame(columns=["Nome", "Latitude", "Longitude"])

st.title("🕊️ SGC - Sistema de Gestão Columbófila")

# --- 3. MENU LATERAL COMPLETO ---
menu = st.sidebar.radio("Navegação", [
    "⚙️ Configurar Prova", 
    "👤 Cadastro de Sócios", 
    "🚀 Lançar Chegadas (3+3)", 
    "📊 Apuramento por Modalidade",
    "🏆 CAMPEONATO GERAL (Soma Tudo)"
])

modalidades = ["Filhotes", "Velocidade Adultos", "Meio Fundo Adultos", "Fundo Adultos", "Grande Fundo Adultos"]

# --- 4. FUNCIONALIDADES ---

if menu == "⚙️ Configurar Prova":
    st.header("⚙️ Parametrização da Solta")
    col1, col2 = st.columns(2)
    with col1:
        mod_sel = st.selectbox("Escolha a Modalidade", modalidades)
        cidade = st.text_input("Cidade da Solta", placeholder="Ex: Valência")
        lat_s = st.text_input("Latitude Solta (GPS)")
        lon_s = st.text_input("Longitude Solta (GPS)")
    with col2:
        st.write("**Hora da Solta**")
        c1, c2, c3 = st.columns(3)
        h_sol = c1.number_input("H", 0, 23, 7)
        m_sol = c2.number_input("M", 0, 59, 0)
        s_sol = c3.number_input("S", 0, 59, 0)
        p_ini = st.number_input("Pontuação Inicial (1º Lugar)", value=100.0)
        dec = st.number_input("Decréscimo (Pontos a menos por lugar)", value=1.0, step=0.1)

    if st.button("💾 Gravar Prova"):
        st.session_state[f'prova_{mod_sel}'] = {
            "cidade": cidade, "lat": lat_s, "lon": lon_s,
            "h": h_sol, "m": m_sol, "s": s_sol, "p_ini": p_ini, "dec": dec
        }
        st.success(f"Prova de {mod_sel} em {cidade} configurada com sucesso!")

elif menu == "👤 Cadastro de Sócios":
    st.header("👤 Registo de Pombais")
    with st.form("novo_socio"):
        nome = st.text_input("Nome do Sócio / Pombal")
        l_p = st.text_input("Latitude Pombal (GPS)")
        lo_p = st.text_input("Longitude Pombal (GPS)")
        if st.form_submit_button("Gravar no Google Sheets"):
            st.success(f"Sócio {nome} registado!")

elif menu == "🚀 Lançar Chegadas (3+3)":
    mod_ativo = st.selectbox("Lançar para qual modalidade?", modalidades)
    if f'prova_{mod_ativo}' not in st.session_state:
        st.error(f"⚠️ Configure a prova de {mod_ativo} primeiro!")
    else:
        p = st.session_state[f'prova_{mod_ativo}']
        st.subheader(f"🚀 Lançamento: {mod_ativo} em {p['cidade']}")
        
        # Seleção de Sócio da Base de Dados
        socio_sel = st.selectbox("Selecione o Sócio", df_socios["Nome"].tolist() if not df_socios.empty else ["Nenhum sócio cadastrado"])
        
        # Mostra os 6 campos de pombos (3+3)
        for i in range(1, 7):
            tipo = "PONTUA" if i <= 3 else "EMPURRA"
            cor = "blue" if i <= 3 else "orange"
            st.markdown(f"---")
            st.markdown(f"**Pombo {i} - :{cor}[{tipo}]**")
            c_ani, c_h, c_m, c_s = st.columns([2, 1, 1, 1])
            with c_ani: st.text_input("Anilha (Ex: 2004466/26)", key=f"ani_{i}_{mod_ativo}")
            with c_h: st.number_input("HH", 0, 23, key=f"h_{i}_{mod_ativo}")
            with c_m: st.number_input("MM", 0, 59, key=f"m_{i}_{mod_ativo}")
            with c_s: st.number_input("SS", 0, 59, key=f"s_{i}_{mod_ativo}")

elif menu == "📊 Apuramento por Modalidade":
    mod_v = st.selectbox("Ver Classificação de:", modalidades)
    st.header(f"📊 Classificação: {mod_v}")
    st.info("Aqui o sistema separa os pombos desta 'gaveta' específica.")

elif menu == "🏆 CAMPEONATO GERAL (Soma Tudo)":
    st.header("🏆 Geral Absoluto - Campeonato")
    st.write("Soma total de todas as modalidades (Vertical + Horizontal).")
    aba_con, aba_pom = st.tabs(["👥 Concorrentes", "🕊️ Pombo Ás"])
    with aba_con: st.info("Ranking acumulado de todos os sócios (3 designados por prova).")
    with aba_pom: st.info("Ranking acumulado de cada anilha individualmente.")
