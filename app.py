import streamlit as st
import pandas as pd

st.set_page_config(page_title="SGC - Sistema Columbófilo", layout="wide")

st.title("🕊️ SGC - Sistema de Gestão Columbófila")

menu = st.sidebar.radio("Navegação", ["⚙️ Configurar Prova", "🚀 Lançar Chegadas (3+3)", "📊 Classificação"])

if menu == "⚙️ Configurar Prova":
    st.header("⚙️ Parametrização da Solta")
    col1, col2 = st.columns(2)
    with col1:
        cidade = st.text_input("Cidade da Solta", placeholder="Ex: Portalegre")
        st.write("---")
        st.write("**Hora da Solta**")
        c1, c2, c3 = st.columns(3)
        h_s = c1.number_input("Hora", 0, 23, 8)
        m_s = c2.number_input("Min", 0, 59, 0)
        s_s = c3.number_input("Seg", 0, 59, 0)
    with col2:
        modalidade = st.selectbox("Modalidade", ["Velocidade", "Meio-Fundo", "Fundo"])
        p_inicial = st.number_input("Pontuação Inicial", value=100.0)
        decrescimento = st.number_input("Decréscimo (Livre)", value=1.0, step=0.1)
    
    if st.button("Gravar Configuração"):
        st.session_state['prova'] = {"cidade": cidade, "mod": modalidade, "p_ini": p_inicial, "dec": decrescimento}
        st.success("Configuração Guardada!")

elif menu == "🚀 Lançar Chegadas (3+3)":
    st.header("🚀 Lançamento de Designados")
    socio = st.text_input("Nome do Sócio / Pombal")
    
    st.write("Introduza as anilhas (Ex: 2004466/26) e os tempos:")
    
    for i in range(1, 7):
        # Diferenciação visual para os 3 que pontuam e os 3 que empurram
        tipo = "PONTUA" if i <= 3 else "EMPURRA"
        cor = "blue" if i <= 3 else "orange"
        
        st.markdown(f"**Pombo {i} - :{cor}[{tipo}]**")
        c_ani, c_h, c_m, c_s = st.columns([2, 1, 1, 1])
        
        with c_ani:
            st.text_input(f"Anilha/Ano", placeholder="0000000/26", key=f"ani_{i}")
        with c_h:
            st.number_input("HH", 0, 23, key=f"h_{i}")
        with c_m:
            st.number_input("MM", 0, 59, key=f"m_{i}")
        with c_s:
            st.number_input("SS", 0, 59, key=f"s_{i}")

    if st.button("Gerar Classificação desta Série"):
        st.success(f"Série de {socio} processada com sucesso!")

elif menu == "📊 Classificação":
    st.info("Aqui aparecerá a lista final com as velocidades e os pontos atribuídos.")
