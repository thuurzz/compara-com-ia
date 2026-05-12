from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from openai import OpenAI

from config import LLM_BASE_URL, LLM_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from extractors import extract_text
from comparator import compare_contracts, format_differences_for_prompt
from report_template import SYSTEM_PROMPT, build_prompt
from pdf_exporter import markdown_to_pdf


# =============================================================================
# ContractState  —  Estrutura de Dados do Pipeline
# =============================================================================
class ContractState(TypedDict):
    file_a_bytes: bytes
    file_a_name: str
    file_b_bytes: bytes
    file_b_name: str
    text_a: str
    text_b: str
    differences: list[dict]
    report_markdown: str
    report_pdf_bytes: bytes


def node_extract_texts(state: ContractState) -> dict:
    """
    Regra de Negocio: Nó de Extracao de Texto
    -----------------------------------------
    Etapa 1 do pipeline. Recebe os bytes dos dois contratos enviados
    pelo usuario e extrai o texto puro de cada um.
    """
    text_a = extract_text(state["file_a_bytes"], state["file_a_name"])
    text_b = extract_text(state["file_b_bytes"], state["file_b_name"])
    return {"text_a": text_a, "text_b": text_b}


def node_compare_contracts(state: ContractState) -> dict:
    """
    Regra de Negocio: Nó de Comparacao Deterministica
    -------------------------------------------------
    Etapa 2 do pipeline. Compara os dois textos extraidos usando
    algoritmo matematico (difflib) para encontrar diferencas estruturais.
    """
    differences = compare_contracts(state["text_a"], state["text_b"])
    return {"differences": differences}


def node_generate_report(state: ContractState) -> dict:
    """
    Regra de Negocio: Nó de Geracao de Relatorio com IA
    ---------------------------------------------------
    Etapa 3 do pipeline. Usa um modelo de linguagem (LLM) via provedor
    OpenAI-compatible (LiteLLM, OpenRouter, OpenAI, Groq, etc.) para
    produzir um relatorio juridico profissional.

    As configuracoes de conexao (modelo, endpoint, chave) sao lidas do
    modulo config.py, que por sua vez le variaveis de ambiente/.env.

    Usamos o cliente 'openai' diretamente (sem wrapper LangChain) para
    evitar conflitos de dependencia e garantir compatibilidade com
    qualquer versao do pacote openai instalado no ambiente.
    """
    differences_text = format_differences_for_prompt(state["differences"])
    prompt = build_prompt(differences_text)

    # Cliente OpenAI universal — funciona com qualquer provedor compatible
    client = OpenAI(
        base_url=LLM_BASE_URL or None,
        api_key=LLM_API_KEY or "not-needed",
    )

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=LLM_TEMPERATURE,
    )

    report_markdown = response.choices[0].message.content

    report_pdf_bytes = markdown_to_pdf(report_markdown)
    return {"report_markdown": report_markdown, "report_pdf_bytes": report_pdf_bytes}


def build_graph():
    """
    Regra de Negocio: Construcao do Pipeline LangGraph
    --------------------------------------------------
    Monta o grafo de estados que orquestra o fluxo completo de
    processamento dos contratos.
    """
    graph = StateGraph(ContractState)
    graph.add_node("extract_texts", node_extract_texts)
    graph.add_node("compare_contracts", node_compare_contracts)
    graph.add_node("generate_report", node_generate_report)
    graph.add_edge(START, "extract_texts")
    graph.add_edge("extract_texts", "compare_contracts")
    graph.add_edge("compare_contracts", "generate_report")
    graph.add_edge("generate_report", END)
    return graph.compile()


# Instancia unica do grafo, importada por app.py
contract_graph = build_graph()
