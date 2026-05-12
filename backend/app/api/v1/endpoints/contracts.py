"""Endpoints da API v1 — Contratos."""

import base64
from fastapi import APIRouter, UploadFile, File, HTTPException

from app.graph.contract_graph import contract_graph
from app.schemas.contracts import ContractCompareResponse

router = APIRouter()


@router.post("/compare", response_model=ContractCompareResponse)
async def compare_contracts(
    file_a: UploadFile = File(..., description="Contrato original (PDF ou DOCX)"),
    file_b: UploadFile = File(..., description="Contrato revisado (PDF ou DOCX)"),
):
    """
    Compara dois contratos e gera um relatorio juridico profissional.

    Recebe dois arquivos (PDF ou DOCX), extrai o texto, compara as diferencas
    e gera um relatorio via LLM. Retorna o relatorio em Markdown e PDF.
    """
    if not file_a or not file_b:
        raise HTTPException(status_code=400, detail="Ambos os arquivos sao obrigatorios.")

    try:
        state_input = {
            "file_a_bytes": await file_a.read(),
            "file_a_name": file_a.filename or "contrato_a",
            "file_b_bytes": await file_b.read(),
            "file_b_name": file_b.filename or "contrato_b",
            "text_a": "",
            "text_b": "",
            "differences": [],
            "report_markdown": "",
            "report_pdf_bytes": b"",
        }

        result = contract_graph.invoke(state_input)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {e}")

    return ContractCompareResponse(
        success=True,
        differences_count=len(result["differences"]),
        differences=result["differences"],
        report_markdown=result["report_markdown"],
        report_pdf_base64=base64.b64encode(result["report_pdf_bytes"]).decode("utf-8"),
    )
