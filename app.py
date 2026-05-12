import streamlit as st
from graph import contract_graph

# =============================================================================
# APP.PY  —  Interface Web do Comparador de Contratos
# =============================================================================
# Este arquivo contém a interface do usuário (UI) construída com Streamlit.
# Sua responsabilidade é:
#   1. Receber os arquivos dos contratos (upload)
#   2. Disparar o pipeline de processamento (contract_graph.invoke)
#   3. Exibir os resultados (diferenças + relatório + download PDF)
#
# NÃO contém regras de negócio complexas — apenas orquestração da UI.
# A lógica pesada (extração, comparação, IA, PDF) vive nos módulos
# extractors.py, comparator.py, graph.py e pdf_exporter.py.
# =============================================================================


st.set_page_config(
    page_title="Comparador de Contratos",
    page_icon="📄",
    layout="wide",
)

st.title("Comparador de Contratos")
st.caption("Faça upload de dois contratos (PDF ou DOCX) para identificar diferenças e gerar um relatório.")


# =============================================================================
# SEÇÃO DE UPLOAD
# =============================================================================
# Layout em duas colunas para upload simultâneo dos dois contratos.
# file_a = contrato original (baseline)
# file_b = contrato revisado (target)
# =============================================================================
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Contrato A — Original")
    file_a = st.file_uploader("Selecione o Contrato A", type=["pdf", "docx"], key="file_a")

with col_b:
    st.subheader("Contrato B — Revisado")
    file_b = st.file_uploader("Selecione o Contrato B", type=["pdf", "docx"], key="file_b")

st.divider()


# =============================================================================
# BOTÃO DE COMPARAÇÃO
# =============================================================================
# O botão só é habilitado quando ambos os arquivos foram enviados.
# Ao clicar, o grafo LangGraph é invocado com o estado inicial.
#
# O state_input contém:
#   - Os bytes brutos dos arquivos (para extração)
#   - Os nomes dos arquivos (para identificar o formato PDF/DOCX)
#   - Campos vazios para os resultados intermediários e finais
#
# O grafo executa sequencialmente:
#   extract_texts → compare_contracts → generate_report
# =============================================================================
if st.button("Comparar Contratos", type="primary", disabled=not (file_a and file_b)):
    with st.spinner("Processando... isso pode levar alguns minutos."):
        try:
            state_input = {
                "file_a_bytes": file_a.read(),
                "file_a_name": file_a.name,
                "file_b_bytes": file_b.read(),
                "file_b_name": file_b.name,
                "text_a": "",
                "text_b": "",
                "differences": [],
                "report_markdown": "",
                "report_pdf_bytes": b"",
            }

            result = contract_graph.invoke(state_input)

        except Exception as e:
            st.error(f"Erro durante o processamento: {e}")
            st.stop()

    # =============================================================================
    # EXIBIÇÃO DOS RESULTADOS
    # =============================================================================
    # Após a execução do grafo, extrai os resultados finais do estado.
    # Exibe:
    #   1. Resumo da contagem de diferenças
    #   2. Expander com detalhamento das diferenças (UI colorida)
    #   3. Relatório em Markdown (renderizado)
    #   4. Botão de download do PDF gerado
    # =============================================================================

    differences = result["differences"]
    report_markdown = result["report_markdown"]
    report_pdf_bytes = result["report_pdf_bytes"]

    st.success(f"Análise concluída. {len(differences)} diferença(s) encontrada(s).")

    # ---------------------------------------------------------------------------
    # Diferenças Determinísticas (expander fechado por padrão)
    # ---------------------------------------------------------------------------
    # Mostra as diferenças brutas detectadas pelo algoritmo de comparação,
    # sem intervenção do LLM. Útil para auditoria ou quando o usuário
    # quer ver exatamente o que mudou antes de ler a análise jurídica.
    #
    # Cores do Streamlit:
    #   - st.success (verde)   → conteúdo adicionado no Contrato B
    #   - st.error (vermelho)  → conteúdo removido do Contrato A
    #   - st.warning (laranja) → texto antes da modificação
    #   - st.info (azul)       → texto depois da modificação
    # ---------------------------------------------------------------------------
    with st.expander("Ver diferenças detectadas (análise determinística)", expanded=False):
        if not differences:
            st.info("Os contratos são idênticos — nenhuma diferença encontrada.")
        else:
            added = [d for d in differences if d["type"] == "added"]
            removed = [d for d in differences if d["type"] == "removed"]
            modified = [d for d in differences if d["type"] == "modified"]

            if added:
                st.markdown(f"**Adicionados no Contrato B:** {len(added)}")
                for d in added:
                    st.success(d["text_b"])

            if removed:
                st.markdown(f"**Removidos do Contrato A:** {len(removed)}")
                for d in removed:
                    st.error(d["text_a"])

            if modified:
                st.markdown(f"**Modificados:** {len(modified)}")
                for d in modified:
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**Antes (A):**")
                        st.warning(d["text_a"] or "—")
                    with c2:
                        st.markdown("**Depois (B):**")
                        st.info(d["text_b"] or "—")

    st.divider()
    st.subheader("Relatório Gerado")
    st.markdown(report_markdown)

    st.divider()
    st.download_button(
        label="Baixar Relatório em PDF",
        data=report_pdf_bytes,
        file_name="relatorio_comparativo.pdf",
        mime="application/pdf",
        type="primary",
    )

elif not (file_a and file_b):
    st.info("Faça upload dos dois contratos para habilitar a comparação.")
