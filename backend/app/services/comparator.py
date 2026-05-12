"""Comparator — Comparacao deterministica de contratos."""

import difflib
import re


def split_into_blocks(text: str) -> list[str]:
    """Divide texto em blocos (paragrafos) separados por 2+ quebras de linha."""
    blocks = re.split(r"\n{2,}", text.strip())
    return [b.strip() for b in blocks if b.strip()]


def compare_contracts(text_a: str, text_b: str) -> list[dict]:
    """Compara dois textos e retorna diferencas estruturadas."""
    blocks_a = split_into_blocks(text_a)
    blocks_b = split_into_blocks(text_b)

    matcher = difflib.SequenceMatcher(None, blocks_a, blocks_b, autojunk=False)
    differences = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        elif tag == "insert":
            for block in blocks_b[j1:j2]:
                differences.append({"type": "added", "text_a": "", "text_b": block})
        elif tag == "delete":
            for block in blocks_a[i1:i2]:
                differences.append({"type": "removed", "text_a": block, "text_b": ""})
        elif tag == "replace":
            a_blocks = blocks_a[i1:i2]
            b_blocks = blocks_b[j1:j2]
            max_len = max(len(a_blocks), len(b_blocks))
            for idx in range(max_len):
                differences.append({
                    "type": "modified",
                    "text_a": a_blocks[idx] if idx < len(a_blocks) else "",
                    "text_b": b_blocks[idx] if idx < len(b_blocks) else "",
                })

    return differences


def format_differences_for_prompt(differences: list[dict]) -> str:
    """Formata diferencas em texto estruturado para o prompt do LLM."""
    if not differences:
        return "Nenhuma diferenca encontrada entre os contratos."

    lines = []
    added = [d for d in differences if d["type"] == "added"]
    removed = [d for d in differences if d["type"] == "removed"]
    modified = [d for d in differences if d["type"] == "modified"]

    if added:
        lines.append("=== CLAUSULAS ADICIONADAS NO CONTRATO B ===")
        for i, d in enumerate(added, 1):
            lines.append(f"[A{i}] {d['text_b']}")
        lines.append("")

    if removed:
        lines.append("=== CLAUSULAS REMOVIDAS DO CONTRATO A ===")
        for i, d in enumerate(removed, 1):
            lines.append(f"[R{i}] {d['text_a']}")
        lines.append("")

    if modified:
        lines.append("=== CLAUSULAS MODIFICADAS ===")
        for i, d in enumerate(modified, 1):
            lines.append(f"[M{i}] ANTES (Contrato A):\n{d['text_a']}")
            lines.append(f"[M{i}] DEPOIS (Contrato B):\n{d['text_b']}")
            lines.append("")

    return "\n".join(lines)
