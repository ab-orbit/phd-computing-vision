"""
Testes para TextAnalysisService (UC3).

EXPLICAÇÃO EDUCATIVA:
Testes unitários verificam que cada função funciona corretamente.
Usamos pytest, framework de testes para Python.
"""

import pytest
from app.models import Paragraph
from app.services import TextAnalysisService


class TestTextAnalysisService:
    """Testes para serviço de análise textual."""

    @pytest.fixture
    def service(self):
        """Fixture que cria instância do serviço para testes."""
        return TextAnalysisService()

    @pytest.fixture
    def sample_paragraphs(self):
        """Fixture com parágrafos de exemplo."""
        return [
            Paragraph(index=0, text="Este é um teste de análise.", word_count=6),
            Paragraph(index=1, text="Análise de texto é importante.", word_count=5),
            Paragraph(index=2, text="Python é uma linguagem versátil.", word_count=5),
        ]

    def test_analyze_text_basic(self, service, sample_paragraphs):
        """Testa análise básica de texto."""
        result = service.analyze_text(sample_paragraphs, top_n=5)

        # Verificar que total de palavras está correto
        assert result.total_words == 16  # 6 + 5 + 5

        # Verificar que tem palavras únicas
        assert result.unique_words > 0

        # Verificar que frequências foram calculadas
        assert len(result.word_frequencies) > 0

        # Verificar que top words foi gerado
        assert len(result.top_words) > 0

    def test_word_counting(self, service, sample_paragraphs):
        """Testa contagem de palavras."""
        text = "teste teste teste palavra palavra outra"
        paragraphs = [Paragraph(index=0, text=text, word_count=6)]

        result = service.analyze_text(paragraphs)

        # "teste" deve aparecer 3 vezes
        assert result.word_frequencies["teste"] == 3

        # "palavra" deve aparecer 2 vezes
        assert result.word_frequencies["palavra"] == 2

    def test_empty_paragraphs_error(self, service):
        """Testa erro com lista vazia."""
        with pytest.raises(ValueError):
            service.analyze_text([])

    def test_top_words_order(self, service):
        """Testa que top words estão ordenadas por frequência."""
        paragraphs = [
            Paragraph(
                index=0,
                text="a a a b b c",
                word_count=6
            )
        ]

        result = service.analyze_text(paragraphs, top_n=3)

        # Primeira palavra deve ser 'a' (3 ocorrências)
        assert result.top_words[0]["word"] == "a"
        assert result.top_words[0]["count"] == 3
