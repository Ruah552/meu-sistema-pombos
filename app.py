import streamlit as st
import pandas as pd
from math import radians, cos, sin, asin, sqrt
import io

# --- 1. MOTOR DE CÁLCULO (HAVERSINE) ---
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

# --- 2. INICIALIZAÇÃO DE MEMÓRIA (NÃO APAGA NADA) ---
if 'db_socios' not in st.session_state: st.session_state['db_socios'] = pd.DataFrame(columns=["Nome", "Lat", "Lon"])
if 'db_pombos' not in st.session_state: st.session_state['db_pombos'] = pd.DataFrame(columns=["Anilha", "Dono"])
if 'historico' not in st.session_state: 
    st.session_state['historico'] = pd.DataFrame(columns=["Prova", "Modalidade", "Sócio", "Anilha", "Velocidade", "Pontos", "Tipo"])

st.set_page_config(page_title="SGC - Clube Limeirense 1951", layout="wide")

# --- 3. CABEÇALHO OFICIAL ---
st.markdown(f"""
    <div style="text-align: center; border: 4px solid #1b5e20; border-radius: 15px; padding: 15px; background-color: #f1f8e9;">
        <h1 style="margin: 0; color: #1b5e20;">Clube Columbófilo Limeirense</h1>
        <h3 style="margin: 0; color: #333;">Fundado em 1951</h3>
        <p style="font-weight: bold; color: #2e7d32;">SISTEMA DE GESTÃO - EVOLUÇÃO CONSTANTE</p>
    </div>
""", unsafe_allow_html=True)

# --- 4. MENU LATERAL ---
menu = st.sidebar.radio("PAINEL DE CONTROLE", [
    "⚙️ Configurar Prova", 
    "👤 Cadastro de Sócios", 
    "🐦 Cadastro de Pombos", 
    "🚀 Lançar Resultados (3+3)", 
    "✏️ Corrigir Histórico", 
    "📊 Apuramento Geral",
    "📑 Relatórios para Impressão"
])

modalidades = ["Filhotes", "Velocidade Adultos", "Meio Fundo Adultos", "Fundo Adultos", "Grande Fundo Adultos"]

# --- 5. CONFIGURAR PROVA ---
if menu == "⚙️ Configurar Prova":
    st.header("⚙️ Parâmetros da Solta")
    with st.container(border=True):
        m_sel = st.selectbox("Modalidade", modalidades)
        c1, c2 = st.columns(2)
        with c1:
            cid = st.text_input("Cidade da Solta")
            lat_s, lon_s = st.text_input("Lat (Solta)"), st.text_input("Lon (Solta)")
        with c2:
            p_ini = st.number_input("Pontos 1º Lugar", value=1000.0)
            p_dec = st.number_input("Decréscimo", value=1.0)
            st.write("Hora Solta")
            hs, ms, ss = st.columns(3)
            h_s = hs.number_input("H",0,23, key="h_solta")
            m_s = ms.number_input("M",0,59, key="m_solta")
            s_s = ss.number_input("S",0,59, key="s_solta")
    if st.button("💾 Salvar Configuração", use_container_width=True):
        st.session_state[f'conf_{m_sel}'] = {"cid":cid, "lat":lat_s, "lon":lon_s, "h":h_s, "m":m_s, "s":s_s, "p":p_ini, "d":p_dec}
        st.success("Configuração Salva!")

