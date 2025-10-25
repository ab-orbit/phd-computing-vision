"""
Testes para ComplianceService (UC4).

EXPLICAÇÃO EDUCATIVA:
Testa validação de regras e geração de relatórios.
"""

import pytest
import tempfile
from pathlib import Path
from app.services import ComplianceService


class TestComplianceService:
    """Testes para serviço de conformidade."""

    @pytest.fixture
    def template_file(self):
        """Cria arquivo de template temporário para testes."""
        template_content = """# Relatório
Arquivo: ${file_name}
Palavras: ${word_count}
Parágrafos: ${paragraph_count}
Status: ${overall_status}
"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            f.write(template_content)
            return Path(f.name)

    @pytest.fixture
    def service(self, template_file):
        """Fixture que cria instância do serviço."""
        return ComplianceService(template_path=template_file)

    def test_validate_compliant_document(self, service):
        """Testa validação de documento conforme."""
        result = service.validate_compliance(
            word_count=2500,  # >= 2000 ✓
            paragraph_count=8  # == 8 ✓
        )

        assert result.is_compliant is True
        assert result.words_compliant is True
        assert result.paragraphs_compliant is True
        assert len(result.recommended_actions) == 0

    def test_validate_too_few_words(self, service):
        """Testa documento com poucas palavras."""
        result = service.validate_compliance(
            word_count=1500,  # < 2000 ✗
            paragraph_count=8   # == 8 ✓
        )

        assert result.is_compliant is False
        assert result.words_compliant is False
        assert result.paragraphs_compliant is True
        assert len(result.recommended_actions) > 0
        assert result.word_difference == -500

    def test_validate_wrong_paragraph_count(self, service):
        """Testa documento com número errado de parágrafos."""
        result = service.validate_compliance(
            word_count=2500,  # >= 2000 ✓
            paragraph_count=10  # != 8 ✗
        )

        assert result.is_compliant is False
        assert result.words_compliant is True
        assert result.paragraphs_compliant is False
        assert result.paragraph_difference == 2

    def test_generate_report(self, service):
        """Testa geração de relatório."""
        report = service.generate_report(
            filename="test.pdf",
            word_count=2100,
            paragraph_count=8
        )

        # Verificar que template foi preenchido
        assert "test.pdf" in report
        assert "2100" in report
        assert "8" in report
        assert "Conforme" in report
