import io
import re
from pypdf import PdfReader
from docx import Document


def extract_text(file_bytes: bytes, filename: str) -> str:
    """
    Regra de Negócio: Roteamento de Extração de Texto
    -----------------------------------------------
    Recebe os bytes brutos de um arquivo e seu nome, identifica o formato
    (PDF ou DOCX) e delega para o extrator correto. É a porta de entrada
    para todo o processo de leitura de documentos na aplicação.

    - PDF  -> usa pypdf para extrair texto página por página
    - DOCX -> usa python-docx para extrair parágrafo por parágrafo

    Em ambos os casos, o texto extraído passa por um pós-processamento
    que corrige artefatos comuns de parsers (ex: R$ virando R).
    """
    name = filename.lower()
    if name.endswith(".pdf"):
        return _extract_pdf(file_bytes)
    if name.endswith(".docx"):
        return _extract_docx(file_bytes)
    raise ValueError(f"Formato não suportado: {filename}. Use PDF ou DOCX.")


def _extract_pdf(file_bytes: bytes) -> str:
    """
    Regra de Negócio: Extração de Texto de PDF
    ------------------------------------------
    PDFs são documentos de layout fixo; o texto pode estar fragmentado
    em múltiplas páginas. Esta função:

    1. Lê o arquivo byte-a-byte via pypdf
    2. Extrai o texto de cada página individualmente
    3. Junta as páginas com dupla quebra de linha (\n\n)
    4. Aplica pós-processamento para limpar artefatos de extração

    Importante: fontes específicas ou encodings podem fazer símbolos
    como "R$" sumirem. O pós-processamento tenta recuperar isso.
    """
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    raw_text = "\n\n".join(pages)
    return _post_process_text(raw_text)


def _extract_docx(file_bytes: bytes) -> str:
    """
    Regra de Negócio: Extração de Texto de DOCX
    -------------------------------------------
    DOCX é um formato estruturado (XML). Esta função:

    1. Lê o arquivo com python-docx
    2. Itera sobre os parágrafos do documento
    3. Filtra parágrafos vazios (apenas whitespace)
    4. Junta os parágrafos com dupla quebra de linha
    5. Aplica pós-processamento para limpar artefatos

    DOCX geralmente preserva melhor caracteres especiais que PDF,
    mas ainda assim passa pelo mesmo pipeline de limpeza.
    """
    doc = Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    raw_text = "\n\n".join(paragraphs)
    return _post_process_text(raw_text)


def _post_process_text(text: str) -> str:
    """
    Regra de Negócio: Correção de Artefatos de Extração
    --------------------------------------------------
    Bibliotecas de extração de texto frequentemente perdem símbolos
    ou introduzem ruídos. Esta função aplica heurísticas para recuperar
    a qualidade do texto antes da comparação.

    Correções aplicadas:
    1. Símbolo "R$" perdido:
       - "R 50.000,00"  -> "R$ 50.000,00"
       - "R100.000,00"  -> "R$ 100.000,00"
       Usa regex com word boundary (\b) para não alterar palavras
       que comecem com R (ex: "Responsável").

    2. Espaços duplicados: normaliza múltiplos espaços/tabs para um só.

    3. Hifenização residual: remove hífens no fim de linha que são
       artefatos de quebra de palavra do PDF/DOCX original.
    """
    # Problema 1: símbolo R$ perdido vira "R " ou "R" colado com número
    text = re.sub(r"\bR\s+(\d[\d.,]*)", r"R$ \1", text)
    text = re.sub(r"\bR(\d[\d.,]*)", r"R$ \1", text)

    # Problema 2: espaços duplicados excessivos
    text = re.sub(r"[ \t]+", " ", text)

    # Problema 3: quebras de linha estranhas no meio de palavras (hifenização)
    text = re.sub(r"-(\n+)(?=[a-záéíóúãõâêîôûç])", r"\1", text, flags=re.IGNORECASE)

    return text
