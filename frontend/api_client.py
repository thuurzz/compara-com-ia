"""API Client — Cliente HTTP para consumir o backend FastAPI."""

import base64
import requests

BACKEND_URL = "http://localhost:8000"


def compare_contracts(file_a_bytes: bytes, file_a_name: str, file_b_bytes: bytes, file_b_name: str) -> dict:
    """
    Envia dois contratos para o backend e retorna o resultado da comparacao.

    Args:
        file_a_bytes: bytes do contrato original
        file_a_name: nome do arquivo do contrato original
        file_b_bytes: bytes do contrato revisado
        file_b_name: nome do arquivo do contrato revisado

    Returns:
        dict com chaves: success, differences_count, differences,
                         report_markdown, report_pdf_base64
    """
    url = f"{BACKEND_URL}/api/v1/contracts/compare"

    files = {
        "file_a": (file_a_name, file_a_bytes, "application/octet-stream"),
        "file_b": (file_b_name, file_b_bytes, "application/octet-stream"),
    }

    response = requests.post(url, files=files, timeout=300)
    response.raise_for_status()
    return response.json()
