import streamlit as st
import pandas as pd
from math import radians, cos, sin, asin, sqrt

# --- MOTOR DE CÁLCULO (NÃO MEXER) ---
def haversine(lat1, lon1, lat2, lon2):
    try:
        lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
        a = sin((lat2-lat1)/2)**2 + cos(lat1) * cos(lat2) * sin((lon2-lon1)/2)**2
        return (2 * asin(sqrt(a))) * 6371 * 1000 # Metros
    except: return 0.0

# --- INICIALIZAÇÃO DA MEMÓRIA (ARMAZENA AS 10 PROVAS E CADASTROS) ---
if 'db_socios' not in st.session_state: st.session_state['db_socios'] = pd.DataFrame(columns=["Nome", "Lat", "Lon"])
if 'db_pombos' not in st.session_state: st.session_state['db_pombos'] = pd.DataFrame(columns=["Anilha", "Dono"])
if 'historico' not in st.session_state: 
    st.session_state['historico'] = pd.DataFrame(columns=["Prova", "Modalidade", "Sócio", "Anilha", "Velocidade", "Pontos", "Tipo"])

st.set_page_config(page_title="SGC - Sistema de Gestão Columbófila", layout="wide")
st.title("🕊️ SGC - Sistema de Gestão Columbófila Profissional")

# --- MENU LATERAL ---
menu = st.sidebar.radio("Navegação", [
    "⚙️ Configurar Prova", 
    "👤 Cadastro de Sócios", 
    "🐦 Cadastro de Pombos", 
    "🚀 Lançar Chegadas (3+3)", 
    "✏️ Corrigir/Editar Provas", 
    "📊 Apuramento (Modalidade e Geral)",
    "📑 Exportar Relatórios (PDF/Excel)"
])

modalidades = ["Filhotes", "Velocidade Adultos", "Meio Fundo Adultos", "Fundo Adultos", "Grande Fundo Adultos"]

# --- 1. CADASTRO DE SÓCIOS ---
if menu == "👤 Cadastro de Sócios":
    st.header("👤 Cadastro de Pombais")
    with st.form("cad_socio"):
        n = st.text_input("Nome do Sócio/Pombal")
        la = st.text_input("Latitude (GPS)")
        lo = st.text_input("Longitude (GPS)")
        if st.form_submit_button("Salvar Sócio"):
            novo = pd.DataFrame([{"Nome": n, "Lat": la, "Lon": lo}])
            st.session_state['db_socios'] = pd.concat([st.session_state['db_socios'], novo], ignore_index=True)
            st.success(f"Sócio {n} cadastrado!")

# --- 2. CADASTRO DE POMBOS ---
elif menu == "🐦 Cadastro de Pombos":
    st.header("🐦 Cadastro de Anilhas")
    if st.session_state['db_socios'].empty:
        st.warning("Cadastre um sócio primeiro!")
    else:
        with st.form("cad_pombo"):
            ani = st.text_input("Anilha (Ex: 2004466/26)")
            dono = st.selectbox("Vincular ao Sócio", st.session_state['db_socios']['Nome'].unique())
            if st.form_submit_button("Vincular Pombo"):
                novo_p = pd.DataFrame([{"Anilha": ani, "Dono": dono}])
                st.session_state['db_pombos'] = pd.concat([st.session_state['db_pombos'], novo_p], ignore_index=True)
                st.success(f"Pombo {ani} vinculado a {dono}!")

