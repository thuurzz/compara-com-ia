import streamlit as st
from api_client import compare_contracts

st.set_page_config(
    page_title="Comparador de Contratos",
    page_icon="📄",
    layout="wide",
)

st.title("Comparador de Contratos")
st.caption("Faça upload de dois contratos (PDF ou DOCX) para identificar diferenças e gerar um relatório.")

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Contrato A — Original")
    file_a = st.file_uploader("Selecione o Contrato A", type=["pdf", "docx"], key="file_a")

with col_b:
    st.subheader("Contrato B — Revisado")
    file_b = st.file_uploader("Selecione o Contrato B", type=["pdf", "docx"], key="file_b")

st.divider()

if st.button("Comparar Contratos", type="primary", disabled=not (file_a and file_b)):
    with st.spinner("Processando... isso pode levar alguns minutos."):
        try:
            result = compare_contracts(
                file_a_bytes=file_a.read(),
                file_a_name=file_a.name,
                file_b_bytes=file_b.read(),
                file_b_name=file_b.name,
            )
        except Exception as e:
            st.error(f"Erro durante o processamento: {e}")
            st.stop()

    differences = result["differences"]
    report_markdown = result["report_markdown"]
    report_pdf_base64 = result["report_pdf_base64"]

    st.success(f"Análise concluída. {result['differences_count']} diferença(s) encontrada(s).")

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
        data=base64.b64decode(report_pdf_base64),
        file_name="relatorio_comparativo.pdf",
        mime="application/pdf",
        type="primary",
    )

elif not (file_a and file_b):
    st.info("Faça upload dos dois contratos para habilitar a comparação.")
