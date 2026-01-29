import streamlit as st
import pandas as pd
from math import radians, cos, sin, asin, sqrt
import io

# --- MOTOR DE CÁLCULO SEGURO ---
def haversine(lat1, lon1, lat2, lon2):
    try:
        if not all([lat1, lon1, lat2, lon2]): return 0.0
        lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
        a = sin((lat2-lat1)/2)**2 + cos(lat1) * cos(lat2) * sin((lon2-lon1)/2)**2
        return (2 * asin(sqrt(a))) * 6371 * 1000 
    except Exception: return 0.0

def calc_vel(dist_m, hs, ms, ss, hc, mc, sc):
    try:
        t_voo = ((hc*3600 + mc*60 + sc) - (hs*3600 + ms*60 + ss)) / 60
        return round(dist_m / t_voo, 3) if t_voo > 0 else 0.0
    except Exception: return 0.0

# --- INICIALIZAÇÃO DE SEGURANÇA ---
for key in ['db_socios', 'db_pombos', 'historico']:
    if key not in st.session_state:
        if key == 'historico':
            st.session_state[key] = pd.DataFrame(columns=["Prova", "Modalidade", "Sócio", "Anilha", "Velocidade", "Pontos", "Tipo"])
        elif key == 'db_socios':
            st.session_state[key] = pd.DataFrame(columns=["Nome", "Lat", "Lon"])
        else:
            st.session_state[key] = pd.DataFrame(columns=["Anilha", "Dono"])

st.set_page_config(page_title="SGC Limeirense 1951", layout="wide")

# --- CABEÇALHO ---
st.markdown("<h1 style='text-align: center; color: #1b5e20;'>Clube Columbófilo Limeirense</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Fundado em 1951 | Gestão de Provas</p>", unsafe_allow_html=True)

menu = st.sidebar.radio("Selecione a tarefa:", [
    "👤 Sócios e Pombos", 
    "⚙️ Configurar Prova", 
    "🚀 Lançar Resultados", 
    "📊 Apuramento Geral",
    "📑 Relatórios"
])

# --- 1. CADASTROS UNIFICADOS (MAIS FÁCIL DE VER) ---
if menu == "👤 Sócios e Pombos":
    col_s, col_p = st.columns(2)
    with col_s:
        st.subheader("👤 Novo Sócio")
        with st.form("f_socio", clear_on_submit=True):
            n = st.text_input("Nome do Sócio")
            la, lo = st.text_input("Lat"), st.text_input("Lon")
            if st.form_submit_button("Cadastrar"):
                st.session_state.db_socios = pd.concat([st.session_state.db_socios, pd.DataFrame([{"Nome": n, "Lat": la, "Lon": lo}])], ignore_index=True)
                st.success("Sócio salvo!")
    with col_p:
        st.subheader("🐦 Novo Pombo")
        with st.form("f_pombo", clear_on_submit=True):
            ani = st.text_input("Anilha")
            dono = st.selectbox("Dono", st.session_state.db_socios['Nome'].unique() if not st.session_state.db_socios.empty else [""])
            if st.form_submit_button("Vincular"):
                st.session_state.db_pombos = pd.concat([st.session_state.db_pombos, pd.DataFrame([{"Anilha": ani, "Dono": dono}])], ignore_index=True)
                st.success("Pombo vinculado!")

# --- 2. LANÇAMENTO COM VERIFICAÇÃO DE ERRO ---
elif menu == "🚀 Lançar Resultados":
    mod_lista = ["Filhotes", "Velocidade Adultos", "Meio Fundo Adultos", "Fundo Adultos", "Grande Fundo Adultos"]
    m_at = st.selectbox("Modalidade", mod_lista)
    
    if f'c_{m_at}' not in st.session_state:
        st.error(f"Atenção: A prova de {m_at} não foi configurada no menu 'Configurar Prova'!")
    else:
        conf = st.session_state[f'c_{m_at}']
        s_sel = st.selectbox("Sócio", st.session_state.db_socios['Nome'].unique())
        
        # BUSCA COORDENADAS DO SÓCIO
        s_data = st.session_state.db_socios[st.session_state.db_socios.Nome == s_sel].iloc[0]
        dist = haversine(conf['lat'], conf['lon'], s_data.Lat, s_data.Lon)
        
        st.write(f"📏 Distância calculada: **{dist/1000:.3f} km**")

        dados_prova = []
        for i in range(1, 7):
            tipo = "PONTUA" if i <= 3 else "EMPURRA"
            with st.expander(f"Pombo {i} - {tipo}", expanded=True):
                c1, c2, c3, c4 = st.columns([2,1,1,1])
                pombos_filtro = st.session_state.db_pombos[st.session_state.db_pombos.Dono == s_sel]['Anilha'].tolist()
                ani_sel = c1.selectbox(f"Anilha", pombos_filtro if pombos_filtro else ["Nenhum pombo"], key=f"a{i}")
                hc = c2.number_input("H", 0, 23, key=f"h{i}")
                mc = c3.number_input("M", 0, 59, key=f"m{i}")
                sc = c4.number_input("S", 0, 59, key=f"s{i}")
                
                v = calc_vel(dist, conf['h'], conf['m'], conf['s'], hc, mc, sc)
                dados_prova.append({"Modalidade": m_at, "Sócio": s_sel, "Anilha": ani_sel, "Velocidade": v, "Tipo": tipo})

        if st.button("💾 Gravar Prova e Gerar Pontuação"):
            df_p = pd.DataFrame(dados_prova).sort_values("Velocidade", ascending=False).reset_index(drop=True)
            for idx, r in df_p.iterrows():
                r['Pontos'] = max(0, conf['p'] - (idx * conf['d']))
                st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([r])], ignore_index=True)
            st.success("Resultados gravados!")

# --- 3. APURAMENTO (SÓCIOS E POMBOS) ---
elif menu == "📊 Apuramento Geral":
    st.subheader("🏆 Rankings de Sócios e Pombos")
    df = st.session_state.historico
    if not df.empty:
        t1, t2 = st.tabs(["👥 Concorrentes", "🕊️ Pombo Ás"])
        with t1:
            st.write("Soma dos 3 pombos 'PONTUA'")
            st.dataframe(df[df.Tipo == 'PONTUA'].groupby('Sócio')['Pontos'].sum().sort_values(ascending=False))
        with t2:
            st.write("Soma de pontos por Anilha")
            st.dataframe(df.groupby(['Anilha', 'Sócio'])['Pontos'].sum().sort_values(ascending=False))
    else:
        st.warning("Sem dados no histórico.")
