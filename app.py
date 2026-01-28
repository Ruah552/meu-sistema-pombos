import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
from math import radians, cos, sin, asin, sqrt

# --- FUNÇÕES TÉCNICAS ---
def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371.0088 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon, dlat = lon2 - lon1, lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * R

def calcular_tempo_real(h_soltura, h_chegada, dia_chegada, h_morto_in, h_morto_fim):
    t_soltura = datetime.combine(datetime.today(), h_soltura)
    t_chegada = datetime.combine(datetime.today(), h_chegada)
    
    if dia_chegada == "Mesmo Dia":
        return (t_chegada - t_soltura).total_seconds() / 60
    else:
        t_chegada_amanha = t_chegada + timedelta(days=1)
        tempo_bruto = (t_chegada_amanha - t_soltura).total_seconds() / 60
        t_morto_inicio = datetime.combine(datetime.today(), h_morto_in)
        t_morto_fim = datetime.combine(datetime.today() + timedelta(days=1), h_morto_fim)
        minutos_mortos = (t_morto_fim - t_morto_inicio).total_seconds() / 60
        return tempo_bruto - minutos_mortos

# --- ESTRUTURA DO SITE ---
st.set_page_config(page_title="SGC PROFISSIONAL", layout="wide")

if "db_socios" not in st.session_state: st.session_state.db_socios = []
if "db_chegadas" not in st.session_state: st.session_state.db_chegadas = []

st.sidebar.title("🕊️ Menu SGC")
aba = st.sidebar.radio("Escolha o Módulo:", ["Painel de Controle", "Sócios & Pombais", "Concursos (Horário Morto)", "Ranking & Pontos", "Financeiro"])

if aba == "Painel de Controle":
    st.title("Sistema de Gestão Columbófila")
    st.info("Bem-vindo! Use o menu lateral para gerir o seu clube.")
    # Resumo rápido
    c1, c2 = st.columns(2)
    c1.metric("Sócios Ativos", len(st.session_state.db_socios))
    c2.metric("Última Prova", "Aguardando dados")

elif aba == "Sócios & Pombais":
    st.header("👤 Gestão de Sócios")
    with st.form("cad_socio"):
        nome = st.text_input("Nome do Sócio")
        c1, c2 = st.columns(2)
        lat = c1.number_input("Lat Pombal", format="%.6f")
        lon = c2.number_input("Lon Pombal", format="%.6f")
        if st.form_submit_button("Guardar Sócio"):
            st.session_state.db_socios.append({"Nome": nome, "Lat": lat, "Lon": lon})
            st.success("Sócio guardado!")
    st.write(pd.DataFrame(st.session_state.db_socios))

elif aba == "Concursos (Horário Morto)":
    st.header("🚀 Lançar Prova Profissional")
    with st.expander("Configurar Soltura e Horário Morto", expanded=True):
        c1, c2, c3 = st.columns(3)
        h_sol = c1.time_input("Hora Soltura", value=time(7,0))
        h_m_in = c2.time_input("Início Horário Morto", value=time(20,0))
        h_m_fim = c3.time_input("Fim Horário Morto", value=time(6,0))
        lat_sol = c1.number_input("Lat Soltura", format="%.6f")
        lon_sol = c2.number_input("Lon Soltura", format="%.6f")

    st.divider()
    if st.session_state.db_socios:
        with st.form("lancar_chegada"):
            s_sel = st.selectbox("Sócio", [s["Nome"] for s in st.session_state.db_socios])
            anilha = st.text_input("Anilha")
            dia = st.radio("Dia da Chegada", ["Mesmo Dia", "Dia Seguinte"])
            h_cheg = st.time_input("Hora da Chegada")
            if st.form_submit_button("Registar Batida"):
                socio_data = next(s for s in st.session_state.db_socios if s["Nome"] == s_sel)
                dist = calcular_distancia(lat_sol, lon_sol, socio_data["Lat"], socio_data["Lon"])
                tempo = calcular_tempo_real(h_sol, h_cheg, dia, h_m_in, h_m_fim)
                vel = (dist * 1000) / tempo if tempo > 0 else 0
                st.session_state.db_chegadas.append({
                    "Sócio": s_sel, "Anilha": anilha, "Velocidade": round(vel, 3), 
                    "Distância (m)": round(dist*1000, 2), "Tempo (min)": round(tempo, 2)
                })
                st.success("Chegada registada com sucesso!")
    else:
        st.warning("Cadastre sócios primeiro!")

elif aba == "Ranking & Pontos":
    st.header("📊 Classificação Final")
    if st.session_state.db_chegadas:
        df = pd.DataFrame(st.session_state.db_chegadas).sort_values("Velocidade", ascending=False)
        max_v = df["Velocidade"].max()
        df["Pontuação"] = df["Velocidade"].apply(lambda x: round((x/max_v)*1000, 2))
        st.dataframe(df, use_container_width=True)
    else:
        st.write("Sem dados de prova.")

elif aba == "Financeiro":
    st.header("💰 Controlo de Quotas")
    st.write("Módulo de pagamentos em desenvolvimento.")
