"""Report Template — Prompts para o LLM."""

SYSTEM_PROMPT = """Voce e um especialista juridico senior especializado em analise e revisao de contratos.
Sua funcao e analisar as diferencas entre dois contratos e produzir um relatorio claro, objetivo e profissional.
Responda sempre em portugues do Brasil. Seja preciso e evite ambiguidades."""

REPORT_PROMPT_TEMPLATE = """Analise as diferencas abaixo, identificadas de forma automatica entre o Contrato A (versao original) e o Contrato B (versao revisada).

DIFERENCAS IDENTIFICADAS:
{differences}

Com base nessas diferencas, gere um relatorio comparativo profissional seguindo EXATAMENTE este formato:

---

## 1. Resumo Executivo

[Escreva 2 a 3 paragrafos descrevendo o contexto geral das alteracoes, o volume de mudancas e a natureza predominante das modificacoes]

---

## 2. Clausulas Adicionadas no Contrato B

[Liste cada clausula ou trecho adicionado, numerado. Se nao houver, escreva "Nenhuma clausula adicionada."]

---

## 3. Clausulas Removidas do Contrato A

[Liste cada clausula ou trecho removido, numerado. Se nao houver, escreva "Nenhuma clausula removida."]

---

## 4. Clausulas Modificadas

[Para cada modificacao, apresente em formato de tabela com:
- Identificacao da clausula/trecho
- Redacao anterior (Contrato A)
- Nova redacao (Contrato B)
- Impacto da alteracao
Se nao houver, escreva "Nenhuma clausula modificada."]

---

## 5. Pontos de Atencao e Riscos

[Destaque as 3 a 5 mudancas mais relevantes sob o ponto de vista juridico ou de negocio, explicando por que merecem atencao especial. Inclua potenciais riscos ou implicacoes de cada uma.]

---

Responda APENAS com o relatorio no formato acima, sem comentarios adicionais antes ou depois."""


def build_prompt(differences_text: str) -> str:
    return REPORT_PROMPT_TEMPLATE.format(differences=differences_text)
