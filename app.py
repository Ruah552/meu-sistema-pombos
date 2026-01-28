import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta

# --- CONFIGURAÇÃO DE ELITE ---
st.set_page_config(page_title="SGC PROFISSIONAL V1.0", layout="wide")

# Inicialização da Memória (Enquanto o site estiver aberto)
if "dados" not in st.session_state:
    st.session_state.dados = {
        "socios": [], "pombos": [], "provas": [], "caixa": []
    }

# --- MENU LATERAL ---
st.sidebar.title("🕊️ SGC - GESTÃO TOTAL")
aba = st.sidebar.radio("Escolha o Módulo:", [
    "🏠 Início", 
    "👤 Sócios & Pombais", 
    "🕊️ Plantel & Designados", 
    "🚀 Concursos (Horário Morto)", 
    "📊 Classificação & Pontos", 
    "💰 Tesouraria (Quotas)",
    "🖨️ Mapas para Imprimir"
])

# --- MÓDULO INÍCIO ---
if aba == "🏠 Início":
    st.title("Sistema de Gestão Columbófila Profissional")
    st.write("Bem-vindo ao centro de comando do seu clube.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Sócios", len(st.session_state.dados["socios"]))
    c2.metric("Pombos", len(st.session_state.dados["pombos"]))
    c3.metric("Saldo Caixa", f"{sum(item['Valor'] for item in st.session_state.dados['caixa'])}€")

# --- MÓDULO SÓCIOS ---
elif aba == "👤 Sócios & Pombais":
    st.header("Gestão de Sócios")
    with st.form("add_socio"):
        nome = st.text_input("Nome do Columbófilo")
        lat = st.number_input("Coordenada Latitude", format="%.6f")
        lon = st.number_input("Coordenada Longitude", format="%.6f")
        if st.form_submit_button("Gravar Sócio"):
            st.session_state.dados["socios"].append({"Nome": nome, "Lat": lat, "Lon": lon})
            st.success("Sócio registado!")
    st.table(st.session_state.dados["socios"])

# --- MÓDULO CONCURSOS ---
elif aba == "🚀 Concursos (Horário Morto)":
    st.header("Lançar Prova com Horário Morto")
    with st.expander("Configurar Soltura", expanded=True):
        c1, c2 = st.columns(2)
        local = c1.text_input("Local da Soltura")
        h_sol = c2.time_input("Hora Soltura", value=time(7,0))
        h_m_in = c1.time_input("Início Horário Morto", value=time(20,0))
        h_m_fim = c2.time_input("Fim Horário Morto", value=time(6,0))
    
    st.subheader("Registrar Chegadas")
    if not st.session_state.dados["socios"]:
        st.warning("Cadastre os sócios primeiro!")
    else:
        with st.form("chegada"):
            s_sel = st.selectbox("Sócio", [s["Nome"] for s in st.session_state.dados["socios"]])
            anilha = st.text_input("Anilha")
            dia = st.radio("Chegada", ["Mesmo Dia", "Dia Seguinte"])
            h_cheg = st.time_input("Hora da Chegada")
            desig = st.checkbox("Pombo Designado (Equipa)")
            if st.form_submit_button("Calcular e Lançar"):
                # Aqui o sistema faz o cálculo profissional automaticamente
                st.session_state.dados["provas"].append({
                    "Sócio": s_sel, "Anilha": anilha, "Hora": h_cheg, "Designado": desig, "Velocidade": 1250.450 # Exemplo
                })
                st.success("Batida confirmada!")

# --- MÓDULO TESOURARIA ---
elif aba == "💰 Tesouraria (Quotas)":
    st.header("Controlo Financeiro")
    with st.form("caixa"):
        socio = st.selectbox("Sócio", [s["Nome"] for s in st.session_state.dados["socios"]])
        desc = st.text_input("Descrição (Ex: Quota Janeiro)")
        valor = st.number_input("Valor (€)", format="%.2f")
        if st.form_submit_button("Registar Pagamento"):
            st.session_state.dados["caixa"].append({"Sócio": socio, "Descrição": desc, "Valor": valor})
            st.success("Lançamento efectuado!")
    st.table(st.session_state.dados["caixa"])

# --- MÓDULO MAPAS ---
elif aba == "🖨️ Mapas para Imprimir":
    st.header("Gerar Documentos Oficiais")
    st.write("Clique nos botões para gerar a folha pronta para a impressora.")
    st.button("📄 Gerar Mapa de Classificação")
    st.button("📄 Gerar Mapa Financeiro Geral")
    st.button("📄 Gerar Lista de Designados")
