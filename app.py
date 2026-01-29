import streamlit as st
import pandas as pd
from math import radians, cos, sin, asin, sqrt
import io

# --- MOTOR DE CÁLCULO ---
def haversine(lat1, lon1, lat2, lon2):
    try:
        if not lat1 or not lat2: return 0.0
        lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
        a = sin((lat2-lat1)/2)**2 + cos(lat1) * cos(lat2) * sin((lon2-lon1)/2)**2
        return (2 * asin(sqrt(a))) * 6371 * 1000 
    except: return 0.0

def calc_vel(dist_m, hs, ms, ss, hc, mc, sc):
    try:
        t_voo = ((hc*3600 + mc*60 + sc) - (hs*3600 + ms*60 + ss)) / 60
        return round(dist_m / t_voo, 3) if t_voo > 0 else 0.0
    except: return 0.0

# --- INICIALIZAÇÃO BLINDADA (ESTADO GLOBAL) ---
for chave in ['db_socios', 'db_pombos', 'historico']:
    if chave not in st.session_state:
        if chave == 'historico':
            st.session_state[chave] = pd.DataFrame(columns=["Prova", "Modalidade", "Sócio", "Anilha", "Velocidade", "Pontos", "Tipo"])
        elif chave == 'db_socios':
            st.session_state[chave] = pd.DataFrame(columns=["Nome", "Lat", "Lon"])
        else:
            st.session_state[chave] = pd.DataFrame(columns=["Anilha", "Dono"])

st.set_page_config(page_title="SGC Limeirense 1951", layout="wide")

