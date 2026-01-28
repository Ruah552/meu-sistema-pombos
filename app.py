import streamlit as st
import pandas as pd
from math import radians, cos, sin, asin, sqrt
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="SGC - Sistema de Gestão Columbófila", layout="wide")

# Função para calcular distância entre coordenadas (Haversine)
def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371.0088 # Raio da Terra em km
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon, dlat = lon2 - lon1, lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * R

# Título e Login
st.title("🕊️ SGC - Sistema de Gestão Columbófila")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    senha = st.text_input("Senha de Acesso:", type="password")
    if st.button("ENTRAR NO SISTEMA"):
        if senha == "1234":
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Acesso Negado.")
else:
    # Memória temporária para os dados
    if "socios" not in st.session_state: st.session_state.socios = []
    if "pombos" not in st.session_state: st.session_state.pombos = []
    if "chegadas" not in st.session_state: st.session_state.chegadas = []

    menu = st.sidebar.radio("Navegação:", ["Início", "Sócios", "Pombos", "Concursos/Chegadas", "Resultados"])

    if menu == "Início":
        st.subheader("Bem-vindo ao SGC!")
        st.write("Use o menu lateral para gerir o seu clube.")
        st.metric("Sócios Inscritos", len(st.session_state.socios))
        st.metric("Pombos Recenseados", len(st.session_state.pombos))

    elif menu == "Sócios":
        st.header("👥 Cadastro de Sócios")
        with st.form("add_socio"):
            nome = st.text_input("Nome do Sócio")
            col1, col2 = st.columns(2)
            lat = col1.number_input("Latitude (ex: 39.123)", format="%.6f")
            lon = col2.number_input("Longitude (ex: -8.123)", format="%.6f")
            if st.form_submit_button("Gravar Sócio"):
                st.session_state.socios.append({"Nome": nome, "Lat": lat, "Lon": lon})
                st.success("Sócio guardado!")
        st.table(pd.DataFrame(st.session_state.socios))

    elif menu == "Pombos":
        st.header("🕊️ Recenseamento")
        if not st.session_state.socios:
            st.warning("Cadastre um sócio primeiro!")
        else:
            with st.form("add_pombo"):
                dono = st.selectbox("Dono", [s["Nome"] for s in st.session_state.socios])
                anilha = st.text_input("Nº da Anilha")
                if st.form_submit_button("Recensear Pombo"):
                    st.session_state.pombos.append({"Dono": dono, "Anilha": anilha})
            st.table(pd.DataFrame(st.session_state.pombos))

    elif menu == "Concursos/Chegadas":
        st.header("⏱️ Lançamento de Chegadas")
        # Dados da Soltura
        st.info("Dados da Soltura")
        lat_s = st.number_input("Lat Soltura", format="%.6f", key="ls")
        lon_s = st.number_input("Lon Soltura", format="%.6f", key="los")
        h_s = st.time_input("Hora da Soltura")
        
        st.divider()
        
        if st.session_state.pombos:
            with st.form("chegada"):
                p = st.selectbox("Pombo", [f"{p['Anilha']} ({p['Dono']})" for p in st.session_state.pombos])
                h_c = st.time_input("Hora de Chegada")
                if st.form_submit_button("Registar Batida"):
                    # Cálculos
                    anilha_sel = p.split(" (")[0]
                    dono_sel = p.split(" (")[1].replace(")", "")
                    socio = next(s for s in st.session_state.socios if s["Nome"] == dono_sel)
                    
                    dist = calcular_distancia(lat_s, lon_s, socio["Lat"], socio["Lon"])
                    
                    # Tempo em minutos
                    t1 = datetime.combine(datetime.today(), h_s)
                    t2 = datetime.combine(datetime.today(), h_c)
                    minutos = (t2 - t1).total_seconds() / 60
                    
                    velocidade = (dist * 1000) / minutos if minutos > 0 else 0
                    
                    st.session_state.chegadas.append({
                        "Anilha": anilha_sel, "Sócio": dono_sel, 
                        "Distância (m)": round(dist*1000, 2), 
                        "Velocidade (m/m)": round(velocidade, 3)
                    })
                    st.success("Chegada registada!")

    elif menu == "Resultados":
        st.header("📊 Classificação Final")
        if st.session_state.chegadas:
            df = pd.DataFrame(st.session_state.chegadas).sort_values("Velocidade (m/m)", ascending=False)
            st.dataframe(df, use_container_width=True)
        else:
            st.write("Nenhum resultado disponível.")