# --- 6. LANÇAMENTO (O BOTÃO QUE ESTAVA COM ERRO FOI REPARADO AQUI) ---
elif menu == "🚀 Lançar Resultados (3+3)":
    mod_v = st.selectbox("Modalidade Ativa", modalidades)
    if f'conf_{mod_v}' not in st.session_state:
        st.error("Configure a prova primeiro!")
    else:
        conf = st.session_state[f'conf_{mod_v}']
        s_sel = st.selectbox("Sócio", st.session_state['db_socios']['Nome'].unique())
        s_data = st.session_state['db_socios'][st.session_state['db_socios'].Nome == s_sel].iloc[0]
        dist = haversine(conf['lat'], conf['lon'], s_data.Lat, s_data.Lon)
        
        st.info(f"📍 Solta: {conf['cid']} | 📏 Distância: {dist/1000:.3f} km")

        chegadas = []
        for i in range(1, 7):
            tipo = "PONTUA" if i <= 3 else "EMPURRA"
            cor = "#E3F2FD" if i <= 3 else "#FFF3E0"
            with st.container(border=True):
                st.markdown(f"<div style='background-color:{cor}; padding:5px;'><strong>POMBO {i} - {tipo}</strong></div>", unsafe_allow_html=True)
                ca, ch, cm, cs = st.columns([2,1,1,1])
                lista_p = st.session_state['db_pombos'][st.session_state['db_pombos'].Dono == s_sel]['Anilha'].unique()
                a_sel = ca.selectbox(f"Anilha", lista_p if len(lista_p)>0 else ["Nenhum"], key=f"a_{mod_v}_{i}")
                hc = ch.number_input("H",0,23,key=f"h_{mod_v}_{i}")
                mc = cm.number_input("M",0,59,key=f"m_{mod_v}_{i}")
                sc = cs.number_input("S",0,59,key=f"s_{mod_v}_{i}")
                v = calc_vel(dist, conf['h'], conf['m'], conf['s'], hc, mc, sc)
                chegadas.append({"Modalidade": mod_v, "Sócio": s_sel, "Anilha": a_sel, "Velocidade": v, "Tipo": tipo})

        if st.button("🏆 GRAVAR NO HISTÓRICO", use_container_width=True):
            df_t = pd.DataFrame(chegadas).sort_values("Velocidade", ascending=False).reset_index(drop=True)
            for idx, r in df_t.iterrows():
                r['Pontos'] = max(0, conf['p'] - (idx * conf['d']))
                st.session_state['historico'] = pd.concat([st.session_state['historico'], pd.DataFrame([r])], ignore_index=True)
            st.success("✅ Gravado com sucesso!")

# --- 7. APURAMENTO (GERAL E MODALIDADES) ---
elif menu == "📊 Apuramento Geral":
    filtro = st.selectbox("Ver Classificação de:", ["GERAL ABSOLUTO"] + modalidades)
    t1, t2 = st.tabs(["👥 Sócios", "🕊️ Pombos"])
    df = st.session_state['historico']
    if not df.empty:
        df_v = df if filtro == "GERAL ABSOLUTO" else df[df.Modalidade == filtro]
        with t1:
            st.write(f"### Ranking Sócios - {filtro}")
            st.table(df_v[df_v.Tipo == 'PONTUA'].groupby('Sócio')['Pontos'].sum().sort_values(ascending=False))
        with t2:
            st.write(f"### Ranking Pombo Ás - {filtro}")
            st.table(df_v.groupby(['Anilha', 'Sócio'])['Pontos'].sum().sort_values(ascending=False))

# --- 8. CADASTROS E RELATÓRIOS (PRESERVADOS) ---
elif menu == "👤 Cadastro de Sócios":
    with st.form("fs"):
        n = st.text_input("Nome")
        la, lo = st.text_input("Lat"), st.text_input("Lon")
        if st.form_submit_button("Salvar"):
            st.session_state['db_socios'] = pd.concat([st.session_state['db_socios'], pd.DataFrame([{"Nome":n, "Lat":la, "Lon":lo}])], ignore_index=True)

elif menu == "🐦 Cadastro de Pombos":
    with st.form("fp"):
        ani = st.text_input("Anilha")
        dono = st.selectbox("Dono", st.session_state['db_socios']['Nome'].unique())
        if st.form_submit_button("Vincular"):
            st.session_state['db_pombos'] = pd.concat([st.session_state['db_pombos'], pd.DataFrame([{"Anilha":ani, "Dono":dono}])], ignore_index=True)

elif menu == "✏️ Corrigir Histórico":
    st.session_state['historico'] = st.data_editor(st.session_state['historico'], num_rows="dynamic")

elif menu == "📑 Relatórios para Impressão":
    if not st.session_state['historico'].empty:
        csv = st.session_state['historico'].to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Excel", csv, "relatorio.csv", "text/csv")
