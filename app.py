import streamlit as st
import pandas as pd
from math import radians, cos, sin, asin, sqrt
import io

# --- MOTOR DE CÁLCULO ---
def haversine(lat1, lon1, lat2, lon2):
    try:
        if not lat1 or not lat2: return 0.0
        l1, n1, l2, n2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
        a = sin((l2-l1)/2)**2 + cos(l1) * cos(l2) * sin((n2-n1)/2)**2
        return (2 * asin(sqrt(a))) * 6371 * 1000 
    except: return 0.0

def calc_vel(dist_m, hs, ms, ss, hc, mc, sc):
    try:
        t_voo = ((hc*3600 + mc*60 + sc) - (hs*3600 + ms*60 + ss)) / 60
        return round(dist_m / t_voo, 3) if t_voo > 0 else 0.0
    except: return 0.0

# --- MEMÓRIA DO SISTEMA (NÃO APAGA) ---
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
st.markdown("<h1 style='text-align: center; color: #1b5e20;'>Clube Columbófilo Limeirense (1951)</h1>", unsafe_allow_html=True)

menu = st.sidebar.radio("NAVEGAÇÃO", [
    "⚙️ Configurar Prova", 
    "👤 Sócios e Pombos", 
    "🚀 Lançar Resultados", 
    "📊 Apuramento Geral",
    "✏️ Editar Histórico",
    "📑 Relatórios"
])

modalidades = ["Filhotes", "Velocidade Adultos", "Meio Fundo Adultos", "Fundo Adultos", "Grande Fundo Adultos"]

# --- 1. CONFIGURAÇÃO ---
if menu == "⚙️ Configurar Prova":
    with st.container(border=True):
        m_sel = st.selectbox("Modalidade", modalidades)
        c1, c2 = st.columns(2)
        with c1:
            cid = st.text_input("Local", key="conf_cid")
            lat_s, lon_s = st.text_input("Lat Solta"), st.text_input("Lon Solta")
        with c2:
            p_ini = st.number_input("Pontos 1º Lugar", value=1000.0)
            p_dec = st.number_input("Decréscimo", value=1.0)
            st.write("Hora Solta")
            h, m, s = st.columns(3)
            hs = h.number_input("H",0,23)
            ms = m.number_input("M",0,59)
            ss = s.number_input("S",0,59)
    if st.button("💾 Salvar Configuração"):
        st.session_state[f'conf_{m_sel}'] = {"cid":cid, "lat":lat_s, "lon":lon_s, "h":hs, "m":ms, "s":ss, "p":p_ini, "d":p_dec}
        st.success("Configurada!")

# --- 2. CADASTROS ---
elif menu == "👤 Sócios e Pombos":
    col1, col2 = st.columns(2)
    with col1:
        with st.form("f_s"):
            n = st.text_input("Nome Sócio")
            la, lo = st.text_input("Lat"), st.text_input("Lon")
            if st.form_submit_button("Cadastrar Sócio"):
                st.session_state.db_socios = pd.concat([st.session_state.db_socios, pd.DataFrame([{"Nome":n, "Lat":la, "Lon":lo}])], ignore_index=True)
    with col2:
        if not st.session_state.db_socios.empty:
            with st.form("f_p"):
                ani = st.text_input("Anilha")
                dono = st.selectbox("Dono", st.session_state.db_socios['Nome'].unique())
                if st.form_submit_button("Arquivar Pombo"):
                    st.session_state.db_pombos = pd.concat([st.session_state.db_pombos, pd.DataFrame([{"Anilha":ani, "Dono":dono}])], ignore_index=True)

# --- 3. LANÇAMENTO (3+3) ---
elif menu == "🚀 Lançar Resultados":
    mod_v = st.selectbox("Modalidade", modalidades)
    if f'conf_{mod_v}' not in st.session_state: st.error("Configure a prova primeiro!")
    else:
        conf = st.session_state[f'conf_{mod_v}']
        s_sel = st.selectbox("Sócio", st.session_state.db_socios['Nome'].unique())
        pombos_dono = st.session_state.db_pombos[st.session_state.db_pombos.Dono == s_sel]['Anilha'].tolist()
        
        if pombos_dono:
            s_data = st.session_state.db_socios[st.session_state.db_socios.Nome == s_sel].iloc[0]
            dist = haversine(conf['lat'], conf['lon'], s_data.Lat, s_data.Lon)
            st.info(f"Distância: {dist/1000:.3f} km")
            
            resultados_temp = []
            for i in range(1, 7):
                tipo = "PONTUA" if i <= 3 else "EMPURRA"
                with st.container(border=True):
                    st.write(f"Pombo {i} - {tipo}")
                    ca, ch, cm, cs = st.columns([2,1,1,1])
                    # KEY ÚNICA PARA EVITAR ERRO
                    a_sel = ca.selectbox(f"Anilha", pombos_dono, key=f"sel_{mod_v}_{s_sel}_{i}")
                    hc = ch.number_input("H",0,23, key=f"h_{mod_v}_{s_sel}_{i}")
                    mc = cm.number_input("M",0,59, key=f"m_{mod_v}_{s_sel}_{i}")
                    sc = cs.number_input("S",0,59, key=f"s_{mod_v}_{s_sel}_{i}")
                    v = calc_vel(dist, conf['h'], conf['m'], conf['s'], hc, mc, sc)
                    resultados_temp.append({"Modalidade":mod_v, "Sócio":s_sel, "Anilha":a_sel, "Velocidade":v, "Tipo":tipo})
            
            if st.button("🏆 GRAVAR", key=f"btn_{mod_v}_{s_sel}"):
                df_c = pd.DataFrame(resultados_temp).sort_values("Velocidade", ascending=False).reset_index(drop=True)
                for idx, r in df_c.iterrows():
                    r['Pontos'] = max(0, conf['p'] - (idx * conf['d']))
                    st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([r])], ignore_index=True)
                st.success("Gravado!")

# --- 4. EDIÇÃO E RELATÓRIO ---
elif menu == "✏️ Editar Histórico":
    if not st.session_state.historico.empty:
        df_ed = st.data_editor(st.session_state.historico, num_rows="dynamic", key="editor_final")
        if st.button("💾 Salvar Alterações"):
            st.session_state.historico = df_ed
            st.success("Atualizado!")

elif menu == "📑 Relatórios":
    if not st.session_state.historico.empty:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            st.session_state.historico.to_excel(writer, index=False, sheet_name='Geral')
        st.download_button("📥 Baixar Relatório Excel", buffer.getvalue(), "Relatorio_Limeirense.xlsx")
