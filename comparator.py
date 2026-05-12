import difflib
import re


def split_into_blocks(text: str) -> list[str]:
    """
    Regra de Negócio: Segmentação de Contrato em Blocos
    --------------------------------------------------
    Um contrato é composto por cláusulas e parágrafos. Para comparar
    dois contratos de forma significativa, precisamos dividir o texto
    em unidades lógicas ("blocos").

    Estratégia: separar o texto sempre que houver 2 ou mais quebras
    de linha consecutivas (\n\n+). Isso identifica parágrafos distintos
    ou seções separadas por espaço em branco.

    Cada bloco representa uma unidade semântica do contrato
    (ex: uma cláusula, um parágrafo, uma seção).
    """
    blocks = re.split(r"\n{2,}", text.strip())
    return [b.strip() for b in blocks if b.strip()]


def compare_contracts(text_a: str, text_b: str) -> list[dict]:
    """
    Regra de Negócio: Comparação Determinística de Contratos
    --------------------------------------------------------
    Compara dois textos de contrato e retorna uma lista estruturada
    de diferenças. É o "cérebro determinístico" da aplicação — não
    usa IA, apenas algoritmos matemáticos de comparação de sequências.

    Algoritmo: difflib.SequenceMatcher
    - Compara as sequências de blocos do Contrato A e Contrato B
    - autojunk=False garante que não ignore blocos pequenos como lixo
    - Cada bloco é tratado como um "token" na sequência

    Tipos de diferenças detectadas:
    - "added"    : bloco existe apenas no Contrato B (inserção)
    - "removed"  : bloco existe apenas no Contrato A (deleção)
    - "modified" : bloco foi substituído por outro no Contrato B (replace)

    Retorno: lista de dicionários com chaves:
        - type  : "added" | "removed" | "modified"
        - text_a: texto do bloco no Contrato A (vazio se "added")
        - text_b: texto do bloco no Contrato B (vazio se "removed")
    """
    blocks_a = split_into_blocks(text_a)
    blocks_b = split_into_blocks(text_b)

    matcher = difflib.SequenceMatcher(None, blocks_a, blocks_b, autojunk=False)
    differences = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        elif tag == "insert":
            for block in blocks_b[j1:j2]:
                differences.append({
                    "type": "added",
                    "text_a": "",
                    "text_b": block,
                })
        elif tag == "delete":
            for block in blocks_a[i1:i2]:
                differences.append({
                    "type": "removed",
                    "text_a": block,
                    "text_b": "",
                })
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
    """
    Regra de Negócio: Formatação de Diferenças para o LLM
    ----------------------------------------------------
    As diferenças brutas (lista de dicts) precisam ser transformadas
    em texto legível para o modelo de linguagem (LLM). Esta função
    organiza as diferenças em seções categorizadas:

    1. CLÁUSULAS ADICIONADAS NO CONTRATO B
       - Prefixo [A1], [A2]... para identificação
    2. CLÁUSULAS REMOVIDAS DO CONTRATO A
       - Prefixo [R1], [R2]... para identificação
    3. CLÁUSULAS MODIFICADAS
       - Prefixo [M1], [M2]... com ANTES e DEPOIS

    Se não houver diferenças, retorna uma mensagem padrão para
    orientar o LLM a produzir um relatório informativo mesmo assim.

    O formato é intencionalmente claro e estruturado para que o LLM
    consiga interpretar corretamente sem confundir os contextos.
    """
    if not differences:
        return "Nenhuma diferença encontrada entre os contratos."

    lines = []
    added = [d for d in differences if d["type"] == "added"]
    removed = [d for d in differences if d["type"] == "removed"]
    modified = [d for d in differences if d["type"] == "modified"]

    if added:
        lines.append("=== CLÁUSULAS ADICIONADAS NO CONTRATO B ===")
        for i, d in enumerate(added, 1):
            lines.append(f"[A{i}] {d['text_b']}")
        lines.append("")

    if removed:
        lines.append("=== CLÁUSULAS REMOVIDAS DO CONTRATO A ===")
        for i, d in enumerate(removed, 1):
            lines.append(f"[R{i}] {d['text_a']}")
        lines.append("")

    if modified:
        lines.append("=== CLÁUSULAS MODIFICADAS ===")
        for i, d in enumerate(modified, 1):
            lines.append(f"[M{i}] ANTES (Contrato A):\n{d['text_a']}")
            lines.append(f"[M{i}] DEPOIS (Contrato B):\n{d['text_b']}")
            lines.append("")

    return "\n".join(lines)
