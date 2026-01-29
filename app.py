import streamlit as st
import pandas as pd

st.set_page_config(page_title="Clube Limeirense 1951", layout="wide")
st.title("🏛️ Clube Limeirense 1951")
st.subheader("Sistema de Apuração de Resultados")

if 'dados' not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=["Sócio", "Anilha", "Distância (km)", "Tempo (min)", "Velocidade (m/min)"])

menu = st.sidebar.radio("Menu:", ["Cadastrar Voo", "Ver Ranking", "Limpar"])

if menu == "Cadastrar Voo":
    with st.form("add"):
        c1, c2 = st.columns(2)
        socio = c1.text_input("Nome do Sócio")
        anilha = c1.text_input("Anilha")
        dist = c2.number_input("Distância (km)", min_value=0.0)
        tempo = c2.number_input("Tempo (minutos)", min_value=0.1)
        if st.form_submit_button("Salvar"):
            vel = (dist * 1000) / tempo
            novo = pd.DataFrame([{"Sócio": socio, "Anilha": anilha, "Distância (km)": dist, "Tempo (min)": tempo, "Velocidade (m/min)": round(vel, 3)}])
            st.session_state.dados = pd.concat([st.session_state.dados, novo], ignore_index=True)
            st.success("Registrado!")

elif menu == "Ver Ranking":
    st.table(st.session_state.dados.sort_values(by="Velocidade (m/min)", ascending=False))
