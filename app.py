import streamlit as st
import pandas as pd
from math import radians, cos, sin, asin, sqrt

# --- MOTOR MATEMÁTICO (FÓRMULAS FCI) ---
def haversine(lat1, lon1, lat2, lon2):
    try:
        lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
        a = sin((lat2-lat1)/2)**2 + cos(lat1) * cos(lat2) * sin((lon2-lon1)/2)**2
        return (2 * asin(sqrt(a))) * 6371 * 1000 # Metros
    except: return 0.0

def calc_vel(dist_m, hs, ms, ss, hc, mc, sc):
    try:
        t_voo = ((hc*3600 + mc*60 + sc) - (hs*3600 + ms*60 + ss)) / 60
        return round(dist_m / t_voo, 3) if t_voo > 0 else 0.0
    except: return 0.0

# --- PERSISTÊNCIA DE DADOS ---
if 'db_socios' not in st.session_state: st.session_state['db_socios'] = pd.DataFrame(columns=["Nome", "Lat", "Lon"])
if 'db_pombos' not in st.session_state: st.session_state['db_pombos'] = pd.DataFrame(columns=["Anilha", "Dono"])
if 'historico' not in st.session_state: 
    st.session_state['historico'] = pd.DataFrame(columns=["Prova", "Modalidade", "Sócio", "Anilha", "Velocidade", "Pontos", "Tipo"])

st.set_page_config(page_title="SGC Master", layout="wide")
st.title("🕊️ SGC - Sistema de Gestão Columbófila")

# --- MENU LATERAL ---
menu = st.sidebar.radio("Navegação", [
    "⚙️ Configurar Prova", 
    "👤 Cadastro de Sócios", 
    "🐦 Cadastro de Pombos", 
    "🚀 Lançar Chegadas (3+3)", 
    "✏️ Corrigir/Editar Provas", 
    "📊 Apuramento (Modalidade e Geral)",
    "📑 Relatórios PDF/Excel"
])

modalidades = ["Filhotes", "Velocidade Adultos", "Meio Fundo Adultos", "Fundo Adultos", "Grande Fundo Adultos"]

# 1 & 2. CADASTROS (MANTIDOS)
if menu == "👤 Cadastro de Sócios":
    st.header("👤 Cadastro de Pombais")
    with st.form("cad_socio"):
        n = st.text_input("Nome do Sócio")
        la, lo = st.text_input("Latitude"), st.text_input("Longitude")
        if st.form_submit_button("Salvar"):
            st.session_state['db_socios'] = pd.concat([st.session_state['db_socios'], pd.DataFrame([{"Nome": n, "Lat": la, "Lon": lo}])], ignore_index=True)

elif menu == "🐦 Cadastro de Pombos":
    st.header("🐦 Cadastro de Anilhas")
    with st.form("cad_pombo"):
        ani = st.text_input("Anilha (milhão/ano)")
        dono = st.selectbox("Sócio", st.session_state['db_socios']['Nome'].unique() if not st.session_state['db_socios'].empty else [""])
        if st.form_submit_button("Vincular"):
            st.session_state['db_pombos'] = pd.concat([st.session_state['db_pombos'], pd.DataFrame([{"Anilha": ani, "Dono": dono}])], ignore_index=True)

# 3. CONFIGURAR PROVA
elif menu == "⚙️ Configurar Prova":
    st.header("⚙️ Parametrizar Solta")
    m_sel = st.selectbox("Modalidade", modalidades)
    col1, col2 = st.columns(2)
    with col1:
        cid = st.text_input("Cidade"); lat_s = st.text_input("Lat Solta"); lon_s = st.text_input("Lon Solta")
    with col2:
        h, m, s = st.columns(3)
        hs, ms, ss = h.number_input("H",0,23), m.number_input("M",0,59), s.number_input("S",0,59)
        p_ini, dec = st.number_input("Pontos 1º", value=100.0), st.number_input("Decréscimo", value=1.0)
    if st.button("Gravar Configuração"):
        st.session_state[f'c_{m_sel}'] = {"cid": cid, "lat": lat_s, "lon": lon_s, "h": hs, "m": ms, "s": ss, "p": p_ini, "d": dec}
        st.success("Configuração gravada!")

# 4. LANÇAR COM CÁLCULO FINANCEIRO AUTOMÁTICO
elif menu == "🚀 Lançar Chegadas (3+3)":
    mod_at = st.selectbox("Modalidade", modalidades)
    if f'c_{mod_at}' not in st.session_state:
        st.error("Configure a prova primeiro!")
    else:
        conf = st.session_state[f'c_{mod_at}']
        n_prova = st.number_input("Prova Nº", 1, 10)
        s_sel = st.selectbox("Sócio", st.session_state['db_socios']['Nome'].unique())
        dados_s = st.session_state['db_socios'][st.session_state['db_socios']['Nome'] == s_sel].iloc[0]
        dist = haversine(conf['lat'], conf['lon'], dados_s['Lat'], dados_s['Lon'])
        
        st.info(f"Distância: {dist/1000:.3f} km")
        
        chegadas_temp = []
        for i in range(1, 7):
            tipo = "PONTUA" if i <= 3 else "EMPURRA"
            st.markdown(f"**Pombo {i} ({tipo})**")
            c_ani, c_h, c_m, c_s = st.columns([2, 1, 1, 1])
            anilha = c_ani.selectbox(f"Anilha {i}", st.session_state['db_pombos'][st.session_state['db_pombos']['Dono'] == s_sel]['Anilha'].unique(), key=f"ani_{i}")
            h_c, m_c, s_c = c_h.number_input("H",0,23,key=f"h{i}"), c_m.number_input("M",0,59,key=f"m{i}"), c_s.number_input("S",0,59,key=f"s{i}")
            vel = calc_vel(dist, conf['h'], conf['m'], conf['s'], h_c, m_c, s_c)
            chegadas_temp.append({"Prova": n_prova, "Modalidade": mod_at, "Sócio": s_sel, "Anilha": anilha, "Velocidade": vel, "Tipo": tipo})

        if st.button("🏆 Gravar Chegadas no Histórico"):
            # Lógica para atribuir pontos baseada na velocidade aqui (Calculadora Financeira)
            df_novos = pd.DataFrame(chegadas_temp).sort_values(by="Velocidade", ascending=False)
            for index, row in df_novos.iterrows():
                row['Pontos'] = conf['p'] - (index * conf['d']) # Aplica decréscimo
                st.session_state['historico'] = pd.concat([st.session_state['historico'], pd.DataFrame([row])], ignore_index=True)
            st.success("Prova gravada e pontos calculados!")

# 5, 6 & 7. APURAMENTO E RELATÓRIOS (DUPLO RANKING)
elif menu == "📊 Apuramento (Modalidade e Geral)":
    st.header("🏆 Classificações")
    opcao = st.selectbox("Ver:", ["GERAL ABSOLUTO"] + modalidades)
    tab_s, tab_p = st.tabs(["👥 SÓCIOS", "🕊️ POMBOS"])
    
    df = st.session_state['historico']
    if not df.empty:
        if opcao != "GERAL ABSOLUTO": df = df[df['Modalidade'] == opcao]
        with tab_s:
            st.table(df[df['Tipo'] == 'PONTUA'].groupby('Sócio')['Pontos'].sum().sort_values(ascending=False))
        with tab_p:
            st.table(df.groupby(['Anilha', 'Sócio'])['Pontos'].sum().sort_values(ascending=False))
