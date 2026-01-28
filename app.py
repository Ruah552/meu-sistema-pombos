import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from math import radians, cos, sin, asin, sqrt

# Configuração da Página
st.set_page_config(page_title="SGC - Gestão Columbófila", layout="wide")

# --- MATEMÁTICA DE PRECISÃO ---
def calcular_distancia(lat1, lon1, lat2, lon2):
    try:
        lon1, lat1, lon2, lat2 = map(radians, [float(lon1), float(lat1), float(lon2), float(lat2)])
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        return c * 6371 * 1000 # Distância exata em METROS
    except:
        return 0

def calcular_velocidade(distancia_m, h_s, m_s, s_s, h_c, m_c, s_c):
    try:
        segundos_solta = h_s * 3600 + m_s * 60 + s_s
        segundos_chegada = h_c * 3600 + m_c * 60 + s_c
        tempo_voo_min = (segundos_chegada - segundos_solta) / 60
        if tempo_voo_min > 0:
            return round(distancia_m / tempo_voo_min, 3)
        return 0
    except:
        return 0

# --- CONEXÃO ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    pass

st.title("🕊️ SGC - Sistema de Gestão Columbófila")

# Menu Lateral
menu = st.sidebar.radio("Navegação", [
    "⚙️ Parametrizar Prova", 
    "👤 Cadastro de Sócios", 
    "🚀 Lançar Chegadas (Regra 3+3)", 
    "📊 Classificação Final"
])

# 1. PARAMETRIZAR PROVA
if menu == "⚙️ Parametrizar Prova":
    st.header("⚙️ Configuração da Solta")
    col1, col2 = st.columns(2)
    with col1:
        cidade = st.text_input("Cidade da Solta", placeholder="Ex: Valência")
        st.write("**Coordenadas da Solta (GPS)**")
        lat_s = st.text_input("Latitude Solta", "39.4697")
        lon_s = st.text_input("Longitude Solta", "-0.3773")
    with col2:
        st.write("**Horário da Solta**")
        c1, c2, c3 = st.columns(3)
        h_solta = c1.number_input("Hora", 0, 23, 7)
        m_solta = c2.number_input("Min", 0, 59, 30)
        s_solta = c3.number_input("Seg", 0, 59, 0)
        st.write("---")
        p_ini = st.number_input("Pontos 1º Lugar", value=100.0)
        dec = st.number_input("Decréscimo (Livre)", value=1.0, step=0.1)

    if st.button("💾 Bloquear Configuração da Prova"):
        st.session_state['prova'] = {
            "cidade": cidade, "lat": lat_s, "lon": lon_s,
            "h": h_solta, "m": m_solta, "s": s_solta,
            "p_ini": p_ini, "dec": dec
        }
        st.success(f"Prova de {cidade} configurada e pronta para cálculos!")

# 2. CADASTRO DE SÓCIOS
elif menu == "👤 Cadastro de Sócios":
    st.header("👤 Cadastro de Pombais")
    with st.form("form_socio"):
        nome_s = st.text_input("Nome do Sócio")
        lat_p = st.text_input("Latitude do Pombal (Ex: 39.123456)")
        lon_p = st.text_input("Longitude do Pombal (Ex: -8.123456)")
        if st.form_submit_button("Gravar Sócio"):
            st.success(f"Sócio {nome_s} gravado no sistema.")

# 3. LANÇAR CHEGADAS (3+3)
elif menu == "🚀 Lançar Chegadas (3+3)":
    if 'prova' not in st.session_state:
        st.warning("⚠️ Primeiro configure a prova no menu lateral!")
    else:
        p = st.session_state['prova']
        st.header(f"🚀 Lançamento: {p['cidade']}")
        socio_nome = st.text_input("Sócio a Classificar")
        lat_socio = st.text_input("Lat. deste Pombal (para cálculo real)", "39.0000")
        lon_socio = st.text_input("Lon. deste Pombal", "-8.0000")
        
        dist_m = calcular_distancia(p['lat'], p['lon'], lat_socio, lon_socio)
        st.info(f"Distância calculada: {dist_m/1000:.3f} km")

        chegadas = []
        for i in range(1, 7):
            tipo = "PONTUA" if i <= 3 else "EMPURRA"
            cor = "blue" if i <= 3 else "orange"
            st.markdown(f"---")
            st.markdown(f"**Pombo {i} - :{cor}[{tipo}]**")
            c_ani, c_h, c_m, c_s = st.columns([2, 1, 1, 1])
            with c_ani:
                ani = st.text_input(f"Anilha/Ano", placeholder="0000000/26", key=f"ani_{i}")
            with c_h: hc = st.number_input("HH", 0, 23, key=f"h_{i}")
            with c_m: mc = st.number_input("MM", 0, 59, key=f"m_{i}")
            with c_s: sc = st.number_input("SS", 0, 59, key=f"s_{i}")
            
            vel = calcular_velocidade(dist_m, p['h'], p['m'], p['s'], hc, mc, sc)
            chegadas.append({"Anilha": ani, "Velocidade": vel, "Tipo": tipo})

        if st.button("🏆 Gerar Classificação da Série"):
            df = pd.DataFrame(chegadas)
            st.table(df)

# 4. CLASSIFICAÇÃO FINAL
elif menu == "📊 Classificação Final":
    if 'prova' in st.session_state:
        p = st.session_state['prova']
        st.header(f"📊 Tabela Oficial - {p['cidade']}")
        st.write(f"Solta: {p['h']}:{p['m']}:{p['s']} | Regra: -{p['dec']} pts/lugar")
        st.info("As velocidades calculadas com 3 casas decimais aparecerão aqui.")
    else:
        st.warning("Aguardando parametrização.")
