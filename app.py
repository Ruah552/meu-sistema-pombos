import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração de estilo
st.set_page_config(page_title="Clube Limeirense 1951", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { width: 100%; background-color: #004a99; color: white; }
    </style>
    """, unsafe_allow_input_with_ some_updates=True)

st.title("🏛️ Clube Limeirense 1951")
st.subheader("Sistema Profissional de Apuração Columbófila")

# Banco de dados do sistema
if 'ranking' not in st.session_state:
    st.session_state.ranking = pd.DataFrame(
        columns=["Sócio", "Anilha", "Distância (km)", "Solta", "Chegada", "Velocidade (m/min)"]
    )

# Menu Lateral
opcao = st.sidebar.selectbox("O que deseja fazer?", ["Registrar Chegada", "Ver Classificação Geral", "Limpar Prova"])

if opcao == "Registrar Chegada":
    st.header("📥 Cadastro de Resultados")
    
    with st.form("apuracao"):
        col1, col2 = st.columns(2)
        with col1:
            socio = st.text_input("Nome do Sócio")
            anilha = st.text_input("Número da Anilha")
            distancia = st.number_input("Distância Real (km)", min_value=0.0, format="%.3f")
        
        with col2:
            h_solta = st.time_input("Hora da Solta", value=datetime.strptime("07:00", "%H:%M"))
            h_chegada = st.time_input("Hora da Chegada", value=datetime.strptime("11:00", "%H:%M"))
        
        btn = st.form_submit_button("Calcular Velocidade e Salvar")

        if btn:
            # Cálculo do tempo em minutos
            t1 = datetime.combine(datetime.today(), h_solta)
            t2 = datetime.combine(datetime.today(), h_chegada)
            tempo_total = (t2 - t1).total_seconds() / 60
            
            if tempo_total <= 0:
                st.error("Erro: A hora de chegada deve ser depois da solta!")
            else:
                # FÓRMULA OFICIAL: (Metros / Minutos)
                vel = (distancia * 1000) / tempo_total
                
                novo_pombo = pd.DataFrame([{
                    "Sócio": socio,
                    "Anilha": anilha,
                    "Distância (km)": distancia,
                    "Solta": h_solta.strftime("%H:%M"),
                    "Chegada": h_chegada.strftime("%H:%M"),
                    "Velocidade (m/min)": round(vel, 3)
                }])
                
                st.session_state.ranking = pd.concat([st.session_state.ranking, novo_pombo], ignore_index=True)
                st.success(f"Pombo {anilha} registrado! Velocidade: {vel:.3f} m/min")

elif opcao == "Ver Classificação Geral":
    st.header("🏆 Ranking Oficial - Clube Limeirense")
    
    if st.session_state.ranking.empty:
        st.info("Nenhum dado registrado para esta prova.")
    else:
        # Ordena do mais rápido para o mais lento
        df_ordenado = st.session_state.ranking.sort_values(by="Velocidade (m/min)", ascending=False).reset_index(drop=True)
        df_ordenado.index += 1  # Para começar o ranking no 1º lugar
        
        st.table(df_ordenado)
        
        # Botão para baixar o resultado
        csv = df_ordenado.to_csv(index=True).encode('utf-8')
        st.download_button("📥 Baixar Planilha de Resultados", csv, "resultado_limeirense.csv", "text/csv")

elif opcao == "Limpar Prova":
    if st.button("⚠️ APAGAR TODOS OS DADOS DA PROVA ATUAL"):
        st.session_state.ranking = pd.DataFrame(columns=["Sócio", "Anilha", "Distância (km)", "Solta", "Chegada", "Velocidade (m/min)"])
        st.rerun()
