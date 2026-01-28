import streamlit as st
import pandas as pd
from math import radians, cos, sin, asin, sqrt

# Função Haversine (Matemática de Precisão Geográfica)
def calcular_distancia(lat1, lon1, lat2, lon2):
    # Converte graus para radianos
    lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
    # Haversine
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Raio da Terra em km
    return c * r * 1000 # Retorna distância exata em METROS

st.set_page_config(page_title="SGC - Gestão Columbófila", layout="wide")

st.title("🕊️ SGC - Precisão Matemática Total")

menu = st.sidebar.radio("Navegação", ["⚙️ Configurar Prova", "🚀 Lançar Chegadas (3+3)", "📊 Classificação"])

if menu == "⚙️ Configurar Prova":
    st.header("⚙️ Parametrização da Solta")
    col1, col2 = st.columns(2)
    with col1:
        cidade = st.text_input("Cidade da Solta")
        c_lat = st.text_input("Lat. Solta (Ex: 39.406522)")
        c_lon = st.text_input("Lon. Solta (Ex: -7.432111)")
        # ... (restante dos campos de hora e pontos igual ao anterior)
    
    if st.button("Gravar Configuração"):
        st.session_state['prova'] = {"cidade": cidade, "lat": c_lat, "lon": c_lon}
        st.success("Coordenadas de Solta Bloqueadas para Cálculo.")

elif menu == "🚀 Lançar Chegadas (3+3)":
    st.header("🚀 Lançamento com Cálculo Automático")
    # Interface de lançamento dos 6 pombos
    st.info("O sistema usará a Fórmula de Haversine para calcular a velocidade de cada pombo.")
    # (O formulário de 6 pombos que já criámos)

elif menu == "📊 Classificação":
    st.header("📊 Resultado Oficial")
    st.write("Cálculos baseados em Geometria Esférica (Norma Internacional).")
