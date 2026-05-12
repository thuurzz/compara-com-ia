# =============================================================================
# REPORT_TEMPLATE.PY  —  Prompts de Engenharia de LLM
# =============================================================================
# Este arquivo contém os "comandos" (prompts) enviados ao modelo de linguagem.
# A qualidade do relatório gerado depende diretamente da clareza e da
# estrutura destes prompts. Eles funcionam como a "receita" que o LLM segue
# para produzir o relatório jurídico comparativo.
# =============================================================================


# ---------------------------------------------------------------------------
# SYSTEM_PROMPT  —  Persona do LLM
# ---------------------------------------------------------------------------
# Define o papel e o comportamento do modelo durante toda a conversa.
# Ao definir o LLM como "especialista jurídico sênior", aumentamos a
# probabilidade de respostas formais, precisas e com vocabulário adequado.
# A instrução de idioma garante consistência em português do Brasil.
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """Você é um especialista jurídico sênior especializado em análise e revisão de contratos.
Sua função é analisar as diferenças entre dois contratos e produzir um relatório claro, objetivo e profissional.
Responda sempre em português do Brasil. Seja preciso e evite ambiguidades."""


# ---------------------------------------------------------------------------
# REPORT_PROMPT_TEMPLATE  —  Estrutura do Relatório Solicitado
# ---------------------------------------------------------------------------
# Este template instrui o LLM a gerar um relatório com 5 seções fixas.
# O placeholder {differences} será preenchido em tempo de execução com
# o texto formatado pela função format_differences_for_prompt() do
# módulo comparator.py.
#
# As seções são projetadas para cobrir todo o ciclo de análise jurídica:
#   1. Resumo Executivo      → visão geral para decisores
#   2. Cláusulas Adicionadas → novas obrigações/direitos
#   3. Cláusulas Removidas   → direitos/obrigações extintas
#   4. Cláusulas Modificadas → alterações de redação (tabela)
#   5. Pontos de Atenção     → riscos e implicações estratégicas
#
# A instrução final "Responda APENAS com o relatório" evita que o LLM
# adicione saudações, desculpas ou explicações extras no início/fim.
# ---------------------------------------------------------------------------
REPORT_PROMPT_TEMPLATE = """Analise as diferenças abaixo, identificadas de forma automática entre o Contrato A (versão original) e o Contrato B (versão revisada).

DIFERENÇAS IDENTIFICADAS:
{differences}

Com base nessas diferenças, gere um relatório comparativo profissional seguindo EXATAMENTE este formato:

---

## 1. Resumo Executivo

[Escreva 2 a 3 parágrafos descrevendo o contexto geral das alterações, o volume de mudanças e a natureza predominante das modificações (ex: ajustes de prazo, alterações de valor, mudanças de responsabilidade, etc.)]

---

## 2. Cláusulas Adicionadas no Contrato B

[Liste cada cláusula ou trecho adicionado, numerado. Se não houver, escreva "Nenhuma cláusula adicionada."]

---

## 3. Cláusulas Removidas do Contrato A

[Liste cada cláusula ou trecho removido, numerado. Se não houver, escreva "Nenhuma cláusula removida."]

---

## 4. Cláusulas Modificadas

[Para cada modificação, apresente em formato de tabela ou lista estruturada com:
- Identificação da cláusula/trecho
- Redação anterior (Contrato A)
- Nova redação (Contrato B)
- Impacto da alteração
Se não houver, escreva "Nenhuma cláusula modificada."]

---

## 5. Pontos de Atenção e Riscos

[Destaque as 3 a 5 mudanças mais relevantes sob o ponto de vista jurídico ou de negócio, explicando por que merecem atenção especial. Inclua potenciais riscos ou implicações de cada uma.]

---

Responda APENAS com o relatório no formato acima, sem comentários adicionais antes ou depois."""


def build_prompt(differences_text: str) -> str:
    """
    Regra de Negócio: Montagem do Prompt Final
    ------------------------------------------
    Injeta o texto das diferenças (já formatado) no template de relatório.
    É a última etapa de preparação antes de enviar o prompt ao LLM.
    """
    return REPORT_PROMPT_TEMPLATE.format(differences=differences_text)
