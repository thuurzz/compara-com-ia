"""PDF Exporter — Converte Markdown para PDF usando WeasyPrint."""

import markdown
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration

from app.core.config import (
    PDF_PAGE_SIZE,
    PDF_MARGIN_TOP_CM,
    PDF_MARGIN_RIGHT_CM,
    PDF_MARGIN_BOTTOM_CM,
    PDF_MARGIN_LEFT_CM,
    PDF_FONT_MAIN,
    PDF_FONT_MONO,
)


def markdown_to_pdf(markdown_text: str) -> bytes:
    """Converte Markdown para PDF (HTML intermediario com WeasyPrint)."""

    html_body = markdown.markdown(markdown_text, extensions=["tables", "nl2br", "fenced_code"])

    html_full = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Relatorio Comparativo de Contratos</title>
<style>
@page {{
    size: {PDF_PAGE_SIZE};
    margin: {PDF_MARGIN_TOP_CM}cm {PDF_MARGIN_RIGHT_CM}cm {PDF_MARGIN_BOTTOM_CM}cm {PDF_MARGIN_LEFT_CM}cm;
    @top-center {{
        content: "Relatorio Comparativo de Contratos";
        font-family: {PDF_FONT_MAIN};
        font-size: 9pt;
        color: #555;
        border-bottom: 0.5pt solid #bbb;
        padding-bottom: 4pt;
    }}
    @bottom-center {{
        content: "Pagina " counter(page);
        font-family: {PDF_FONT_MAIN};
        font-size: 8pt;
        color: #888;
    }}
}}
body {{
    font-family: {PDF_FONT_MAIN};
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}}
h1 {{
    font-size: 18pt;
    color: #1a3a6e;
    border-bottom: 2pt solid #1a3a6e;
    padding-bottom: 6pt;
    margin-top: 0;
    margin-bottom: 16pt;
    page-break-after: avoid;
}}
h2 {{
    font-size: 14pt;
    color: #1a3a6e;
    border-bottom: 1pt solid #1a3a6e;
    padding-bottom: 4pt;
    margin-top: 20pt;
    margin-bottom: 10pt;
    page-break-after: avoid;
}}
h3 {{
    font-size: 12pt;
    color: #444;
    margin-top: 14pt;
    margin-bottom: 6pt;
    page-break-after: avoid;
}}
p {{
    margin: 6pt 0;
    text-align: justify;
    orphans: 3;
    widows: 3;
}}
strong {{
    font-weight: 700;
    color: #222;
}}
ul, ol {{
    margin: 6pt 0;
    padding-left: 20pt;
}}
li {{
    margin: 3pt 0;
}}
hr {{
    border: none;
    border-top: 1pt solid #ccc;
    margin: 14pt 0;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 10pt 0;
    font-size: 10pt;
    page-break-inside: auto;
}}
tr {{
    page-break-inside: avoid;
    page-break-after: auto;
}}
thead {{
    display: table-header-group;
}}
th, td {{
    border: 0.5pt solid #999;
    padding: 6pt 8pt;
    text-align: left;
    vertical-align: top;
}}
th {{
    background-color: #e8eef5;
    font-weight: 700;
    color: #1a3a6e;
}}
tbody tr:nth-child(even) {{
    background-color: #f7f9fb;
}}
code {{
    font-family: {PDF_FONT_MONO};
    background-color: #f0f0f0;
    padding: 1pt 3pt;
    border-radius: 2pt;
    font-size: 10pt;
}}
pre {{
    background-color: #f5f5f5;
    padding: 8pt;
    border-radius: 3pt;
    overflow-x: auto;
    font-size: 9.5pt;
    line-height: 1.4;
    page-break-inside: avoid;
}}
blockquote {{
    margin: 8pt 0;
    padding: 8pt 12pt;
    border-left: 3pt solid #1a3a6e;
    background-color: #f0f4f8;
    color: #444;
    font-style: italic;
}}
</style>
</head>
<body>
{html_body}
</body>
</html>"""

    font_config = FontConfiguration()
    html_doc = HTML(string=html_full)
    return html_doc.write_pdf(font_config=font_config)
