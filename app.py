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

# --- INICIALIZAÇÃO DE MEMÓRIA (NÃO APAGA NADA) ---
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
st.markdown(f"""
    <div style="text-align: center; border: 4px solid #1b5e20; border-radius: 15px; padding: 15px; background-color: #f1f8e9; margin-bottom: 20px;">
        <h1 style="margin: 0; color: #1b5e20;">Clube Columbófilo Limeirense</h1>
        <h3 style="margin: 0; color: #333;">Fundado em 1951</h3>
        <p style="font-weight: bold; color: #2e7d32;">SISTEMA DE GESTÃO - VERSÃO CORRIGIDA E ESTÁVEL</p>
    </div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("PAINEL DE CONTROLE", [
    "⚙️ Configurar Prova", 
    "👤 Cadastro de Sócios", 
    "🐦 Cadastro de Pombos", 
    "🚀 Lançar Resultados (3+3)", 
    "📊 Apuramento Geral",
    "✏️ Editar Histórico",
    "📑 Relatórios"
])

modalidades = ["Filhotes", "Velocidade Adultos", "Meio Fundo Adultos", "Fundo Adultos", "Grande Fundo Adultos"]

# --- 1. CONFIGURAR PROVA ---
if menu == "⚙️ Configurar Prova":
    st.subheader("⚙️ Configuração da Solta")
    with st.container(border=True):
        m_sel = st.selectbox("Modalidade", modalidades)
        c1, c2 = st.columns(2)
        with c1:
            cid = st.text_input("Local da Solta", key="cid_input")
            lat_s = st.text_input("Latitude Solta", key="lat_s_input")
            lon_s = st.text_input("Longitude Solta", key="lon_s_input")
        with c2:
            p_ini = st.number_input("Pontos 1º Lugar", value=1000.0, key="p_ini_input")
            p_dec = st.number_input("Decréscimo", value=1.0, key="p_dec_input")
            st.write("Hora Solta")
            h, m, s = st.columns(3)
            hs = h.number_input("H",0,23, key="hs_input")
            ms = m.number_input("M",0,59, key="ms_input")
            ss = s.number_input("S",0,59, key="ss_input")
    
    if st.button("💾 Gravar Configuração", use_container_width=True):
        st.session_state[f'conf_{m_sel}'] = {"cid":cid, "lat":lat_s, "lon":lon_s, "h":hs, "m":ms, "s":ss, "p":p_ini, "d":p_dec}
        st.success(f"Configuração para {m_sel} gravada!")

# --- 2. CADASTRO DE SÓCIOS E POMBOS (VÍNCULO GARANTIDO) ---
elif menu == "👤 Cadastro de Sócios":
    with st.form("f_socio", clear_on_submit=True):
        n = st.text_input("Nome do Pombal")
        la, lo = st.text_input("Latitude"), st.text_input("Longitude")
        if st.form_submit_button("Salvar Sócio"):
            st.session_state.db_socios = pd.concat([st.session_state.db_socios, pd.DataFrame([{"Nome":n, "Lat":la, "Lon":lo}])], ignore_index=True)
            st.success("Sócio Cadastrado!")

elif menu == "🐦 Cadastro de Pombos":
    if st.session_state.db_socios.empty:
        st.warning("Cadastre um sócio primeiro!")
    else:
        with st.form("f_pombo", clear_on_submit=True):
            ani = st.text_input("Número da Anilha")
            dono = st.selectbox("Dono", st.session_state.db_socios['Nome'].unique())
            if st.form_submit_button("Arquivar para o Dono"):
                st.session_state.db_pombos = pd.concat([st.session_state.db_pombos, pd.DataFrame([{"Anilha":ani, "Dono":dono}])], ignore_index=True)
                st.success(f"Pombo {ani} arquivado com sucesso!")

# --- 3. LANÇAMENTO (CORREÇÃO DOS BOTÕES) ---
elif menu == "🚀 Lançar Resultados (3+3)":
    mod_v = st.selectbox("Modalidade", modalidades)
    if f'conf_{mod_v}' not in st.session_state:
        st.error("Configure a prova primeiro!")
    else:
        conf = st.session_state[f'conf_{mod_v}']
        s_sel = st.selectbox("Sócio", st.session_state.db_socios['Nome'].unique())
        
        pombos_arquivados = st.session_state.db_pombos[st.session_state.db_pombos.Dono == s_sel]['Anilha'].tolist()
        
        if not pombos_arquivados:
            st.warning(f"Este sócio não tem pombos arquivados!")
        else:
            s_data = st.session_state.db_socios[st.session_state.db_socios.Nome == s_sel].iloc[0]
            dist = haversine(conf['lat'], conf['lon'], s_data.Lat, s_data.Lon)
            
            st.info(f"📏 Distância: {dist/1000:.3f} km")
            
            chegadas_temporarias = []
            for i in range(1, 7):
                tipo = "PONTUA" if i <= 3 else "EMPURRA"
                cor = "#D1E9F6" if i <= 3 else "#F6EACB"
                with st.container(border=True):
                    st.markdown(f"<div style='background-color:{cor}; padding:5px;'><strong>Pombo {i} - {tipo}</strong></div>", unsafe_allow_html=True)
                    c_a, c_h, c_m, c_s = st.columns([2,1,1,1])
                    a_sel = c_a.selectbox(f"Anilha {i}", pombos_arquivados, key=f"sel_{mod_v}_{s_sel}_{i}")
                    hc = c_h.number_input("H",0,23, key=f"h_{mod_v}_{s_sel}_{i}")
                    mc = c_m.number_input("M",0,59, key=f"m_{mod_v}_{s_sel}_{i}")
                    sc = c_s.number_input("S",0,59, key=f"s_{mod_v}_{s_sel}_{i}")
                    v = calc_vel(dist, conf['h'], conf['m'], conf['s'], hc, mc, sc)
                    chegadas_temporarias.append({"Modalidade": mod_v, "Sócio": s_sel, "Anilha": a_sel, "Velocidade": v, "Tipo": tipo})

            # BOTÃO DE GRAVAÇÃO COM CHAVE ÚNICA
            if st.button("🏆 GRAVAR RESULTADOS", key=f"btn_gravar_{mod_v}_{s_sel}", use_container_width=True):
                df_calc = pd.DataFrame(chegadas_temporarias).sort_values("Velocidade", ascending=False).reset_index(drop=True)
                for idx, r in df_calc.iterrows():
                    r['Pontos'] = max(0, conf['p'] - (idx * conf['d']))
                    st.session_state.historico = pd.concat([st.session_state.historico, pd.DataFrame([r])], ignore_index=True)
                st.balloons()
                st.success("Resultados arquivados!")

# --- 4. APURAMENTO ---
elif menu == "📊 Apuramento Geral":
    df = st.session_state.historico
    if df.empty:
        st.info("Nenhum dado lançado.")
    else:
        filtro = st.selectbox("Filtrar:", ["GERAL ABSOLUTO"] + modalidades)
        df_v = df if "GERAL" in filtro else df[df.Modalidade == filtro]
        
        t1, t2 = st.tabs(["👥 Sócios", "🕊️ Pombos Ás"])
        with t1:
            # SOMA SÓ DESIGNADOS
            st.table(df_v[df_v.Tipo == 'PONTUA'].groupby('Sócio')['Pontos'].sum().sort_values(ascending=False))
        with t2:
            # SOMA TUDO POR ANILHA
            st.table(df_v.groupby(['Anilha', 'Sócio'])['Pontos'].sum().sort_values(ascending=False))