# --- 3. CONFIGURAR PROVA ---
elif menu == "⚙️ Configurar Prova":
    st.header("⚙️ Parametrização da Solta")
    m_sel = st.selectbox("Modalidade", modalidades)
    col1, col2 = st.columns(2)
    with col1:
        cid = st.text_input("Cidade")
        lat_s, lon_s = st.text_input("Lat Solta"), st.text_input("Lon Solta")
    with col2:
        st.write("Hora Solta")
        h, m, s = st.columns(3)
        hs, ms, ss = h.number_input("H",0,23), m.number_input("M",0,59), s.number_input("S",0,59)
        p_ini = st.number_input("Pontos 1º", value=100.0)
        dec = st.number_input("Decréscimo", value=1.0)
    if st.button("Gravar Prova"):
        st.session_state[f'conf_{m_sel}'] = {"cid": cid, "lat": lat_s, "lon": lon_s, "h": hs, "m": ms, "s": ss, "p": p_ini, "d": dec}
        st.success(f"Prova de {m_sel} em {cid} pronta!")

# --- 4. LANÇAR (REGRA 3+3) ---
elif menu == "🚀 Lançar Chegadas (3+3)":
    mod_at = st.selectbox("Modalidade", modalidades)
    if f'conf_{mod_at}' not in st.session_state:
        st.error("Configure a prova primeiro!")
    else:
        p = st.session_state[f'conf_{mod_at}']
        s_sel = st.selectbox("Sócio", st.session_state['db_socios']['Nome'].unique())
        dados_s = st.session_state['db_socios'][st.session_state['db_socios']['Nome'] == s_sel].iloc[0]
        dist = haversine(p['lat'], p['lon'], dados_s['Lat'], dados_s['Lon'])
        st.info(f"Distância Oficial: {dist/1000:.3f} km")

        for i in range(1, 7):
            tipo = "PONTUA" if i <= 3 else "EMPURRA"
            st.markdown(f"**Pombo {i} ({tipo})**")
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            anilha = c1.selectbox(f"Anilha {i}", st.session_state['db_pombos'][st.session_state['db_pombos']['Dono'] == s_sel]['Anilha'].unique(), key=f"a_{i}")
            h_c, m_c, s_c = c2.number_input("H",0,23,key=f"h{i}"), c3.number_input("M",0,59,key=f"m{i}"), c4.number_input("S",0,59,key=f"s{i}")

# --- 5. CORREÇÃO E RECALCULO ---
elif menu == "✏️ Corrigir/Editar Provas":
    st.header("✏️ Central de Correção")
    if not st.session_state['historico'].empty:
        df_edit = st.data_editor(st.session_state['historico'], num_rows="dynamic")
        if st.button("🔄 Recalcular Geral"):
            st.session_state['historico'] = df_edit
            st.success("Tudo recalculado!")

# --- 6. APURAMENTO (SOMA DE POMBOS E CONCORRENTES POR MODALIDADE E GERAL) ---
elif menu == "📊 Apuramento (Modalidade e Geral)":
    st.header("🏆 Classificações do Campeonato")
    opcao = st.selectbox("Ver Ranking:", ["GERAL ABSOLUTO"] + modalidades)
    tab1, tab2 = st.tabs(["👥 CONCORRENTES (SOMA PONTOS)", "🕊️ POMBO ÁS (INDIVIDUAL)"])
    
    df = st.session_state['historico']
    if not df.empty:
        if opcao != "GERAL ABSOLUTO": df = df[df['Modalidade'] == opcao]
        
        with tab1:
            st.subheader(f"Geral de Concorrentes - {opcao}")
            rank_s = df[df['Tipo'] == 'PONTUA'].groupby('Sócio')['Pontos'].sum().sort_values(ascending=False).reset_index()
            st.table(rank_s)
            
        with tab2:
            st.subheader(f"Geral de Pombos (Soma de Pontos) - {opcao}")
            rank_p = df.groupby(['Anilha', 'Sócio'])['Pontos'].sum().sort_values(ascending=False).reset_index()
            st.table(rank_p)

# --- 7. EXPORTAR PDF/EXCEL ---
elif menu == "📑 Exportar Relatórios (PDF/Excel)":
    st.header("📑 Documentos Oficiais")
    if not st.session_state['historico'].empty:
        csv = st.session_state['historico'].to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Excel do Campeonato", csv, "geral.csv", "text/csv")
