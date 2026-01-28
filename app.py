import streamlit as st
import pandas as pd
from math import radians, cos, sin, asin, sqrt
from datetime import datetime

# --- CONFIGURAÇÃO E IDENTIDADE NOVA ---
st.set_page_config(page_title="SGC - Gestão Columbófila", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stTable { background-color: white; border-radius: 10px; border: 1px solid #ddd; }
    .stButton>button { background-color: #1a73e8; color: white; border-radius: 8px; font-weight: bold; }
    .titulo-gpc { color: #1a73e8; font-family: 'Arial'; font-weight: bold; }
    </style>
    """, unsafe_allow_stdio=True)

# --- SEGURANÇA ---
SENHA_SISTEMA = "1234"
if "autenticado" not in st.session_state: st.session_state.autenticado = False

def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371.0088
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon, dlat = lon2 - lon1, lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * R

if not st.session_state.autenticado:
    st.markdown("<h1 class='titulo-gpc'>🕊️ SGC - Acesso Restrito</h1>", unsafe_allow_stdio=True)
    senha = st.text_input("Identificação do Utilizador:", type="password")
    if st.button("ACEDER AO SISTEMA"):
        if senha == SENHA_SISTEMA:
            st.session_state.autenticado = True
            st.rerun()
        else: st.error("Acesso Negado.")
else:
    # Memória do Sistema
    if "concorrentes" not in st.session_state: st.session_state.concorrentes = []
    if "recenseamento" not in st.session_state: st.session_state.recenseamento = []
    if "prova_ativa" not in st.session_state: st.session_state.prova_ativa = []
    if "campeonato" not in st.session_state: st.session_state.campeonato = pd.DataFrame()
    if "dados_prova" not in st.session_state: st.session_state.dados_prova = {}

    # MENU LATERAL (ESTILO SGC)
    with st.sidebar:
        st.markdown("<h2 class='titulo-gpc'>SGC MENU</h2>", unsafe_allow_stdio=True)
        opcao = st.radio("Selecione o Sub-Sistema:", ["Associados", "Pombos", "Concursos", "Lançamentos", "Classificações", "Relatórios Geras"])
        st.divider()
        if st.button("SAIR"):
            st.session_state.autenticado = False
            st.rerun()

    # --- SUB-SISTEMAS ---
    if opcao == "Associados":
        st.header("👥 Gestão de Associados")
        with st.form("f_assoc"):
            c1, c2, c3 = st.columns(3)
            n = c1.text_input("Nome")
            la = c2.number_input("Lat", format="%.6f")
            lo = c3.number_input("Lon", format="%.6f")
            if st.form_submit_button("Gravar"):
                st.session_state.concorrentes.append({"Nome": n, "Lat": la, "Lon": lo})
        st.table(pd.DataFrame(st.session_state.concorrentes))

    elif opcao == "Pombos":
        st.header("🕊️ Recenseamento de Pombos")
        if st.session_state.concorrentes:
            with st.form("f_pom"):
                d = st.selectbox("Dono", [c["Nome"] for c in st.session_state.concorrentes])
                a = st.text_input("Anilha")
                cat = st.selectbox("Categoria", ["Adulto", "Borracho", "Geral"])
                if st.form_submit_button("Efectuar Recenseamento"):
                    st.session_state.recenseamento.append({"Dono": d, "Anilha": a, "Cat": cat})
            st.table(pd.DataFrame(st.session_state.recenseamento))

    elif opcao == "Concursos":
        st.header("📅 Dados da Prova")
        with st.form("f_con"):
            n = st.text_input("Nome da Prova")
            loc = st.text_input("Local de Soltura")
            c1, c2 = st.columns(2)
            d = c1.date_input("Data Soltura")
            h = c2.time_input("Hora Soltura")
            la_s = c1.number_input("Lat Solta", format="%.6f")
            lo_s = c2.number_input("Lon Solta", format="%.6f")
            if st.form_submit_button("Confirmar Dados"):
                st.session_state.dados_prova = {"Nome":n, "Local":loc, "Data":d, "Hora":h, "Lat":la_s, "Lon":lo_s}
                st.success("Configuração de Prova Gravada!")

    elif opcao == "Lançamentos":
        st.header("📥 Lançamentos e Pernoite")
        c1, c2 = st.columns(2)
        h_para = c1.time_input("Início Tempo Morto", value=datetime.strptime("20:00", "%H:%M"))
        h_volta = c2.time_input("Fim Tempo Morto", value=datetime.strptime("05:30", "%H:%M"))

        if st.session_state.recenseamento:
            with st.form("f_lan"):
                pombo = st.selectbox("Pombo Chegado", [f"{p['Anilha']} - {p['Dono']} ({p['Cat']})" for p in st.session_state.recenseamento])
                d_c = st.date_input("Data Chegada")
                h_c = st.time_input("Hora Chegada")
                if st.form_submit_button("Gravar Batida"):
                    dp = st.session_state.dados_prova
                    inicio = datetime.combine(dp["Data"], dp["Hora"])
                    fim = datetime.combine(d_c, h_c)
                    t_min = (fim - inicio).total_seconds() / 60
                    if d_c > dp["Data"]:
                        noites = (d_c - dp["Data"]).days
                        m_morte = (1440 - (h_para.hour*60+h_para.minute)) + (h_volta.hour*60+h_volta.minute)
                        t_min -= (noites * m_morte)
                    
                    ani_f = pombo.split(" - ")[0]
                    dono_f = pombo.split(" - ")[1].split(" (")[0]
                    cat_f = pombo.split("(")[1].replace(")", "")
                    soc = next(s for s in st.session_state.concorrentes if s["Nome"] == dono_f)
                    dist = calcular_distancia(dp["Lat"], dp["Lon"], soc["Lat"], soc["Lon"])
                    vel = (dist * 1000) / t_min
                    st.session_state.prova_ativa.append({"Anilha": ani_f, "Concorrente": dono_f, "Cat": cat_f, "Dist": round(dist*1000, 2), "Vel": round(vel, 3)})
                    st.success("Lançamento efectuado com sucesso!")

    elif opcao == "Classificações":
        st.header("📊 Classificação Oficial")
        c_pts1, c_pts2 = st.columns(2)
        pts_topo = c_pts1.number_input("Pontos 1º Lugar:", value=100)
        intervalo = c_pts2.number_input("Escala de Perca (1 para 1-1, 5 para 5-5):", value=1, min_value=1)

        if st.session_state.prova_ativa:
            df = pd.DataFrame(st.session_state.prova_ativa).sort_values("Vel", ascending=False).reset_index(drop=True)
            df.insert(0, "Pos", range(1, len(df) + 1))
            df["Pontos"] = [max(pts_topo - (i * intervalo), 0) for i in range(len(df))]
            
            st.table(df)
            
            # --- GERADOR DE TEXTO PARA WHATSAPP ---
            st.subheader("📢 Resumo para Partilha")
            texto_wa = f"*🏆 RESULTADO: {st.session_state.dados_prova['Nome']}*\n"
            for i, row in df.head(5).iterrows():
                texto_wa += f"{row['Pos']}º {row['Concurrente']} - {row['Vel']} m/m\n"
            st.text_area("Copie para o WhatsApp:", texto_wa, height=150)

            if st.button("FINALIZAR E ARQUIVAR PROVA"):
                st.session_state.campeonato = pd.concat([st.session_state.campeonato, df])
                st.session_state.prova_ativa = []
                st.rerun()

    elif opcao == "Relatórios Geras":
        st.header("🏆 Campeonato Geral - Anilha de Ouro")
        if not st.session_state.campeonato.empty:
            res = st.session_state.campeonato.groupby(["Anilha", "Concorrente", "Cat"])["Pontos"].sum().sort_values(ascending=False).reset_index()
            st.table(res)
            st.download_button("📥 Exportar Dados (CSV)", st.session_state.campeonato.to_csv(index=False), "campeonato_sgc.csv")
