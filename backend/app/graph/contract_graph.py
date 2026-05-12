"""Contract Graph — Pipeline LangGraph de comparacao de contratos."""

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from openai import OpenAI

from app.core.config import LLM_BASE_URL, LLM_API_KEY, LLM_MODEL, LLM_TEMPERATURE
from app.services.extractors import extract_text
from app.services.comparator import compare_contracts, format_differences_for_prompt
from app.services.report_template import SYSTEM_PROMPT, build_prompt
from app.services.pdf_exporter import markdown_to_pdf


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
    text_a = extract_text(state["file_a_bytes"], state["file_a_name"])
    text_b = extract_text(state["file_b_bytes"], state["file_b_name"])
    return {"text_a": text_a, "text_b": text_b}


def node_compare_contracts(state: ContractState) -> dict:
    differences = compare_contracts(state["text_a"], state["text_b"])
    return {"differences": differences}


def node_generate_report(state: ContractState) -> dict:
    differences_text = format_differences_for_prompt(state["differences"])
    prompt = build_prompt(differences_text)

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
    graph = StateGraph(ContractState)
    graph.add_node("extract_texts", node_extract_texts)
    graph.add_node("compare_contracts", node_compare_contracts)
    graph.add_node("generate_report", node_generate_report)
    graph.add_edge(START, "extract_texts")
    graph.add_edge("extract_texts", "compare_contracts")
    graph.add_edge("compare_contracts", "generate_report")
    graph.add_edge("generate_report", END)
    return graph.compile()


contract_graph = build_graph()
