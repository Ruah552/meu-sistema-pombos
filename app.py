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

# --- INICIALIZAÇÃO DE MEMÓRIA ---
for key in ['db_socios', 'db_pombos', 'historico']:
    if key not in st.session_state:
        if key == 'historico': st.session_state[key] = pd.DataFrame(columns=["Modalidade", "Sócio", "Anilha", "Velocidade", "Pontos", "Tipo"])
        elif key == 'db_socios': st.session_state[key] = pd.DataFrame(columns=["Nome", "Lat", "Lon"])
        else: st.session_state[key] = pd.DataFrame(columns=["Anilha", "Dono"])

st.set_page_config(page_title="SGC Limeirense", layout="wide")
st.title("🏛️ Clube Columbófilo Limeirense (1951)")

menu = st.sidebar.radio("MENU", ["⚙️ Configurar Prova", "👤 Sócios", "🐦 Pombos", "🚀 Lançar Resultados", "📊 Rankings", "✏️ Editar", "📑 Relatórios"])
mods = ["Filhotes", "Velocidade", "Meio Fundo", "Fundo", "G. Fundo"]

# --- TELAS ---
if menu == "⚙️ Configurar Prova":
    m = st.selectbox("Modalidade", mods)
    with st.container(border=True):
        c1, c2 = st.columns(2)
        la_s = c1.text_input("Lat Solta", key="ls")
        lo_s = c1.text_input("Lon Solta", key="os")
        p1 = c2.number_input("Pontos 1º", 1000)
        dec = c2.number_input("Decréscimo", 1)
        h, mi, s = c2.columns(3)
        hs = h.number_input("H", 0, 23, key="h_s")
        ms = mi.number_input("M", 0, 59, key="m_s")
        ss = s.number_input("S", 0, 59, key="s_s")
    if st.button("Salvar Prova"):
        st.session_state[f'c_{m}'] = {"lat":la_s, "lon":lo_s, "h":hs, "m":ms, "s":ss, "p":p1, "d":dec}
        st.success(f"Prova de {m} salva!")

elif menu == "👤 Sócios":
    with st.form("fs", clear_on_submit=True):
        n = st.text_input("Nome")
        la = st.text_input("Lat")
        lo = st.text_input("Lon")
        if st.form_submit_button("Salvar Sócio"):
            st.session_state.db_socios = pd.concat([st.session_state.db_socios, pd.DataFrame([{"Nome":n,"Lat":la,"Lon":lo}])], ignore_index=True)
            st.success("Sócio Cadastrado!")

elif menu == "🐦 Pombos":
    if not st.session_state.db_socios.empty:
        with st.form("fp", clear_on_submit=True):
            ani = st.text_input("Anilha")
            dono = st.selectbox("Dono", st.session_state.db_socios['Nome'].unique())
            if st.form_submit_button("Vincular ao Dono"):
                st.session_state.db_pombos = pd.concat([st.session_state.db_pombos, pd.DataFrame([{"Anilha":ani,"Dono":dono}])], ignore_index=True)
                st.success(f"Pombo {ani} arquivado para {dono}!")
    else: st.warning("Cadastre o sócio antes.")

elif menu == "🚀 Lançar Resultados":
    m_v = st.selectbox("Escolha a Prova", mods)
    if f'c_{m_v}' not in st.session_state: st.error("Configure a prova primeiro!")
    elif st.session_state.db_socios.empty: st.warning("Cadastre os sócios!")
    else:
        conf = st.session_state[f'c_{m_v}']
        socio = st.selectbox("Sócio", st.session_state.db_socios['Nome'].unique())
        pombos = st.session_state.db_pombos[st.session_state.db_pombos.Dono == socio]['Anilha'].tolist()
        if not pombos: st.warning("Este sócio não tem pombos cadastrados.")
        else:
            s_d = st.session_state.db_socios[st.session_state.db_socios.Nome == socio].iloc[0]
            dist = haversine(conf['lat'], conf['lon'], s_d.Lat, s_d.Lon)
            res_temp = []
            for i in range(1, 7):
                t = "PONTUA" if i <= 3 else "EMPURRA"
                with st.container(border=True):
                    c_a, c_h, c_m, c_s = st.columns([2,1,1,1])
                    a = c_a.selectbox(f"Anilha {i}", pombos, key=f"a{m_v}{socio}{i}")
                    hc = c_h.number_input("H",0,23, key=f"h{m_v}{socio}{i}")
                    mc = c_m.number_input("M",0,59, key=f"m{m_v}{socio}{i}")
                    sc = c_s.number_input("S",0,59, key=f"s{m_v}{socio}{i}")
                    v = calc_vel(dist, conf['h'], conf['m'], conf['s'], hc, mc, sc)
                    res_temp.append({"Modalidade":m_v,"Sócio":socio,"Anilha":a,"Velocidade":v, "Tipo":t})
            if st.button("GRAVAR RESULTADOS", key=f"btn_{m_v}_{socio}"):
                df_c = pd.DataFrame(res_temp).sort_values("Velocidade", ascending=False).reset_index(drop=True)
                for idx, r in df_c.iterrows():
                    r['Pontos'] = max(0, conf['p'] - (idx * conf['d']))
                    st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([r])], ignore_index=True)
                st.success("Dados Gravados!")

elif menu == "📊 Rankings":
    if not st.session_state.historico.empty:
        st.write("### Campeonato de Sócios (Pontuados)")
        rank = st.session_state.historico[st.session_state.historico.Tipo == 'PONTUA'].groupby('Sócio')['Pontos'].sum().sort_values(ascending=False)
        st.dataframe(rank)
    else: st.info("Sem dados para mostrar.")

elif menu == "✏️ Editar":
    st.session_state.historico = st.data_editor(st.session_state.historico, num_rows="dynamic", key="ed")

elif menu == "📑 Relatórios":
    if not st.session_state.historico.empty:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine='xlsxwriter') as writer:
            st.session_state.historico.to_excel(writer, index=False)
        st.download_button("📥 Baixar Relatório Excel", buf.getvalue(), "Resultados.xlsx", key="dl")
