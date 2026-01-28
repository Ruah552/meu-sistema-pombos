import streamlit as st
import pandas as pd
from math import radians, cos, sin, asin, sqrt
from datetime import datetime

# --- CONFIGURAÇÕES E CÁLCULOS ---
st.set_page_config(page_title="SGC - Sistema Columbófilo Profissional", layout="wide")

def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371.0088  # Raio da Terra em km
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon, dlat = lon2 - lon1, lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * R

# --- BANCO DE DADOS EM MEMÓRIA ---
if "socios" not in st.session_state: st.session_state.socios = []
if "pombos" not in st.session_state: st.session_state.pombos = []
if "provas" not in st.session_state: st.session_state.provas = []

# --- TELA DE LOGIN ---
if "logado" not in st.session_state: st.session_state.logado = False

if not st.session_state.logado:
    st.title("🕊️ SGC - Acesso Restrito")
    senha = st.text_input("Introduza a Senha do Clube:", type="password")
    if st.button("ENTRAR"):
        if senha == "1234":
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Senha incorreta!")
else:
    # --- SISTEMA APÓS LOGIN ---
    st.sidebar.title("MENU PRINCIPAL")
    menu = st.sidebar.radio("Escolha uma opção:", ["Início", "👤 Sócios", "🕊️ Plantel de Pombos", "🚀 Lançar Concurso", "📊 Ranking Final"])

    if menu == "Início":
        st.title("🕊️ SGC - Gestão Columbófila")
        st.write(f"Bem-vindo! O sistema está pronto para operar.")
        col1, col2, col3 = st.columns(3)
        col1.metric("Sócios", len(st.session_state.socios))
        col2.metric("Pombos", len(st.session_state.pombos))
        col3.metric("Chegadas", len(st.session_state.provas))

    elif menu == "👤 Sócios":
        st.header("Cadastro de Sócios e Coordenadas")
        with st.form("add_socio"):
            nome = st.text_input("Nome do Columbófilo")
            c1, c2 = st.columns(2)
            lat = c1.number_input("Latitude do Pombal (Ex: 39.123)", format="%.6f")
            lon = c2.number_input("Longitude do Pombal (Ex: -8.123)", format="%.6f")
            if st.form_submit_button("Guardar Sócio"):
                st.session_state.socios.append({"Nome": nome, "Lat": lat, "Lon": lon})
                st.success("Sócio cadastrado com sucesso!")
        st.table(pd.DataFrame(st.session_state.socios))

    elif menu == "🕊️ Plantel de Pombos":
        st.header("Recenseamento de Pombos")
        if not st.session_state.socios:
            st.warning("Cadastre os sócios primeiro!")
        else:
            with st.form("add_pombo"):
                dono = st.selectbox("Dono", [s["Nome"] for s in st.session_state.socios])
                anilha = st.text_input("Nº da Anilha")
                cor = st.text_input("Cor/Variedade")
                if st.form_submit_button("Registar Pombo"):
                    st.session_state.pombos.append({"Dono": dono, "Anilha": anilha, "Cor": cor})
                    st.success(f"Pombo {anilha} registado!")
            st.table(pd.DataFrame(st.session_state.pombos))

    elif menu == "🚀 Lançar Concurso":
        st.header("Apuração de Resultados")
        st.info("Configuração da Soltura")
        c1, c2, c3 = st.columns(3)
        lat_s = c1.number_input("Lat. Soltura", format="%.6f")
        lon_s = c2.number_input("Lon. Soltura", format="%.6f")
        h_s = c3.time_input("Hora da Soltura", value=datetime.strptime("07:00", "%H:%M").time())

        st.divider()
        if not st.session_state.pombos:
            st.warning("Precisa de ter pombos cadastrados para lançar chegadas.")
        else:
            with st.form("batida"):
                pombo_sel = st.selectbox("Selecione o Pombo", [f"{p['Anilha']} ({p['Dono']})" for p in st.session_state.pombos])
                h_c = st.time_input("Hora de Chegada")
                if st.form_submit_button("REGISTAR BATIDA"):
                    anilha = pombo_sel.split(" (")[0]
                    dono = pombo_sel.split(" (")[1][:-1]
                    socio = next(s for s in st.session_state.socios if s["Nome"] == dono)
                    
                    dist = calcular_distancia(lat_s, lon_s, socio["Lat"], socio["Lon"])
                    # Cálculo de tempo
                    t1 = datetime.combine(datetime.today(), h_s)
                    t2 = datetime.combine(datetime.today(), h_c)
                    minutos = (t2 - t1).total_seconds() / 60
                    
                    if minutos > 0:
                        vel = (dist * 1000) / minutos
                        st.session_state.provas.append({
                            "Pos": 0, "Anilha": anilha, "Sócio": dono,
                            "Distância (m)": round(dist*1000, 2),
                            "Tempo (min)": round(minutos, 2),
                            "Velocidade (m/m)": round(vel, 3)
                        })
                        st.success("Resultado computado!")

    elif menu == "📊 Ranking Final":
        st.header("Classificação da Prova")
        if st.session_state.provas:
            df = pd.DataFrame(st.session_state.provas).sort_values("Velocidade (m/m)", ascending=False)
            df['Pos'] = range(1, len(df) + 1)
            st.dataframe(df, use_container_width=True)
            if st.button("Limpar Resultados"):
                st.session_state.provas = []
                st.rerun()
