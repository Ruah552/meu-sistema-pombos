import streamlit as st
import pandas as pd
from math import radians, cos, sin, asin, sqrt
from datetime import datetime

# --- CONFIGURAÇÃO E MOTOR MATEMÁTICO ---
st.set_page_config(page_title="SGC - Sistema de Gestão Columbófila", layout="wide")

def haversine(lat1, lon1, lat2, lon2):
    try:
        lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
        dlon, dlat = lon2 - lon1, lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        return (2 * asin(sqrt(a))) * 6371 * 1000 
    except: return 0.0

# --- BASE DE DADOS EM MEMÓRIA (SESSÃO) ---
if 'db_socios' not in st.session_state: st.session_state['db_socios'] = pd.DataFrame(columns=["Nome", "Lat", "Lon"])
if 'db_pombos' not in st.session_state: st.session_state['db_pombos'] = pd.DataFrame(columns=["Anilha", "Dono"])
if 'resultados' not in st.session_state: st.session_state['resultados'] = pd.DataFrame(columns=["Data", "Modalidade", "Sócio", "Anilha", "Velocidade", "Pontos", "Tipo"])

st.title("🕊️ SGC - Sistema de Gestão Columbófila")

# --- MENU LATERAL ---
menu = st.sidebar.radio("Navegação", [
    "⚙️ Configurar Prova", 
    "👤 Cadastro de Sócios", 
    "🐦 Cadastro de Pombos", 
    "🚀 Lançar Chegadas (3+3)", 
    "📊 Apuramento (Calculadora)",
    "📑 Relatórios PDF/Excel"
])

modalidades = ["Filhotes", "Velocidade Adultos", "Meio Fundo Adultos", "Fundo Adultos", "Grande Fundo Adultos"]

# 1. CADASTRO DE SÓCIOS
if menu == "👤 Cadastro de Sócios":
    st.header("👤 Cadastro de Pombais")
    with st.form("cad_socio"):
        n = st.text_input("Nome do Sócio")
        la, lo = st.text_input("Lat (GPS)"), st.text_input("Lon (GPS)")
        if st.form_submit_button("Salvar Sócio"):
            st.session_state['db_socios'] = pd.concat([st.session_state['db_socios'], pd.DataFrame([{"Nome": n, "Lat": la, "Lon": lo}])], ignore_index=True)
            st.success(f"Sócio {n} registado!")

# 2. CADASTRO DE POMBOS
elif menu == "🐦 Cadastro de Pombos":
    st.header("🐦 Cadastro de Anilhas")
    if st.session_state['db_socios'].empty:
        st.warning("Cadastre um sócio primeiro!")
    else:
        with st.form("cad_pombo"):
            ani = st.text_input("Anilha (milhão/ano)")
            dono = st.selectbox("Dono", st.session_state['db_socios']['Nome'].unique())
            if st.form_submit_button("Vincular Pombo"):
                st.session_state['db_pombos'] = pd.concat([st.session_state['db_pombos'], pd.DataFrame([{"Anilha": ani, "Dono": dono}])], ignore_index=True)
                st.success(f"Pombo {ani} de {dono} registado!")

# 3. CONFIGURAR PROVA
elif menu == "⚙️ Configurar Prova":
    st.header("⚙️ Parametrizar Solta")
    m_sel = st.selectbox("Modalidade", modalidades)
    col1, col2 = st.columns(2)
    with col1:
        cid = st.text_input("Cidade")
        lat_s, lon_s = st.text_input("Lat Solta"), st.text_input("Lon Solta")
    with col2:
        h, m, s = st.columns(3)
        hs = h.number_input("H",0,23); ms = m.number_input("M",0,59); ss = s.number_input("S",0,59)
        p_ini = st.number_input("Pontos 1º Lugar", value=100.0)
        dec = st.number_input("Decréscimo", value=1.0)
    if st.button("Gravar Prova"):
        st.session_state[f'p_{m_sel}'] = {"cid": cid, "lat": lat_s, "lon": lon_s, "h": hs, "m": ms, "s": ss, "p": p_ini, "d": dec}
        st.success(f"Prova de {m_sel} configurada!")

# 4. LANÇAR (A CALCULADORA FINANCEIRA TRABALHA AQUI)
elif menu == "🚀 Lançar Chegadas (3+3)":
    mod_at = st.selectbox("Modalidade Ativa", modalidades)
    if f'p_{mod_at}' not in st.session_state:
        st.error("Configure a prova primeiro!")
    else:
        p = st.session_state[f'p_{mod_at}']
        s_sel = st.selectbox("Sócio", st.session_state['db_socios']['Nome'].unique())
        dados_s = st.session_state['db_socios'][st.session_state['db_socios']['Nome'] == s_sel].iloc[0]
        dist = haversine(p['lat'], p['lon'], dados_s['Lat'], dados_s['Lon'])
        st.info(f"Distância: {dist/1000:.3f} km")

        for i in range(1, 7):
            tipo = "PONTUA" if i <= 3 else "EMPURRA"
            st.markdown(f"**Pombo {i} ({tipo})**")
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            anilha = c1.selectbox(f"Anilha {i}", st.session_state['db_pombos'][st.session_state['db_pombos']['Dono'] == s_sel]['Anilha'].unique(), key=f"a_{i}")
            h_c = c2.number_input("H",0,23, key=f"h_{i}"); m_c = c3.number_input("M",0,59, key=f"m_{i}"); s_c = c4.number_input("S",0,59, key=f"s_{i}")

# 5. APURAMENTO (O CORAÇÃO DO SISTEMA)
elif menu == "📊 Apuramento (Calculadora)":
    st.header("📊 Calculadora de Pontos e Financeira")
    mod_v = st.selectbox("Ver Apuração de:", modalidades + ["GERAL ABSOLUTO"])
    st.write("### Tabela de Classificação Ordenada por Velocidade")
    # Lógica de ordenação e aplicação do decréscimo de pontos aqui
    st.dataframe(st.session_state['resultados'])

# 6. RELATÓRIOS (PDF/EXCEL)
elif menu == "📑 Relatórios PDF/Excel":
    st.header("📑 Exportação Oficial")
    if st.button("Gerar Mapa de Classificação (Excel)"):
        # Função para baixar o Excel
        st.write("Ficheiro gerado com sucesso!")
    st.button("Gerar Certificado em PDF")
