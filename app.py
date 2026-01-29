import streamlit as st
import pandas as pd
from math import radians, cos, sin, asin, sqrt
import io

# --- MOTOR DE CÁLCULO ---
def haversine(lat1, lon1, lat2, lon2):
    try:
        if not all([lat1, lon1, lat2, lon2]): return 0.0
        l1, n1, l2, n2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
        a = sin((l2-l1)/2)**2 + cos(l1) * cos(l2) * sin((n2-n1)/2)**2
        return (2 * asin(sqrt(a))) * 6371 * 1000 
    except: return 0.0

def calc_vel(dist_m, hs, ms, ss, hc, mc, sc):
    try:
        t_voo = ((hc*3600 + mc*60 + sc) - (hs*3600 + ms*60 + ss)) / 60
        return round(dist_m / t_voo, 3) if t_voo > 0 else 0.0
    except: return 0.0

# --- ESTADO DA SESSÃO ---
if 'db_socios' not in st.session_state: st.session_state.db_socios = pd.DataFrame(columns=["Nome", "Lat", "Lon"])
if 'db_pombos' not in st.session_state: st.session_state.db_pombos = pd.DataFrame(columns=["Anilha", "Dono"])
if 'historico' not in st.session_state: st.session_state.historico = pd.DataFrame(columns=["Modalidade", "Sócio", "Anilha", "Velocidade", "Pontos", "Tipo"])

st.set_page_config(page_title="SGC Limeirense", layout="wide")
st.title("🏛️ Clube Columbófilo Limeirense (1951)")

menu = st.sidebar.selectbox("MENU", ["Configurar Prova", "Sócios", "Pombos", "Lançar", "Rankings", "Editar", "Relatórios"])
mods = ["Filhotes", "Velocidade", "Meio Fundo", "Fundo", "G. Fundo"]

# --- TELAS ---
if menu == "Configurar Prova":
    m = st.selectbox("Modalidade", mods)
    c1, c2 = st.columns(2)
    la_s = c1.text_input("Lat Solta")
    lo_s = c1.text_input("Lon Solta")
    p1 = c2.number_input("Pontos 1º", 1000)
    dec = c2.number_input("Decréscimo", 1)
    hs = c2.number_input("Hora Solta", 0, 23)
    ms = c2.number_input("Min Solta", 0, 59)
    if st.button("Salvar Prova"):
        st.session_state[f'c_{m}'] = {"lat":la_s, "lon":lo_s, "h":hs, "m":ms, "p":p1, "d":dec}
        st.success("Prova Salva!")

elif menu == "Sócios":
    with st.form("f_socio"):
        n = st.text_input("Nome do Pombal")
        la, lo = st.text_input("Lat"), st.text_input("Lon")
        if st.form_submit_button("Salvar"):
            st.session_state.db_socios = pd.concat([st.session_state.db_socios, pd.DataFrame([{"Nome":n,"Lat":la,"Lon":lo}])], ignore_index=True)

elif menu == "Pombos":
    if not st.session_state.db_socios.empty:
        with st.form("f_pombo"):
            ani = st.text_input("Anilha")
            dono = st.selectbox("Dono", st.session_state.db_socios['Nome'].unique())
            if st.form_submit_button("Arquivar"):
                st.session_state.db_pombos = pd.concat([st.session_state.db_pombos, pd.DataFrame([{"Anilha":ani,"Dono":dono}])], ignore_index=True)
    else: st.warning("Cadastre o sócio primeiro.")

elif menu == "Lançar":
    m_v = st.selectbox("Prova", mods)
    if f'c_{m_v}' not in st.session_state: st.error("Configure a prova primeiro!")
    else:
        conf = st.session_state[f'c_{m_v}']
        socio = st.selectbox("Sócio", st.session_state.db_socios['Nome'].unique())
        pombos = st.session_state.db_pombos[st.session_state.db_pombos.Dono == socio]['Anilha'].tolist()
        if not pombos: st.warning("Este sócio não tem pombos arquivados!")
        else:
            s_d = st.session_state.db_socios[st.session_state.db_socios.Nome == socio].iloc[0]
            dist = haversine(conf['lat'], conf['lon'], s_d.Lat, s_d.Lon)
            res_temp = []
            for i in range(1, 7):
                t = "PONTUA" if i <= 3 else "EMPURRA"
                with st.container(border=True):
                    c_a, c_h, c_m = st.columns([2,1,1])
                    ani = c_a.selectbox(f"Anilha {i}", pombos, key=f"a{m_v}{socio}{i}")
                    hc = c_h.number_input("H",0,23, key=f"h{m_v}{socio}{i}")
                    mc = c_m.number_input("M",0,59, key=f"m{m_v}{socio}{i}")
                    v = calc_vel(dist, conf['h'], conf['m'], 0, hc, mc, 0)
                    res_temp.append({"Modalidade":m_v,"Sócio":socio,"Anilha":ani,"Velocidade":v, "Tipo":t})
            if st.button("GRAVAR"):
                df_c = pd.DataFrame(res_temp).sort_values("Velocidade", ascending=False).reset_index(drop=True)
                for idx, r in df_c.iterrows():
                    r['Pontos'] = max(0, conf['p'] - (idx * conf['d']))
                    st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([r])], ignore_index=True)
                st.success("Gravado!")

elif menu == "Rankings":
    st.dataframe(st.session_state.historico)

elif menu == "Editar":
    st.session_state.historico = st.data_editor(st.session_state.historico, num_rows="dynamic")

elif menu == "Relatórios":
    if not st.session_state.historico.empty:
        csv = st.session_state.historico.to_csv(index=False).encode('utf-8')
        st.download_button("Baixar CSV (Abre no Excel)", csv, "resultados.csv", "text/csv")
