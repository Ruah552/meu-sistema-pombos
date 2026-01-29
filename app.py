import streamlit as st
import pandas as pd
from math import radians, cos, sin, asin, sqrt

# --- 1. MOTOR MATEMÁTICO (PRECISÃO GPS) ---
def haversine(lat1, lon1, lat2, lon2):
    try:
        lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
        a = sin((lat2-lat1)/2)**2 + cos(lat1) * cos(lat2) * sin((lon2-lon1)/2)**2
        return (2 * asin(sqrt(a))) * 6371 * 1000 
    except: return 0.0

# --- 2. MEMÓRIA DAS 10 PROVAS (SESSÃO) ---
if 'db_socios' not in st.session_state: st.session_state['db_socios'] = pd.DataFrame(columns=["Nome", "Lat", "Lon"])
if 'db_pombos' not in st.session_state: st.session_state['db_pombos'] = pd.DataFrame(columns=["Anilha", "Dono"])
if 'historico' not in st.session_state: 
    st.session_state['historico'] = pd.DataFrame(columns=["Prova", "Modalidade", "Sócio", "Anilha", "Velocidade", "Pontos", "Tipo"])

st.set_page_config(page_title="SGC - Sistema de Gestão Columbófila", layout="wide")
st.title("🕊️ SGC - Sistema de Gestão Columbófila")

# --- 3. MENU ---
menu = st.sidebar.radio("Navegação", [
    "⚙️ Configurar Prova", 
    "👤 Cadastro de Sócios/Pombos", 
    "🚀 Lançar Chegadas (3+3)", 
    "✏️ Corrigir/Editar Provas", 
    "📊 Apuramento (Modalidade e Geral)",
    "📑 Exportar Documentos"
])

mods = ["Filhotes", "Velocidade Adultos", "Meio Fundo Adultos", "Fundo Adultos", "Grande Fundo Adultos"]

# --- 4. LANÇAMENTO E GRAVAÇÃO ---
if menu == "🚀 Lançar Chegadas (3+3)":
    st.header("🚀 Lançamento de Provas")
    m_at = st.selectbox("Selecione a Modalidade", mods)
    n_p = st.number_input("Número da Prova (1 a 10)", 1, 10)
    
    # [Lógica de Lançamento 3+3 que discutimos]
    # Ao clicar em "Gravar", os dados entram no st.session_state['historico']

# --- 5. APURAMENTO (DUPLO: MODALIDADE E GERAL) ---
elif menu == "📊 Apuramento (Modalidade e Geral)":
    st.header("🏆 Classificações do Campeonato")
    
    # SELETOR DE GAVETAS (POR MODALIDADE OU TUDO)
    selecao = st.selectbox("Filtrar por:", ["GERAL ABSOLUTO (Soma de Tudo)"] + mods)
    
    aba_soc, aba_pom = st.tabs(["👥 CAMPEONATO DE SÓCIOS", "🕊️ CAMPEONATO POMBO ÁS"])
    
    df = st.session_state['historico']
    
    if not df.empty:
        # Se não for Geral, filtra a gaveta da modalidade
        if selecao != "GERAL ABSOLUTO (Soma de Tudo)":
            df_view = df[df['Modalidade'] == selecao]
        else:
            df_view = df

        with aba_soc:
            st.subheader(f"Ranking Sócios - {selecao}")
            # CALCULADORA: Soma apenas os pombos 'PONTUA'
            res_soc = df_view[df_view['Tipo'] == 'PONTUA'].groupby('Sócio')['Pontos'].sum().sort_values(ascending=False).reset_index()
            st.table(res_soc)

        with aba_pom:
            st.subheader(f"Ranking Pombos - {selecao}")
            # CALCULADORA: Soma a anilha individual em todas as provas da seleção
            res_pom = df_view.groupby(['Anilha', 'Sócio'])['Pontos'].sum().sort_values(ascending=False).reset_index()
            st.table(res_pom)
    else:
        st.warning("Sem dados no histórico.")

# --- 6. EXPORTAÇÃO (PDF E EXCEL) ---
elif menu == "📑 Exportar Documentos":
    st.header("📑 Exportação Oficial")
    st.write("Gere o ficheiro para impressão das 10 provas e dos rankings gerais.")
    
    if not st.session_state['historico'].empty:
        # EXCEL
        csv = st.session_state['historico'].to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Geral em Excel", csv, "geral_campeonato.csv", "text/csv")
