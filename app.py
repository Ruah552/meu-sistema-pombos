import streamlit as st
import pandas as pd

st.set_page_config(page_title="SGC - Gestão Columbófila", layout="wide")

# Interface do Sistema
st.title("🕊️ SGC - Sistema de Gestão Columbófila")

# Menu Lateral
menu = st.sidebar.radio("Navegação", ["⚙️ Configurar Prova", "🚀 Lançar Chegadas", "📊 Classificação"])

if menu == "⚙️ Configurar Prova":
    st.header("⚙️ Parametrização da Solta")
    col1, col2 = st.columns(2)
    with col1:
        cidade = st.text_input("Cidade da Solta", placeholder="Ex: Portalegre")
        hora_solta = st.time_input("Hora da Solta")
        modalidade = st.selectbox("Modalidade", ["Velocidade", "Meio-Fundo", "Fundo"])
    with col2:
        lat_solta = st.text_input("Latitude Solta (Decimal)")
        lon_solta = st.text_input("Longitude Solta (Decimal)")
        p_inicial = st.number_input("Pontuação Inicial", value=100.0)
        decrescimento = st.number_input("Decréscimo (Livre)", value=1.0, step=0.1)
    
    if st.button("Gravar Configuração"):
        st.session_state['prova'] = {
            "cidade": cidade, "hora": str(hora_solta), "mod": modalidade, 
            "p_ini": p_inicial, "dec": decrescimento
        }
        st.success(f"Prova de {modalidade} configurada!")

elif menu == "🚀 Lançar Chegadas":
    st.header("🚀 Lançamento de Designados (Regra 3+3)")
    st.write("Introduza os 6 pombos designados que entraram na classificação.")
    
    socio = st.text_input("Nome do Sócio")
    
    # Grid para lançar os 6 pombos rapidamente
    st.subheader("Dados dos 6 Pombos")
    col_anilha, col_hora = st.columns(2)
    
    pombos_chegada = []
    for i in range(1, 7):
        with col_anilha:
            anilha = st.text_input(f"Anilha {i}", key=f"a_{i}")
        with col_hora:
            tempo = st.text_input(f"Hora Chegada (HH:MM:SS) {i}", key=f"t_{i}")
        pombos_chegada.append({"anilha": anilha, "hora": tempo})

    if st.button("Processar Classificação"):
        st.info(f"A processar: Os 3 mais rápidos de {socio} somam pontos; os outros 3 apenas empurram.")
        # Futuramente: Enviar para o Google Sheets

elif menu == "📊 Classificação":
    if 'prova' in st.session_state:
        p = st.session_state['prova']
        st.subheader(f"📊 Classificação: {p['cidade']} ({p['mod']})")
        st.write(f"**Solta:** {p['hora']} | **Regra:** {p['p_ini']} pts (-{p['dec']} por lugar)")
        st.info("A tabela aparecerá aqui após o processamento dos dados.")
    else:
        st.warning("Configure a prova primeiro no menu lateral.")
