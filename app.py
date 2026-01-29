import streamlit as st

st.set_page_config(page_title="Teste Limeirense")

st.title("🏛️ Clube Limeirense 1951")
st.subheader("O sistema está ONLINE!")

st.balloons() # Isso vai soltar balões na tela se funcionar!

st.write("Se você está vendo isso, o terreno está limpo.")
st.write("Agora podemos colocar as fórmulas de pombos.")

nome = st.text_input("Digite seu nome para testar:")
if nome:
    st.write(f"Olá {nome}, o sistema está te ouvindo!")
