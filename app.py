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

# --- INICIALIZAÇÃO FIXA (NÃO APAGA) ---
if 'db_socios' not in st.session_state: st.session_state['db_socios'] = pd.DataFrame(columns=["Nome", "Lat", "Lon"])
if 'db_pombos' not in st.session_state: st.session_state['db_pombos'] = pd.DataFrame(columns=["Anilha", "Dono"])
if 'historico' not in st.session_state: st.session_state['historico'] = pd.DataFrame(columns=["Prova", "Modalidade", "Sócio", "Anilha", "Velocidade", "Pontos", "Tipo"])

st.set_page_config(page_title="SGC - Clube Limeirense 1951", layout="wide")

# --- CABEÇALHO ---
st.markdown(f"""
    <div style="text-align: center; border: 3px solid #1b5e20; border-radius: 15px; padding: 20px; background-color: #e8f5e9; margin-bottom: 25px;">
        <h1 style="margin: 0; color: #1b5e20; font-family: 'Arial';">Clube Columbófilo Limeirense</h1>
        <h3 style="margin: 0; color: #333;">Fundado em 1951</h3>
        <p style="margin: 10px 0 0 0; font-weight: bold; color: #666;">Sistema de Gestão de Provas e Campeonatos</p>
    </div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio("Navegação Principal", [
    "⚙️ Configurar Prova", 
    "👤 Cadastro de Sócios", 
    "🐦 Cadastro de Pombos", 
    "🚀 Lançar Chegadas (3+3)", 
    "✏️ Corrigir/Editar Provas", 
    "📊 Apuramento Geral e Modalidade",
    "📑 Relatórios para Impressão"
])

modalidades = ["Filhotes", "Velocidade Adultos", "Meio Fundo Adultos", "Fundo Adultos", "Grande Fundo Adultos"]

# --- 1. CONFIGURAR PROVA ---
if menu == "⚙️ Configurar Prova":
    st.subheader("⚙️ Parametrização da Solta e Pontuação")
    with st.container(border=True):
        m_sel = st.selectbox("Modalidade", modalidades)
        col1, col2 = st.columns(2)
        with col1:
            cid = st.text_input("Localidade da Solta")
            lat_s = st.text_input("Latitude Solta (GPS)")
            lon_s = st.text_input("Longitude Solta (GPS)")
        with col2:
            p_ini = st.number_input("Pontuação do 1º Lugar", value=100.0, step=1.0)
            p_dec = st.number_input("Decréscimo por Posição", value=1.0, step=0.1)
            st.write("Hora da Solta")
            h, m, s = st.columns(3)
            hs, ms, ss = h.number_input("HH",0,23), m.number_input("MM",0,59), s.number_input("SS",0,59)
            
    if st.button("💾 Salvar Configuração"):
        st.session_state[f'c_{m_sel}'] = {"cid": cid, "lat": lat_s, "lon": lon_s, "h": hs, "m": ms, "s": ss, "p": p_ini, "d": p_dec}
        st.success(f"Configuração para {m_sel} salva com sucesso!")

# --- 2. LANÇAMENTO (3+3) ---
elif menu == "🚀 Lançar Chegadas (3+3)":
    mod_at = st.selectbox("Selecione a Modalidade Ativa", modalidades)
    if f'c_{mod_at}' not in st.session_state:
        st.error("⚠️ Erro: Primeiro configure a prova no menu 'Configurar Prova'.")
    elif st.session_state['db_socios'].empty:
        st.warning("⚠️ Erro: Cadastre os Sócios antes de lançar chegadas.")
    else:
        conf = st.session_state[f'c_{mod_at}']
        s_sel = st.selectbox("Selecionar Sócio", st.session_state['db_socios']['Nome'].unique())
        dados_s = st.session_state['db_socios'][st.session_state['db_socios']['Nome'] == s_sel].iloc[0]
        dist = haversine(conf['lat'], conf['lon'], dados_s['Lat'], dados_s['Lon'])
        
        st.success(f"📍 Local: {conf['cid']} | 📏 Distância: {dist/1000:.3f} km")

        chegadas_input = []
        for i in range(1, 7):
            tipo = "PONTUA" if i <= 3 else "EMPURRA"
            cor = "#D1E9F6" if i <= 3 else "#F6EACB"
            with st.container(border=True):
                st.markdown(f"<div style='background-color:{cor}; padding:10px; border-radius:5px;'><strong>Pombo {i} - {tipo}</strong></div>", unsafe_allow_html=True)
                c_ani, c_h, c_m, c_s = st.columns([2, 1, 1, 1])
                
                # Filtra apenas pombos do sócio selecionado
                pombos_do_socio = st.session_state['db_pombos'][st.session_state['db_pombos']['Dono'] == s_sel]['Anilha'].unique()
                anilha_sel = c_ani.selectbox(f"Anilha {i}", pombos_do_socio if len(pombos_do_socio) > 0 else ["Sem Pombos"], key=f"sel_ani_{i}")
                
                hc = c_h.number_input("H", 0, 23, key=f"input_h_{i}")
                mc = c_m.number_input("M", 0, 59, key=f"input_m_{i}")
                sc = c_s.number_input("S", 0, 59, key=f"input_s_{i}")
                
                velocidade = calc_vel(dist, conf['h'], conf['m'], conf['s'], hc, mc, sc)
                chegadas_input.append({"Modalidade": mod_at, "Sócio": s_sel, "Anilha": anilha_sel, "Velocidade": velocidade, "Tipo": tipo})

        if st.button("🏆 Gravar e Calcular Pontuação"):
            df_temp = pd.DataFrame(chegadas_input).sort_values(by="Velocidade", ascending=False).reset_index(drop=True)
            # A Calculadora Financeira usa os ajustes que definiu
            for idx, row in df_temp.iterrows():
                row['Pontos'] = max(0, conf['p'] - (idx * conf['d']))
                st.session_state['historico'] = pd.concat([st.session_state['historico'], pd.DataFrame([row])], ignore_index=True)
            st.balloons()
            st.success("✅ Prova processada e gravada nas 10 provas do histórico!")

# --- 3. CADASTROS (REPARADOS) ---
elif menu == "👤 Cadastro de Sócios":
    st.subheader("👤 Registro de Novos Pombais")
    with st.form("form_socio", clear_on_submit=True):
        n = st.text_input("Nome do Sócio")
        la = st.text_input("Latitude Pombal")
        lo = st.text_input("Longitude Pombal")
        if st.form_submit_button("Confirmar Cadastro"):
            st.session_state['db_socios'] = pd.concat([st.session_state['db_socios'], pd.DataFrame([{"Nome": n, "Lat": la, "Lon": lo}])], ignore_index=True)
            st.rerun()

elif menu == "🐦 Cadastro de Pombos":
    st.subheader("🐦 Registro de Anilhas por Sócio")
    with st.form("form_pombo", clear_on_submit=True):
        ani = st.text_input("Número da Anilha")
        dono = st.selectbox("Proprietário", st.session_state['db_socios']['Nome'].unique())
        if st.form_submit_button("Vincular Anilha"):
            st.session_state['db_pombos'] = pd.concat([st.session_state['db_pombos'], pd.DataFrame([{"Anilha": ani, "Dono": dono}])], ignore_index=True)
            st.rerun()
