"""
Serviço de Análise Textual (UC3).

Implementa o caso de uso 3: Extrair textos e quantificar palavras frequentes.

EXPLICAÇÃO EDUCATIVA:
Este serviço é responsável por:
1. Receber lista de parágrafos detectados
2. Extrair todo o texto
3. Contar palavras totais
4. Calcular frequência de cada palavra
5. Identificar palavras mais comuns

Constraint UC3: DEVE usar técnica básica de programação.
Usamos apenas Python stdlib (Counter, regex, str.split).
"""

import logging
import re
from collections import Counter
from typing import List, Dict

from app.models import Paragraph, TextAnalysis

logger = logging.getLogger(__name__)


class TextAnalysisService:
    """
    Serviço de análise textual básica.

    EXPLICAÇÃO EDUCATIVA:
    Este serviço usa apenas técnicas básicas de programação:

    1. Collections.Counter:
       - Estrutura de dados para contar elementos
       - Implementa dict especializado em contagem
       - Método most_common() retorna top N

    2. Regex (re):
       - Expressões regulares para processar texto
       - Limpar pontuação
       - Normalizar espaços

    3. String manipulation:
       - lower(): normalizar para minúsculas
       - split(): separar palavras
       - strip(): remover espaços

    Não usa bibliotecas avançadas de NLP (NLTK, spaCy) pois
    constraint UC3 exige programação básica.
    """

    def __init__(self):
        """Inicializa serviço de análise textual."""
        # Padrão regex para limpar pontuação
        # EXPLICAÇÃO: [^\w\s] significa "não é letra/número/underscore e não é espaço"
        self.punctuation_pattern = re.compile(r'[^\w\s]')

        logger.info("TextAnalysisService inicializado")

    def analyze_text(
        self,
        paragraphs: List[Paragraph],
        top_n: int = 10
    ) -> TextAnalysis:
        """
        Analisa texto dos parágrafos e retorna estatísticas.

        EXPLICAÇÃO EDUCATIVA:
        Este é o método principal do UC3.

        Fluxo de análise:
        1. Extrair texto de todos os parágrafos
        2. Concatenar em texto único
        3. Limpar e normalizar:
           - Remover pontuação
           - Converter para minúsculas
           - Normalizar espaços
        4. Tokenizar (split por espaços)
        5. Contar palavras com Counter
        6. Calcular estatísticas:
           - Total de palavras
           - Vocabulário (palavras únicas)
           - Frequências
           - Top N mais comuns

        Constraint UC3: Técnica básica de programação.

        Args:
            paragraphs: Lista de parágrafos detectados
            top_n: Número de palavras mais frequentes a retornar

        Returns:
            Objeto TextAnalysis com estatísticas

        Raises:
            ValueError: Se lista de parágrafos vazia
        """
        if not paragraphs:
            raise ValueError("Lista de parágrafos vazia")

        logger.info(f"Analisando texto de {len(paragraphs)} parágrafos")

        # Etapa 1: Extrair e concatenar texto
        full_text = self._extract_full_text(paragraphs)

        # Etapa 2: Limpar e normalizar texto
        cleaned_text = self._clean_text(full_text)

        # Etapa 3: Tokenizar (separar em palavras)
        words = self._tokenize(cleaned_text)

        # Etapa 4: Contar palavras
        word_frequencies = self._count_words(words)

        # Etapa 5: Obter top N palavras
        top_words = self._get_top_words(word_frequencies, top_n)

        # Etapa 6: Calcular estatísticas
        total_words = len(words)
        unique_words = len(word_frequencies)

        logger.info(
            f"Análise concluída: {total_words} palavras totais, "
            f"{unique_words} únicas"
        )

        # Criar objeto TextAnalysis
        return TextAnalysis(
            total_words=total_words,
            unique_words=unique_words,
            word_frequencies=word_frequencies,
            top_words=top_words
        )

    def _extract_full_text(self, paragraphs: List[Paragraph]) -> str:
        """
        Extrai e concatena texto de todos os parágrafos.

        EXPLICAÇÃO EDUCATIVA:
        Usa list comprehension + join:
        - List comprehension: [p.text for p in paragraphs]
        - join: une strings com separador

        Separamos parágrafos com "\n\n" para preservar estrutura.

        Args:
            paragraphs: Lista de parágrafos

        Returns:
            Texto completo concatenado
        """
        texts = [p.text for p in paragraphs]
        return "\n\n".join(texts)

    def _clean_text(self, text: str) -> str:
        """
        Limpa e normaliza texto.

        EXPLICAÇÃO EDUCATIVA:
        Passos de limpeza:
        1. Remover pontuação (regex)
        2. Converter para minúsculas
        3. Normalizar espaços múltiplos

        Exemplo:
        "Olá! Como vai?" → "ola como vai"

        Args:
            text: Texto a limpar

        Returns:
            Texto limpo e normalizado
        """
        # Remover pontuação
        text = self.punctuation_pattern.sub(' ', text)

        # Converter para minúsculas
        text = text.lower()

        # Normalizar espaços (substituir múltiplos por único)
        text = ' '.join(text.split())

        return text

    def _tokenize(self, text: str) -> List[str]:
        """
        Tokeniza texto em palavras.

        EXPLICAÇÃO EDUCATIVA:
        Tokenização básica:
        - Split por espaços
        - Filtrar palavras vazias
        - Filtrar palavras muito curtas (< 2 caracteres)

        Para análise mais sofisticada, poderia usar:
        - NLTK tokenizer
        - spaCy
        - Remoção de stopwords

        Mas UC3 exige programação básica.

        Args:
            text: Texto limpo

        Returns:
            Lista de palavras (tokens)
        """
        # Split por espaços
        words = text.split()

        # Filtrar palavras muito curtas (< 2 caracteres)
        # EXPLICAÇÃO: Evita contar "a", "e", "o" que não são informativos
        words = [w for w in words if len(w) >= 2]

        return words

    def _count_words(self, words: List[str]) -> Dict[str, int]:
        """
        Conta frequência de cada palavra.

        EXPLICAÇÃO EDUCATIVA:
        Usa Counter do módulo collections:
        - Counter([lista]) cria dicionário de contagens
        - Exemplo: Counter(['a', 'b', 'a']) → {'a': 2, 'b': 1}
        - Muito eficiente para contagem

        Converte para dict normal para serialização JSON.

        Args:
            words: Lista de palavras

        Returns:
            Dicionário {palavra: frequência}
        """
        # Contar com Counter
        counter = Counter(words)

        # Converter para dict normal
        return dict(counter)

    def _get_top_words(
        self,
        word_frequencies: Dict[str, int],
        top_n: int
    ) -> List[Dict[str, int]]:
        """
        Obtém N palavras mais frequentes.

        EXPLICAÇÃO EDUCATIVA:
        Usa Counter.most_common(n):
        - Retorna lista de tuplas: [(palavra, contagem), ...]
        - Já ordenada por contagem decrescente

        Convertemos para lista de dicts para serialização JSON:
        [{"word": "análise", "count": 45}, ...]

        Args:
            word_frequencies: Dicionário de frequências
            top_n: Número de palavras a retornar

        Returns:
            Lista de dicts com palavras mais frequentes
        """
        # Criar Counter a partir do dict
        counter = Counter(word_frequencies)

        # Obter top N
        top_items = counter.most_common(top_n)

        # Converter para lista de dicts
        top_words = [
            {"word": word, "count": count}
            for word, count in top_items
        ]

        return top_words
