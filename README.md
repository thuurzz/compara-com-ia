# Comparador de Contratos com IA

Aplicacao web para comparacao inteligente de contratos (PDF/DOCX) usando
processamento deterministico + Modelos de Linguagem (LLM). Gera um relatorio
juridico profissional em Markdown e PDF com analise das diferencas entre duas
versoes de um mesmo contrato.

---

## Sumario

- [O que faz](#o-que-faz)
- [Arquitetura](#arquitetura)
- [Tecnologias](#tecnologias)
- [Pre-requisitos](#pre-requisitos)
- [Instalacao](#instalacao)
- [Configuracao do LLM](#configuracao-do-llm)
  - [LiteLLM Proxy + Ollama (local)](#1-litellm-proxy--ollama-local)
  - [OpenRouter](#2-openrouter)
  - [Groq](#3-groq)
  - [OpenAI Oficial](#4-openai-oficial)
- [Como usar](#como-usar)
- [Estrutura de arquivos](#estrutura-de-arquivos)
- [Variaveis de ambiente](#variaveis-de-ambiente)
- [Regra de negocio detalhada](#regra-de-negocio-detalhada)
- [Licenca](#licenca)

---

## O que faz

O **Comparador de Contratos** automatiza a analise de revisoes contratuais.
Em vez de ler dois documentos manualmente pagina por pagina, o usuario faz o
upload da versao original (Contrato A) e da versao revisada (Contrato B). A
aplicacao entao:

1. **Extrai o texto** de ambos os documentos (PDF ou DOCX)
2. **Compara estruturalmente** os textos usando algoritmo deterministico
   (`difflib.SequenceMatcher`)
3. **Gera um relatorio juridico profissional** via LLM, analisando o impacto
   de cada alteracao
4. **Exporta o relatorio em PDF** com formatacao profissional (tabelas,
   cabecalho, rodape, tipografia)

### Exemplo de cenario de uso

> Um advogado recebe uma nova versao de um contrato de prestacao de servicos
> da contraparte. Em vez de comparar manualmente, ele faz upload das duas
> versoes no sistema. Em segundos, recebe um relatorio indicando que o prazo
> foi extendido de 12 para 24 meses, o valor subiu de R$ 50.000,00 para
> R$ 75.000,00 e uma clausula de foro foi alterada — com alertas de risco
> para cada mudanca.

---

## Arquitetura

O pipeline e orquestrado pelo **LangGraph** em 3 etapas sequenciais:

```
+-------------+     +------------------+     +------------------+
|   Upload    | --> |  Extração        | --> |  Comparação      |
|  (Streamlit)|     |  (PDF/DOCX)      |     |  (difflib)       |
+-------------+     +------------------+     +------------------+
                                                      |
                      +------------------+            v
                      |  Relatorio PDF   | <-- +------------------+
                      |  (WeasyPrint)    |     |  Geracao de      |
                      +------------------+     |  Relatorio (LLM) |
                                               +------------------+
```

1. **Extracao** (`extractors.py`): le PDF via `pypdf` ou DOCX via
   `python-docx`. Aplica pos-processamento para corrigir artefatos
   (ex: `R 50.000,00` -> `R$ 50.000,00`).

2. **Comparacao** (`comparator.py`): divide os textos em blocos
   (paragrafos/clausulas) e usa `difflib.SequenceMatcher` para detectar
   adicoes, remocoes e modificacoes. Classifica cada diferenca em:
   - `added`    — clausula nova no Contrato B
   - `removed`  — clausula removida do Contrato A
   - `modified` — clausula alterada

3. **Geracao de relatorio** (`graph.py` / `report_template.py`): as
   diferencas sao formatadas em um prompt estruturado e enviadas a um LLM
   via API OpenAI-compatible. O LLM produz um relatorio com 5 secoes:
   Resumo Executivo, Adicionadas, Removidas, Modificadas e Pontos de
   Atencao/Riscos.

4. **Exportacao PDF** (`pdf_exporter.py`): converte o Markdown do LLM para
   HTML (via `markdown`) e renderiza em PDF (via `weasyprint`) com CSS
   profissional — incluindo tabelas, cabecalho, rodape e tipografia.

---

## Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| Interface Web | [Streamlit](https://streamlit.io) |
| Orquestracao | [LangGraph](https://langchain-ai.github.io/langgraph/) |
| LLM (conexao) | Cliente nativo `openai` (OpenAI-compatible) |
| Extracao PDF | [pypdf](https://pypdf.readthedocs.io) |
| Extracao DOCX | [python-docx](https://python-docx.readthedocs.io) |
| Comparacao | `difflib` (stdlib Python) |
| Markdown -> HTML | [markdown](https://python-markdown.github.io) |
| HTML -> PDF | [WeasyPrint](https://weasyprint.org) |
| Configuracoes | [python-dotenv](https://saurabh-kumar.com/python-dotenv/) |

---

## Pre-requisitos

- Python 3.10+
- [Ollama](https://ollama.com) instalado (se for usar localmente)
- Ou uma chave de API de um provedor OpenAI-compatible (OpenRouter, Groq,
  OpenAI, etc.)

---

## Instalacao

```bash
# 1. Clone o repositorio
git clone https://github.com/seu-usuario/comparador-contratos.git
cd comparador-contratos

# 2. Crie e ative um ambiente virtual
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. Instale as dependencias
pip install -r requirements.txt

# 4. Configure o provedor de LLM (veja proxima secao)
cp .env.example .env
# Edite o arquivo .env com seus dados
```

---

## Configuracao do LLM

A aplicacao suporta **qualquer provedor com API OpenAI-compatible**.
A configuracao e feita exclusivamente via variaveis de ambiente ou arquivo
`.env`.

### 1. LiteLLM Proxy + Ollama (local)

Recomendado para uso offline/privado. O [LiteLLM](https://docs.litellm.ai)
funciona como um proxy universal que expoe modelos locais (Ollama) via API
OpenAI.

**Instale e inicie o LiteLLM:**
```bash
pip install litellm
litellm --model ollama/llama3.1:8b --port 4000
```

**`.env`:**
```env
LLM_BASE_URL=http://localhost:4000
LLM_API_KEY=sk-litellm-qualquer-chave-aqui
LLM_MODEL=ollama/llama3.1:8b
```

### 2. OpenRouter

Acesso a dezenas de modelos (OpenAI, Anthropic, Google, Meta, etc.) com uma
unica chave.

**`.env`:**
```env
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=sk-or-v1-sua-chave-aqui
LLM_MODEL=openai/gpt-4o-mini
```

### 3. Groq

Rapido e barato, com modelos Llama e Mixtral otimizados.

**`.env`:**
```env
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=gsk_sua-chave-aqui
LLM_MODEL=llama-3.1-8b-instant
```

### 4. OpenAI Oficial

```env
LLM_BASE_URL=
LLM_API_KEY=sk-proj-sua-chave-aqui
LLM_MODEL=gpt-4o-mini
```

> **Dica:** deixe `LLM_BASE_URL` vazio para usar o endpoint oficial da
> OpenAI (`https://api.openai.com/v1`).

---

## Como usar

```bash
# Certifique-se de que o ambiente virtual esta ativado
source .venv/bin/activate

# Inicie a aplicacao
streamlit run app.py
```

A interface abrira automaticamente no navegador (geralmente em
`http://localhost:8501`).

### Passo a passo na interface

1. **Upload do Contrato A** — selecione o PDF ou DOCX da versao original
2. **Upload do Contrato B** — selecione o PDF ou DOCX da versao revisada
3. Clique em **Comparar Contratos**
4. Aguarde o processamento (extracao + comparacao + LLM + PDF)
5. Explore os resultados:
   - **Diferencas detectadas** — visao tecnica das mudancas (expander)
   - **Relatorio Gerado** — analise juridica do LLM em Markdown
   - **Baixar Relatorio em PDF** — download do relatorio formatado

---

## Estrutura de arquivos

```
.
├── app.py                  # Interface web (Streamlit)
├── graph.py                # Orquestracao do pipeline (LangGraph)
├── config.py               # Central de configuracoes (.env)
├── extractors.py           # Extracao de texto de PDF/DOCX
├── comparator.py           # Comparacao deterministica (difflib)
├── report_template.py      # Prompts do LLM (system + template)
├── pdf_exporter.py         # Conversao Markdown -> PDF (WeasyPrint)
├── requirements.txt        # Dependencias Python
├── .env.example            # Exemplo de configuracao
├── .gitignore              # (recomendado) ignore .env, __pycache__/
└── README.md               # Este arquivo
```

| Arquivo | Responsabilidade |
|---------|-----------------|
| `app.py` | UI — upload, exibicao de resultados, download de PDF |
| `graph.py` | Orquestra as 3 etapas do pipeline via LangGraph |
| `config.py` | Centraliza todas as configs (LLM, PDF, validacoes) |
| `extractors.py` | Le PDF/DOCX e corrige artefatos de extracao |
| `comparator.py` | Detecta adicoes, remocoes e modificacoes |
| `report_template.py` | Define a "receita" do prompt juridico para o LLM |
| `pdf_exporter.py` | Renderiza Markdown em PDF profissional |

---

## Variaveis de ambiente

Todas as configuracoes sao centralizadas em `config.py` e podem ser
sobrescritas via arquivo `.env` ou variaveis de ambiente do sistema.

### LLM

| Variavel | Padrao | Descricao |
|----------|--------|-----------|
| `LLM_BASE_URL` | `http://localhost:4000` | Endpoint OpenAI-compatible |
| `LLM_API_KEY` | *(vazio)* | Chave de API do provedor |
| `LLM_MODEL` | `ollama/llama3.1:8b` | Identificador do modelo |
| `LLM_TEMPERATURE` | `0.0` | Temperatura (0 = deterministico) |

### PDF

| Variavel | Padrao | Descricao |
|----------|--------|-----------|
| `PDF_PAGE_SIZE` | `A4` | Formato da pagina |
| `PDF_MARGIN_TOP_CM` | `2.5` | Margem superior (cm) |
| `PDF_MARGIN_RIGHT_CM` | `2.0` | Margem direita (cm) |
| `PDF_MARGIN_BOTTOM_CM` | `2.5` | Margem inferior (cm) |
| `PDF_MARGIN_LEFT_CM` | `2.0` | Margem esquerda (cm) |
| `PDF_FONT_MAIN` | DejaVu Sans | Fonte principal |
| `PDF_FONT_MONO` | DejaVu Sans Mono | Fonte monoespacada |

---

## Regra de negocio detalhada

### 1. Extracao de texto

- PDFs sao lidos pagina a pagina com `pypdf`
- DOCX e lido paragrafo a paragrafo com `python-docx`
- **Pos-processamento**: correcao automatica de artefatos comuns, como o
  simbolo `R$` que frequentemente vira `R ` ou `R50.000,00` durante a
  extracao de certas fontes PDF

### 2. Comparacao deterministico

- O texto e dividido em **blocos** (paragrafos separados por 2+ quebras de
  linha)
- `difflib.SequenceMatcher` compara as sequencias de blocos do Contrato A
  e Contrato B
- Diferencas sao classificadas em 3 tipos:
  - `added` — bloco existe so no Contrato B
  - `removed` — bloco existe so no Contrato A
  - `modified` — bloco foi substituido

### 3. Geracao do relatorio com IA

- As diferencas sao formatadas em texto estruturado com prefixos `[A1]`,
  `[R1]`, `[M1]`
- Um prompt completo e montado com o template de 5 secoes
- O LLM recebe um `system prompt` definindo-o como "especialista juridico
  senior"
- **Temperatura 0** garante precisao e previsibilidade na analise
- O LLM retorna o relatorio em Markdown

### 4. Exportacao para PDF

- Markdown e convertido para HTML via `markdown` (com suporte a tabelas)
- WeasyPrint renderiza o HTML em PDF com CSS profissional
- Cabecalho e rodape automaticos com numero de pagina
- Tabelas renderizam com bordas, cabecalho colorido e zebrado
- UTF-8 nativo — sem truncamento de caracteres acentuados

---

## Licenca

Distribuido sob a licenca MIT. Veja [LICENSE](LICENSE) para mais detalhes.

---

> Desenvolvido com Python, Streamlit, LangGraph e WeasyPrint.
