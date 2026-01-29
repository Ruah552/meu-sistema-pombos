import streamlit as st
import pandas as pd
from math import radians, cos, sin, asin, sqrt
import io

# --- MOTOR DE CÁLCULO ---
def haversine(lat1, lon1, lat2, lon2):
    try:
        if not all([lat1, lon1, lat2, lon2]) or lat1 == "" or lat2 == "": return 0.0
        l1, n1, l2, n2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
        a = sin((l2-l1)/2)**2 + cos(l1) * cos(l2) * sin((n2-n1)/2)**2
        return (2 * asin(sqrt(a))) * 6371 * 1000 
    except: return 0.0

def calc_vel(dist_m, hs, ms, ss, hc, mc, sc):
    try:
        t_voo = ((hc*3600 + mc*60 + sc) - (hs*3600 + ms*60 + ss)) / 60
        return round(dist_m / t_voo, 3) if t_voo > 0 else 0.0
    except: return 0.0

# --- INICIALIZAÇÃO DE MEMÓRIA ---
for key in ['db_socios', 'db_pombos', 'historico']:
    if key not in st.session_state:
        if key == 'historico': st.session_state[key] = pd.DataFrame(columns=["Modalidade", "Sócio", "Anilha", "Velocidade", "Pontos", "Tipo"])
        elif key == 'db_socios': st.session_state[key] = pd.DataFrame(columns=["Nome", "Lat", "Lon"])
        else: st.session_state[key] = pd.DataFrame(columns=["Anilha", "Dono"])

st.set_page_config(page_title="SGC Limeirense 1951", layout="wide")

st.markdown("<h1 style='text-align: center; color: #1b5e20;'>🏛️ Clube Columbófilo Limeirense (1951)</h1>", unsafe_allow_html=True)

menu = st.sidebar.radio("MENU PRINCIPAL", ["⚙️ Prova", "👤 Sócios", "🐦 Pombos", "🚀 Lançar", "📊 Rankings", "✏️ Editar", "📑 Relatórios"])
mods = ["Filhotes", "Velocidade", "Meio Fundo", "Fundo", "G. Fundo"]

# --- 1. CONFIGURAÇÃO DA PROVA ---
if menu == "⚙️ Prova":
    with st.container(border=True):
        m = st.selectbox("Modalidade", mods)
        c1, c2 = st.columns(2)
        cid = c1.text_input("Local")
        la_s, lo_s = c1.text_input("Lat Solta"), c1.text_input("Lon Solta")
        p1, dec = c2.number_input("Pts 1º", 1000), c2.number_input("Perda", 1)
        h, mi, s = c2.columns(3)
        hs = h.number_input("H",0,23, key="h_s")
        ms = mi.number_input("M",0,59, key="m_s")
        ss = s.number_input("S",0,59, key="s_s")
    if st.button("💾 Salvar Configuração"):
        st.session_state[f'c_{m}'] = {"lat":la_s, "lon":lo_s, "h":hs, "m":ms, "s":ss, "p":p1, "d":dec}
        st.success("Salvo!")

# --- 2. CADASTROS ---
elif menu == "👤 Sócios":
    with st.form("f_s"):
        n, la, lo = st.text_input("Nome"), st.text_input("Lat"), st.text_input("Lon")
        if st.form_submit_button("Salvar Sócio"):
            st.session_state.db_socios = pd.concat([st.session_state.db_socios, pd.DataFrame([{"Nome":n,"Lat":la,"Lon":lo}])], ignore_index=True)

elif menu == "🐦 Pombos":
    if not st.session_state.db_socios.empty:
        with st.form("f_p"):
            ani = st.text_input("Anilha")
            dono = st.selectbox("Dono", st.session_state.db_socios['Nome'].unique())
            if st.form_submit_button("Arquivar"):
                st.session_state.db_pombos = pd.concat([st.session_state.db_pombos, pd.DataFrame([{"Anilha":ani,"Dono":dono}])], ignore_index=True)
    else: st.warning("Cadastre o sócio primeiro!")

# --- 3. LANÇAMENTO (3+3) ---
elif menu == "🚀 Lançar":
    m_v = st.selectbox("Modalidade", mods)
    if f'c_{m_v}' not in st.session_state: st.error("Configure a prova primeiro!")
    else:
        conf = st.session_state[f'c_{m_v}']
        socio = st.selectbox("Sócio", st.session_state.db_socios['Nome'].unique())
        pombos = st.session_state.db_pombos[st.session_state.db_pombos.Dono == socio]['Anilha'].tolist()
        
        if not pombos: st.warning("Este sócio não tem pombos arquivados!")
        else:
            s_data = st.session_state.db_socios[st.session_state.db_socios.Nome == socio].iloc[0]
            dist = haversine(conf['lat'], conf['lon'], s_data.Lat, s_data.Lon)
            st.info(f"Distância: {dist/1000:.3f} km")
            
            resultados = []
            for i in range(1, 7):
                tipo = "PONTUA" if i <= 3 else "EMPURRA"
                with st.container(border=True):
                    st.write(f"Pombo {i} - {tipo}")
                    c_a, c_h, c_m, c_s = st.columns([2,1,1,1])
                    a = c_a.selectbox("Anilha", pombos, key=f"a_{m_v}_{socio}_{i}")
                    hc = c_h.number_input("H",0,23, key=f"h_{m_v}_{socio}_{i}")
                    mc = c_m.number_input("M",0,59, key=f"m_{m_v}_{socio}_{i}")
                    sc = c_s.number_input("S",0,59, key=f"s_{m_v}_{socio}_{i}")
                    v = calc_vel(dist, conf['h'], conf['m'], conf['s'], hc, mc, sc)
                    resultados.append({"Modalidade":m_v, "Sócio":socio, "Anilha":a, "Velocidade":v, "Tipo":tipo})
            
            if st.button("🏆 GRAVAR RESULTADOS"):
                df_c = pd.DataFrame(resultados).sort_values("Velocidade", ascending=False).reset_index(drop=True)
                for idx, r in df_c.iterrows():
                    r['Pontos'] = max(0, conf['p'] - (idx * conf['d']))
                    st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([r])], ignore_index=True)
                st.success("Sucesso!")

# --- 4. EXIBIÇÃO E EXPORTAÇÃO ---
elif menu == "📊 Rankings":
    st.table(st.session_state.historico[st.session_state.historico.Tipo == 'PONTUA'].groupby('Sócio')['Pontos'].sum())

elif menu == "✏️ Editar":
    st.session_state.historico = st.data_editor(st.session_state.historico, num_rows="dynamic")

elif menu == "📑 Relatórios":
    buf = io.BytesIO()
    st.session_state.historico.to_excel(buf, index=False)
    st.download_button("📥 Baixar Excel", buf.getvalue(), "Resultados.xlsx")
