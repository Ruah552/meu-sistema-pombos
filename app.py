# --- 6. APURAMENTO (MODALIDADES E GERAL ABSOLUTO) ---
elif menu == "📊 Apuramento Geral e Modalidade":
    st.subheader("🏆 Classificações Oficiais - Limeirense 1951")
    
    # Filtro de visualização: Permite ver o campeonato específico ou a soma de tudo
    opcao_campeonato = st.selectbox(
        "Selecione o Ranking que deseja consultar:", 
        ["GERAL ABSOLUTO (Soma de Todas as Provas)"] + modalidades
    )
    
    tab_concorrentes, tab_pombo_as = st.tabs(["👥 CAMPEONATO DE SÓCIOS", "🕊️ CAMPEONATO POMBO ÁS"])
    
    df_mestre = st.session_state['historico']
    
    if not df_mestre.empty:
        # Lógica de Filtragem
        if "GERAL ABSOLUTO" not in opcao_campeonato:
            df_final = df_mestre[df_mestre['Modalidade'] == opcao_campeonato]
        else:
            df_final = df_mestre

        with tab_concorrentes:
            st.markdown(f"#### Ranking de Sócios/Pombais - {opcao_campeonato}")
            st.caption("Regra: Soma dos pontos apenas dos pombos designados (PONTUA).")
            # Agrupa por sócio e soma pontos dos pombos 'PONTUA'
            rank_s = df_final[df_final['Tipo'] == 'PONTUA'].groupby('Sócio')['Pontos'].sum().sort_values(ascending=False).reset_index()
            rank_s.index += 1
            st.table(rank_s)

        with tab_pombo_as:
            st.markdown(f"#### Ranking Individual de Pombos (Pombo Ás) - {opcao_campeonato}")
            st.caption("Regra: Soma da pontuação individual de cada anilha em todas as soltas.")
            # Agrupa por anilha e dono
            rank_p = df_final.groupby(['Anilha', 'Sócio'])['Pontos'].sum().sort_values(ascending=False).reset_index()
            rank_p.index += 1
            st.table(rank_p)
    else:
        st.info("ℹ️ O histórico está vazio. Realize os lançamentos nas provas para gerar o apuramento.")

# --- 7. RELATÓRIOS PARA IMPRESSÃO (EXCEL/PDF) ---
elif menu == "📑 Relatórios para Impressão":
    st.subheader("📑 Gerador de Mapas Oficiais")
    st.write("Aqui pode exportar os resultados consolidados para impressão e arquivo do clube.")
    
    if not st.session_state['historico'].empty:
        with st.container(border=True):
            st.write(f"**Clube Columbófilo Limeirense - Fundado em 1951**")
            st.write(f"Total de registos no histórico: {len(st.session_state['historico'])}")
            
            # Criar o ficheiro Excel em memória
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                # Folha 1: Histórico Completo
                st.session_state['historico'].to_excel(writer, index=False, sheet_name='Resultados_Gerais')
                
                # Folha 2: Resumo Sócios (Geral)
                resumo_s = st.session_state['historico'][st.session_state['historico']['Tipo'] == 'PONTUA'].groupby('Sócio')['Pontos'].sum().sort_values(ascending=False).reset_index()
                resumo_s.to_excel(writer, index=False, sheet_name='Ranking_Socios')
                
                # Folha 3: Resumo Pombos (Pombo Ás)
                resumo_p = st.session_state['historico'].groupby(['Anilha', 'Sócio'])['Pontos'].sum().sort_values(ascending=False).reset_index()
                resumo_p.to_excel(writer, index=False, sheet_name='Ranking_Pombo_As')

            st.download_button(
                label="📥 Descarregar Mapa de Classificação (Excel)",
                data=buffer.getvalue(),
                file_name="Classificacao_Limeirense_Oficial.xlsx",
                mime="application/vnd.ms-excel"
            )
            st.success("✅ Relatório gerado com sucesso! Pode abrir no Excel e imprimir como PDF.")
    else:
        st.warning("⚠️ Não existem dados no histórico para exportar.")
