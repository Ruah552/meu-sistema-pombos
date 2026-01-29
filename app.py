elif menu == "✏️ Editar Histórico":
    st.subheader("✏️ Editor do Livro de Provas")
    st.write("Ajuste qualquer dado diretamente na tabela abaixo. As alterações refletem instantaneamente nos rankings.")
    
    if not st.session_state['historico'].empty:
        # O data_editor permite editar como se fosse uma planilha Excel
        df_editado = st.data_editor(
            st.session_state['historico'],
            num_rows="dynamic", # Permite apagar linhas se necessário
            use_container_width=True,
            key="editor_historico"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Salvar Alterações e Recalcular Rankings", type="primary"):
                st.session_state['historico'] = df_editado
                st.success("✅ Histórico oficial atualizado e rankings recalculados!")
        with col2:
            st.info("💡 Dica: Para apagar uma linha, selecione-a e aperte 'Delete' no teclado.")
    else:
        st.warning("⚠️ O histórico está vazio. Não há dados para editar.")