# --- CABEÇALHO ---
st.markdown("""
    <div style='text-align: center; background-color: #1b5e20; padding: 15px; border-radius: 10px; margin-bottom: 20px;'>
        <h1 style='color: white; margin: 0;'>Clube Columbófilo Limeirense (1951)</h1>
        <p style='color: #e8f5e9; margin: 0;'>Sistema de Gestão Desportiva Estável</p>
    </div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("MENU PRINCIPAL", [
    "👤 Cadastro de Sócios e Pombos",
    "⚙️ Configurar Prova", 
    "🚀 Lançar Resultados", 
    "📊 Apuramento Geral",
    "✏️ Editar/Corrigir Dados"
])

modalidades = ["Filhotes", "Velocidade Adultos", "Meio Fundo Adultos", "Fundo Adultos", "Grande Fundo Adultos"]

# --- 1. CADASTROS (UNIFICADOS PARA NÃO DAR ERRO) ---
if menu == "👤 Cadastro de Sócios e Pombos":
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("👥 Cadastrar Sócio")
        with st.form("form_s", clear_on_submit=True):
            n = st.text_input("Nome do Pombal")
            la = st.text_input("Latitude (ex: -22.56)")
            lo = st.text_input("Longitude (ex: -47.40)")
            if st.form_submit_button("Salvar Sócio"):
                if n and la and lo:
                    st.session_state.db_socios = pd.concat([st.session_state.db_socios, pd.DataFrame([{"Nome":n, "Lat":la, "Lon":lo}])], ignore_index=True)
                    st.success("Sócio salvo!")
                else: st.error("Preencha todos os campos!")
    
    with c2:
        st.subheader("🐦 Cadastrar Anilha")
        if st.session_state.db_socios.empty: st.warning("Cadastre um sócio primeiro!")
        else:
            with st.form("form_p", clear_on_submit=True):
                ani = st.text_input("Número da Anilha")
                dono = st.selectbox("Sócio", st.session_state.db_socios['Nome'].unique())
                if st.form_submit_button("Vincular Pombo"):
                    st.session_state.db_pombos = pd.concat([st.session_state.db_pombos, pd.DataFrame([{"Anilha":ani, "Dono":dono}])], ignore_index=True)
                    st.success("Pombo cadastrado!")

# --- 2. CONFIGURAÇÃO ---
elif menu == "⚙️ Configurar Prova":
    st.subheader("⚙️ Configurar Parâmetros da Prova")
    with st.container(border=True):
        m_sel = st.selectbox("Modalidade", modalidades)
        col1, col2 = st.columns(2)
        with col1:
            cid = st.text_input("Local da Solta")
            lat_s, lon_s = st.text_input("Lat Solta"), st.text_input("Lon Solta")
        with col2:
            p_ini = st.number_input("Pontos do 1º Lugar", value=100.0)
            p_dec = st.number_input("Decréscimo p/ Lugar", value=1.0)
            st.write("Hora Solta")
            hs, ms, ss = st.columns(3)
            h = hs.number_input("H",0,23, key="sh")
            m = ms.number_input("M",0,59, key="sm")
            s = ss.number_input("S",0,59, key="ss")
    if st.button("💾 Gravar Configuração", use_container_width=True):
        st.session_state[f'conf_{m_sel}'] = {"cid":cid, "lat":lat_s, "lon":lon_s, "h":h, "m":m, "s":s, "p":p_ini, "d":p_dec}
        st.success(f"Configuração para {m_sel} salva!")

# --- 3. LANÇAMENTO (O CORAÇÃO DO SISTEMA) ---
elif menu == "🚀 Lançar Resultados":
    mod_v = st.selectbox("Modalidade", modalidades)
    if f'conf_{mod_v}' not in st.session_state:
        st.error(f"Você ainda não configurou a prova de {mod_v}!")
    elif st.session_state.db_socios.empty:
        st.error("Não há sócios cadastrados!")
    else:
        conf = st.session_state[f'conf_{mod_v}']
        s_sel = st.selectbox("Sócio", st.session_state.db_socios['Nome'].unique())
        s_data = st.session_state.db_socios[st.session_state.db_socios.Nome == s_sel].iloc[0]
        dist = haversine(conf['lat'], conf['lon'], s_data.Lat, s_data.Lon)
        
        st.info(f"📍 Solta: {conf['cid']} | 📏 Distância: {dist/1000:.3f} km")

        chegadas = []
        for i in range(1, 7):
            tipo = "PONTUA" if i <= 3 else "EMPURRA"
            with st.expander(f"Pombo {i} - {tipo}", expanded=True):
                c_a, c_h, c_m, c_s = st.columns([2,1,1,1])
                lista_p = st.session_state.db_pombos[st.session_state.db_pombos.Dono == s_sel]['Anilha'].tolist()
                ani_sel = c_a.selectbox(f"Anilha {i}", lista_p if lista_p else ["Sem Pombos"], key=f"ani_{i}")
                hc = c_h.number_input("H",0,23, key=f"h_{i}")
                mc = c_m.number_input("M",0,59, key=f"m_{i}")
                sc = c_s.number_input("S",0,59, key=f"s_{i}")
                v = calc_vel(dist, conf['h'], conf['m'], conf['s'], hc, mc, sc)
                chegadas.append({"Modalidade":mod_v, "Sócio":s_sel, "Anilha":ani_sel, "Velocidade":v, "Tipo":tipo})

        if st.button("🏆 Gravar e Calcular Pontos", use_container_width=True):
            df_t = pd.DataFrame(chegadas).sort_values("Velocidade", ascending=False).reset_index(drop=True)
            for idx, r in df_t.iterrows():
                r['Pontos'] = max(0, conf['p'] - (idx * conf['d']))
                st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([r])], ignore_index=True)
            st.success("Resultados gravados no histórico!")

# --- 4. APURAMENTO ---
elif menu == "📊 Apuramento Geral":
    df = st.session_state.historico
    if df.empty: st.info("Histórico vazio.")
    else:
        t1, t2 = st.tabs(["SÓCIOS", "POMBO ÁS"])
        with t1: st.table(df[df.Tipo == 'PONTUA'].groupby('Sócio')['Pontos'].sum().sort_values(ascending=False))
        with t2: st.table(df.groupby(['Anilha', 'Sócio'])['Pontos'].sum().sort_values(ascending=False))
