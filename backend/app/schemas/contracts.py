"""Schemas — Modelos Pydantic para request/response da API."""

from pydantic import BaseModel


class ContractCompareRequest(BaseModel):
    """Request vazio (upload e via multipart/form-data, nao JSON body)."""
    pass


class DifferenceItem(BaseModel):
    type: str
    text_a: str
    text_b: str


class ContractCompareResponse(BaseModel):
    success: bool
    differences_count: int
    differences: list[DifferenceItem]
    report_markdown: str
    report_pdf_base64: str


class HealthResponse(BaseModel):
    status: str
    model: str
