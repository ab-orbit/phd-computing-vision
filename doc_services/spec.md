# Spec

UC1. Serviço que identifique se a imagem do documento (pdf ou imagem)
é um artigo científico. Caso não seja, retorno que não é um documento válido
contraint:
Em caso positivo:
Use serviço API já implementado e disponivel.

UC2. Detecte parágrafos e quantifique
constraint: use docling 

UC3. Extraia textos dos parágrafos e quantifique as palavras mais frequentes
constraint: use técnica básica de programação

UC4. Crie um resumo informando se o texto está em conformidade com a regra: 2000 palavras e 08 parágrafos
constraint: use programacao básica para construir um resumo a partir do template abaixo

# UC4 — Resumo de Conformidade do Texto

**Arquivo:** {{file_name}}
**ID do Documento (opcional):** {{document_id}}
**Data da Análise:** {{analysis_datetime}}

---

## Regras Avaliadas
- Mínimo de palavras: **2000**
- Número de parágrafos: **8**

## Métricas Detectadas
- Total de palavras: **{{word_count}}**
- Total de parágrafos: **{{paragraph_count}}**

## Conformidade por Regra
- Palavras (≥ 2000): {{words_ok}}  <!-- use "Conforme" ou "Não conforme" -->
- Parágrafos (= 8): {{paragraphs_ok}}  <!-- use "Conforme" ou "Não conforme" -->

## Resultado Geral
**Status:** {{overall_status}}  <!-- "Conforme" se ambas as regras ok, caso contrário "Não conforme" -->

---

## Resumo Automático
{{summary_sentence_1}}  
<!-- Ex.: "O texto possui {{word_count}} palavras ({{word_diff_from_2000}} em relação ao mínimo) e {{paragraph_count}} parágrafos ({{paragraph_diff_from_8}} em relação ao exigido)." -->

{{summary_sentence_2}}  
<!-- Ex.: "Com base nas regras estabelecidas, o documento está {{overall_status}}." -->

## Ações Recomendadas (se não conforme)
- Ajustar contagem de palavras: {{words_action}}  
  <!-- Ex.: "Adicionar {{missing_words}} palavras" ou "Reduzir {{excess_words}} palavras" ou "Nenhuma ação necessária" -->
- Ajustar número de parágrafos: {{paragraphs_action}}  
  <!-- Ex.: "Adicionar {{missing_paragraphs}} parágrafos" ou "Fundir/redistribuir para reduzir {{excess_paragraphs}} parágrafos" ou "Nenhuma ação necessária" -->

---

## Observações (opcional)
{{notes}}