"""
config.py — Centralizacao de Configuracoes da Aplicacao
=======================================================

Este modulo isola TODAS as variaveis de configuracao da aplicacao,
sejam elas vindas de variaveis de ambiente (os.environ) ou de um
arquivo .env (via python-dotenv).

Principios aplicados:
- Single source of truth: uma unica porta de entrada para configs
- Fail fast: validacoes sao feitas no carregamento, nao no meio da execucao
- Valores padrao explicitos: sempre que fizer sentido, definimos fallback
- Leitura facil: qualquer arquivo que precise de config importa deste modulo

Exemplo de uso:
    from config import LLM_MODEL, PDF_MARGIN_LEFT

Exemplo de arquivo .env:
    LLM_BASE_URL=http://localhost:4000
    LLM_API_KEY=sk-xxx
    LLM_MODEL=ollama/llama3.1:8b
"""

import os
from dotenv import load_dotenv

# Carrega variaveis de ambiente de um arquivo .env (se existir).
# load_dotenv() e seguro para chamar multiplas vezes — ele nao sobrescreve
# variaveis ja definidas no ambiente, respeitando a hierarquia:
#   os.environ > .env > valores padrao deste arquivo
load_dotenv()


# =============================================================================
# SECAO 1: CONFIGURACOES DO MODELO DE LINGUAGEM (LLM)
# =============================================================================

LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "http://localhost:4000")
"""URL base do endpoint OpenAI-compatible.
Padrao aponta para LiteLLM Proxy rodando localmente na porta 4000.
Para OpenAI oficial, deixe vazio ou configure como https://api.openai.com/v1."""

LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
"""Chave de API do provedor. Alguns proxies locais (como LiteLLM) aceitam
qualquer string, entao o fallback e uma string vazia que sera tratada
como 'not-needed' no momento de instanciar o cliente."""

LLM_MODEL: str = os.getenv("LLM_MODEL", "ollama/llama3.1:8b")
"""Identificador do modelo no provedor.
Exemplos:
  - LiteLLM + Ollama:  ollama/llama3.1:8b
  - OpenRouter:        openai/gpt-4o-mini
  - Groq:              groq/llama-3.1-8b-instant
  - OpenAI oficial:    gpt-4o-mini"""

LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))
"""Temperatura da amostragem. 0 = deterministico/maximo de precisao.
Valores maiores geram respostas mais criativas (e imprevisiveis).
Para analise juridica, recomenda-se manter em 0."""


# =============================================================================
# SECAO 2: CONFIGURACOES DO PDF (WeasyPrint)
# =============================================================================

PDF_PAGE_SIZE: str = os.getenv("PDF_PAGE_SIZE", "A4")
"""Formato de pagina do relatorio. Valores aceitos por WeasyPrint:
A4, Letter, Legal, A3, A5, etc."""

PDF_MARGIN_TOP_CM: float = float(os.getenv("PDF_MARGIN_TOP_CM", "2.5"))
PDF_MARGIN_RIGHT_CM: float = float(os.getenv("PDF_MARGIN_RIGHT_CM", "2.0"))
PDF_MARGIN_BOTTOM_CM: float = float(os.getenv("PDF_MARGIN_BOTTOM_CM", "2.5"))
PDF_MARGIN_LEFT_CM: float = float(os.getenv("PDF_MARGIN_LEFT_CM", "2.0"))
"""Margens do documento PDF, em centimetros.
Formato: (topo, direita, baixo, esquerda)."""

PDF_FONT_MAIN: str = os.getenv("PDF_FONT_MAIN", '"DejaVu Sans", "Liberation Sans", sans-serif')
"""Fonte principal do corpo do texto no PDF."""

PDF_FONT_MONO: str = os.getenv("PDF_FONT_MONO", '"DejaVu Sans Mono", monospace')
"""Fonte monoespacada para codigo inline ou blocos de codigo no PDF."""


# =============================================================================
# SECAO 3: VALIDACAO (fail-fast)
# =============================================================================

def _validate() -> None:
    """Executa validacoes basicas no carregamento do modulo.
    Falha imediatamente se alguma configuracao essencial estiver inconsistente."""
    if LLM_TEMPERATURE < 0 or LLM_TEMPERATURE > 2:
        raise ValueError(
            f"LLM_TEMPERATURE deve estar entre 0 e 2, mas recebeu {LLM_TEMPERATURE}. "
            f"Verifique a variavel de ambiente LLM_TEMPERATURE."
        )

    for margin_name, margin_val in (
        ("PDF_MARGIN_TOP_CM", PDF_MARGIN_TOP_CM),
        ("PDF_MARGIN_RIGHT_CM", PDF_MARGIN_RIGHT_CM),
        ("PDF_MARGIN_BOTTOM_CM", PDF_MARGIN_BOTTOM_CM),
        ("PDF_MARGIN_LEFT_CM", PDF_MARGIN_LEFT_CM),
    ):
        if margin_val < 0:
            raise ValueError(
                f"{margin_name} nao pode ser negativo, mas recebeu {margin_val}. "
                f"Verifique o arquivo .env ou as variaveis de ambiente."
            )


# Executa validacao automaticamente ao importar o modulo.
_validate()
