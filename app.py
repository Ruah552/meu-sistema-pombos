import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
from math import radians, cos, sin, asin, sqrt

# --- FUNÇÃO DE CÁLCULO DE TEMPO COM HORÁRIO MORTO ---
def calcular_tempo_real(h_soltura, h_chegada, h_morto_inicio, h_morto_fim):
    # Se a chegada for no mesmo dia
    t_soltura = datetime.combine(datetime.today(), h_soltura)
    t_chegada = datetime.combine(datetime.today(), h_chegada)
    
    if t_chegada > t_soltura:
        total_minutos = (t_chegada - t_soltura).total_seconds() / 60
        return total_minutos
    else:
        # Se a chegada for no dia seguinte, calcula o desconto do horário morto
        t_chegada_amanha = t_chegada + timedelta(days=1)
        # Tempo bruto em minutos
        tempo_bruto = (t_chegada_amanha - t_soltura).total_seconds() / 60
        
        # Cálculo do período morto (noite)
        t_morto_inicio = datetime.combine(datetime.today(), h_morto_inicio)
        t_morto_fim = datetime.combine(datetime.today() + timedelta(days=1), h_morto_fim)
        minutos_mortos = (t_morto_fim - t_morto_inicio).total_seconds() / 60
        
        return tempo_bruto - minutos_mortos

# --- INTERFACE ---
st.title("🕊️ SGC - Sistema Profissional com Horário Morto")

menu = st.sidebar.radio("Módulos", ["Configurar Concurso", "Classificação"])

if menu == "Configurar Concurso":
    st.header("🚀 Lançamento de Prova")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Dados da Soltura")
        h_soltura = st.time_input("Hora da Soltura", value=time(7, 0))
        lat_s = st.number_input("Lat Soltura", format="%.6f")
        lon_s = st.number_input("Lon Soltura", format="%.6f")
        
    with col2:
        st.subheader("Configuração Horário Morto")
        h_morto_in = st.time_input("Início (Ex: 20:00)", value=time(20, 0))
        h_morto_fim = st.time_input("Fim (Ex: 06:00)", value=time(6, 0))
    
    st.divider()
    
    st.subheader("Registo de Chegadas")
    with st.form("chegada"):
        anilha = st.text_input("Nº da Anilha")
        dias = st.selectbox("Dia da Chegada", ["Mesmo Dia", "Dia Seguinte"])
        h_chegada = st.time_input("Hora da Batida")
        
        if st.form_submit_button("Calcular Velocidade"):
            # Lógica simplificada para teste
            tempo = calcular_tempo_real(h_soltura, h_chegada, h_morto_in, h_morto_fim)
            st.success(f"Tempo de voo apurado (com desconto de horário morto): {tempo:.2f} minutos")

elif menu == "Classificação":
    st.write("Os resultados aqui já aparecerão com os pontos e médias corrigidos pelo horário morto.")
