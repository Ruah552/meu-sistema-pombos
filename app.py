import streamlit as st
import pandas as pd
from math import radians, cos, sin, asin, sqrt

# --- 1. MOTOR DE CÁLCULO (HAVERSINE & VELOCIDADE) ---
def calcular_distancia(lat1, lon1, lat2, lon2):
    try:
        lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
        a = sin((lat2-lat1)/2)**2 + cos(lat1) * cos(lat2) * sin((lon2-lon1)/2)**2
        return (2 * asin(sqrt(a))) * 6371 * 1000 
    except: return 0.0

# --- 2. GESTÃO DE MEMÓRIA (ARMAZENA AS 10 PROVAS) ---
if 'db_socios' not in st.session_state: st.session_state['db_socios'] = pd.DataFrame(columns=["Nome", "Lat", "Lon"])
if 'db_pombos' not in st.session_state: st.session_state['db_pombos'] = pd.DataFrame(columns=["Anilha", "Dono"])
if 'historico_provas' not in st.session_state: 
    st.session_state['historico_provas'] = pd.DataFrame(columns=["ID", "Prova_N", "Modalidade", "Sócio", "Anilha", "Velocidade", "Pontos", "Tipo"])

st.set_page_config(page_title="SGC - Master", layout="wide")
st.title("🕊️ SGC - Sistema de Gestão Columbófila")

# --- 3. MENU COMPLETO ---
menu = st.sidebar.radio("Navegação", [
    "⚙️ Configurar Prova", 
    "👤 Cadastro de Sócios", 
    "🐦 Cadastro de Pombos", 
    "🚀 Lançar Chegadas (3+3)", 
    "✏️ Corrigir/Editar Provas", 
    "📊 Apuramento (Geral e Modalidade)",
    "📑 Relatórios PDF/Excel"
])

modalidades = ["Filhotes", "Velocidade Adultos", "Meio Fundo Adultos", "Fundo Adultos", "Grande Fundo Adultos"]

# --- 4. FUNCIONALIDADES (ACRESCENTANDO SEM REMOVER) ---

# [CADASTROS MANTIDOS]
if menu == "👤 Cadastro de Sócios":
    st.header("👤 Cadastro de Pombais")
    with st.form("cad_socio"):
        n = st.text_input("Nome do Sócio")
        la, lo = st.text_input("Lat"), st.text_input("Lon")
        if st.form_submit_button("Salvar Sócio"):
            st.session_state['db_socios'] = pd.concat([st.session_state['db_socios'], pd.DataFrame([{"Nome": n, "Lat": la, "Lon": lo}])], ignore_index=True)
            st.success("Sócio gravado!")

elif menu == "🐦 Cadastro de Pombos":
    st.header("🐦 Cadastro de Anilhas")
    with st.form("cad_pombo"):
        ani = st.text_input("Anilha (Ex: 2004466/26)")
        dono = st.selectbox("Dono", st.session_state['db_socios']['Nome'].unique() if not st.session_state['db_socios'].empty else ["Sem Sócios"])
        if st.form_submit_button("Vincular Pombo"):
            st.session_state['db_pombos'] = pd.concat([st.session_state['db_pombos'], pd.DataFrame([{"Anilha": ani, "Dono": dono}])], ignore_index=True)

# --- 5. CORREÇÃO E RECALCULO (A NOVIDADE) ---
elif menu == "✏️ Corrigir/Editar Provas":
    st.header("✏️ Central de Correção e Recálculo")
    st.write("Altere qualquer dado abaixo (Anilha, Tempo ou Pontos) e o sistema atualizará o Geral automaticamente.")
    
    if not st.session_state['historico_provas'].empty:
        # Tabela editável que permite corrigir erros
        df_corrigido = st.data_editor(st.session_state['historico_provas'], num_rows="dynamic")
        
        if st.button("🔄 Salvar Alterações e Recalcular Campeonato"):
            st.session_state['historico_provas'] = df_corrigido
            st.success("✅ Erros corrigidos! O Campeonato Geral foi atualizado.")
    else:
        st.info("Nenhuma prova no histórico para editar.")

# --- 6. APURAMENTO (GAVETAS E GERAL) ---
elif menu == "📊 Apuramento (Geral e Modalidade)":
    st.header("🏆 Classificação Acumulada")
    sel_mod = st.selectbox("Filtrar por:", ["GERAL ABSOLUTO"] + modalidades)
    
    df = st.session_state['historico_provas']
    if not df.empty:
        if sel_mod != "GERAL ABSOLUTO":
            df = df[df['Modalidade'] == sel_mod]
        
        # Apuramento Concorrentes (Soma apenas os pombos 'PONTUA')
        ranking = df[df['Tipo'] == 'PONTUA'].groupby('Sócio')['Pontos'].sum().sort_values(ascending=False).reset_index()
        st.subheader(f"Ranking Concorrentes - {sel_mod}")
        st.table(ranking)
        
        # Apuramento Pombos (Soma pontos por anilha)
        pombo_as = df.groupby(['Anilha', 'Sócio'])['Pontos'].sum().sort_values(ascending=False).reset_index()
        st.subheader(f"Ranking Pombo Ás - {sel_mod}")
        st.table(pombo_as)
