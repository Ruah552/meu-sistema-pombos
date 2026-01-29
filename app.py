import streamlit as st
import pandas as pd
from math import radians, cos, sin, asin, sqrt
import io

# --- MOTOR DE CÁLCULO ---
def haversine(lat1, lon1, lat2, lon2):
    try:
        lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
        a = sin((lat2-lat1)/2)**2 + cos(lat1) * cos(lat2) * sin((lon2-lon1)/2)**2
        return (2 * asin(sqrt(a))) * 6371 * 1000 
    except: return 0.0

def calc_vel(dist_m, hs, ms, ss, hc, mc, sc):
    try:
        t_voo = ((hc*3600 + mc*60 + sc) - (hs*3600 + ms*60 + ss)) / 60
        return round(dist_m / t_voo, 3) if t_voo > 0 else 0.0
    except: return 0.0

# --- INICIALIZAÇÃO DA MEMÓRIA ---
if 'db_socios' not in st.session_state: st.session_state['db_socios'] = pd.DataFrame(columns=["Nome", "Lat", "Lon"])
if 'db_pombos' not in st.session_state: st.session_state['db_pombos'] = pd.DataFrame(columns=["Anilha", "Dono"])
if 'historico' not in st.session_state: st.session_state['historico'] = pd.DataFrame(columns=["Prova", "Modalidade", "Sócio", "Anilha", "Velocidade", "Pontos", "Tipo"])

st.set_page_config(page_title="SGC - Limeirense 1951", layout="wide")

# --- CABEÇALHO ---
st.markdown(f"""
    <div style="text-align: center; border: 2px solid #2e7d32; border-radius: 10px; padding: 10px; background-color: #f1f8e9;">
        <h1 style="margin: 0; color: #2e7d32;">Clube Columbófilo Limeirense</h1>
        <h3 style="margin: 0; color: #555;">Fundado em 1951</h3>
    </div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("Navegação", [
    "⚙️ Configurar Prova", 
    "👤 Cadastro de Sócios", 
    "🐦 Cadastro de Pombos", 
    "🚀 Lançar Chegadas (3+3)", 
    "✏️ Corrigir/Editar Provas", 
    "📊 Apuramento Geral e Modalidade",
    "📑 Relatórios para Impressão"
])

modalidades = ["Filhotes", "Velocidade Adultos", "Meio Fundo Adultos", "Fundo Adultos", "Grande Fundo Adultos"]

# --- 1. CONFIGURAÇÃO (PONTUAÇÃO AJUSTÁVEL AQUI) ---
if menu == "⚙️ Configurar Prova":
    st.subheader("⚙️ Configuração da Calculadora de Pontos")
    with st.container(border=True):
        m_sel = st.selectbox("Selecione a Modalidade", modalidades)
        col1, col2 = st.columns(2)
        with col1:
            cid = st.text_input("Local da Solta (Cidade)")
            lat_s = st.text_input("Latitude Solta")
            lon_s = st.text_input("Longitude Solta")
        with col2:
            st.write("**⚠️ Ajuste de Pontuação**")
            p_ini = st.number_input("Pontos para o 1º Lugar", value=1000.0, step=10.0)
            p_dec = st.number_input("Decréscimo por lugar (ex: 1 ponto a menos)", value=1.0, step=0.1)
            st.write("**Hora da Solta**")
            h, m, s = st.columns(3)
            hs, ms, ss = h.number_input("H",0,23), m.number_input("M",0,59), s.number_input("S",0,59)
            
    if st.button("💾 Gravar Configuração da Prova"):
        st.session_state[f'c_{m_sel}'] = {"cid": cid, "lat": lat_s, "lon": lon_s, "h": hs, "m": ms, "s": ss, "p": p_ini, "d": p_dec}
        st.success(f"Prova de {m_sel} configurada com 1º lugar valendo {p_ini} pontos!")

# --- 2. LANÇAMENTO (INTERFACE MELHORADA) ---
elif menu == "🚀 Lançar Chegadas (3+3)":
    mod_at = st.selectbox("Lançar para qual gaveta?", modalidades)
    if f'c_{mod_at}' not in st.session_state:
        st.error("Configure a prova primeiro no menu acima!")
    else:
        conf = st.session_state[f'c_{mod_at}']
        st.info(f"📍 Solta: {conf['cid']} | Pontuação Inicial: {conf['p']} | Decréscimo: {conf['d']}")
        
        with st.container(border=True):
            s_sel = st.selectbox("Escolha o Sócio/Concorrente", st.session_state['db_socios']['Nome'].unique())
            dados_s = st.session_state['db_socios'][st.session_state['db_socios']['Nome'] == s_sel].iloc[0]
            dist = haversine(conf['lat'], conf['lon'], dados_s['Lat'], dados_s['Lon'])
            st.write(f"📏 **Distância para o Pombal:** {dist/1000:.3f} km")

        st.subheader("⏱️ Registro de Chegadas")
        temp_list = []
        for i in range(1, 7):
            is_designado = i <= 3
            tipo = "PONTUA" if is_designado else "EMPURRA"
            cor = "#e3f2fd" if is_designado else "#fff3e0"
            
            with st.container(border=True):
                st.markdown(f"<div style='background-color:{cor}; padding:5px;'><strong>Pombo {i} - {tipo}</strong></div>", unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                ani = c1.selectbox(f"Anilha", st.session_state['db_pombos'][st.session_state['db_pombos']['Dono'] == s_sel]['Anilha'].unique(), key=f"ani_{i}")
                hc = c2.number_input("Hora", 0, 23, key=f"h{i}")
                mc = c3.number_input("Min", 0, 59, key=f"m{i}")
                sc = c4.number_input("Seg", 0, 59, key=f"s{i}")
                vel = calc_vel(dist, conf['h'], conf['m'], conf['s'], hc, mc, sc)
                temp_list.append({"Modalidade": mod_at, "Sócio": s_sel, "Anilha": ani, "Velocidade": vel, "Tipo": tipo})

        if st.button("🏆 Calcular e Gravar no Histórico"):
            # AQUI A CALCULADORA TRABALHA COM O AJUSTE QUE DEFINISTE
            df_novos = pd.DataFrame(temp_list).sort_values(by="Velocidade", ascending=False).reset_index(drop=True)
            for index, row in df_novos.iterrows():
                row['Pontos'] = conf['p'] - (index * conf['d'])
                st.session_state['historico'] = pd.concat([st.session_state['historico'], pd.DataFrame([row])], ignore_index=True)
            st.success("Resultados gravados e pontos calculados com sucesso!")

# --- 3. APURAMENTO (DUPLO) ---
elif menu == "📊 Apuramento Geral e Modalidade":
    opcao = st.selectbox("Escolha o Campeonato:", ["GERAL ABSOLUTO"] + modalidades)
    df = st.session_state['historico']
    
    tab_con, tab_pom = st.tabs(["👥 Ranking de Sócios", "🕊️ Ranking Pombo Ás"])
    
    if not df.empty:
        df_f = df if opcao == "GERAL ABSOLUTO" else df[df['Modalidade'] == opcao]
        with tab_con:
            # SOMA SÓ DESIGNADOS
            res_s = df_f[df_f['Tipo'] == 'PONTUA'].groupby('Sócio')['Pontos'].sum().sort_values(ascending=False).reset_index()
            st.table(res_s)
        with tab_pom:
            # SOMA TUDO POR ANILHA
            res_p = df_f.groupby(['Anilha', 'Sócio'])['Pontos'].sum().sort_values(ascending=False).reset_index()
            st.table(res_p)
