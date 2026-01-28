import streamlit as st

st.set_page_config(page_title="SGC - Gestão Columbófila")

st.title("🕊️ SGC - Sistema de Gestão")
st.write("O seu sistema está online e pronto para uso!")

# Sistema de Login Simples
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    senha = st.text_input("Palavra-passe:", type="password")
    if st.button("Entrar"):
        if senha == "1234":
            st.session_state.logado = True
            st.rerun()
        else:
            st.error("Senha incorreta!")
else:
    st.success("Bem-vindo ao SGC!")
    st.sidebar.title("Menu")
    opcao = st.sidebar.selectbox("Escolha uma opção:", ["Início", "Sócios", "Pombos", "Resultados"])
    st.write(f"Você selecionou: {opcao}")
