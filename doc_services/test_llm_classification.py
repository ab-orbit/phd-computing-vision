#!/usr/bin/env python3
"""
Script de teste para classificação de documentos usando LLM.

Este script demonstra como usar a API de classificação com
Anthropic Claude para classificar documentos.
"""

import asyncio
import sys
from pathlib import Path

# Adicionar path do projeto
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.services.llm_anthropic import create_anthropic_service
from app.models.schemas import DocumentType


async def test_classification_simple():
    """
    Teste simples de classificação com LLM.

    Demonstra classificação básica sem features adicionais.
    """
    print("=" * 80)
    print("TESTE 1: Classificação Simples")
    print("=" * 80)

    # Verificar API key
    if not settings.ANTHROPIC_API_KEY:
        print("ERRO: ANTHROPIC_API_KEY não configurada")
        print("Configure no arquivo .env:")
        print("  ANTHROPIC_API_KEY=sk-ant-xxx")
        return

    # Criar service
    service = create_anthropic_service(
        api_key=settings.ANTHROPIC_API_KEY,
        model=settings.ANTHROPIC_MODEL
    )

    print(f"\nModelo: {settings.ANTHROPIC_MODEL}")
    print(f"Provider: Anthropic Claude")
    print(f"Custo estimado: ~$0.005 por documento\n")

    # Tipos disponíveis
    available_types = [t.value for t in DocumentType]

    # Testar classificação de diferentes tipos de documentos
    test_cases = [
        {
            "name": "research_paper_2024.pdf",
            "expected": "scientific_publication"
        },
        {
            "name": "invoice_12345.pdf",
            "expected": "invoice"
        },
        {
            "name": "employment_contract.pdf",
            "expected": "contract"
        },
        {
            "name": "email_thread.pdf",
            "expected": "email"
        },
        {
            "name": "product_advertisement.pdf",
            "expected": "advertisement"
        }
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n[{i}/{len(test_cases)}] Classificando: {test['name']}")
        print("-" * 80)

        try:
            result = await service.classify_document(
                document_name=test["name"],
                available_types=available_types
            )

            print(f"Tipo predito: {result['predicted_type']}")
            print(f"Tipo esperado: {test['expected']}")
            print(f"Confiança: {result['confidence']:.2%}")
            print(f"Razão: {result.get('reasoning', 'N/A')}")

            # Metadados LLM
            llm_meta = result['llm_metadata']
            print(f"\nTokens: {llm_meta.total_tokens} (in:{llm_meta.input_tokens}, out:{llm_meta.output_tokens})")
            print(f"Custo: ${llm_meta.total_cost_usd}")
            print(f"Latência: {llm_meta.latency_ms:.0f}ms")

            # Validar resultado
            correct = result['predicted_type'] == test['expected']
            status = "✓ CORRETO" if correct else "✗ INCORRETO"
            print(f"\nStatus: {status}")

        except Exception as e:
            print(f"ERRO: {str(e)}")

    print("\n" + "=" * 80)


async def test_classification_with_features():
    """
    Teste de classificação com features adicionais.

    Demonstra como features extraídas do documento melhoram a classificação.
    """
    print("\n" + "=" * 80)
    print("TESTE 2: Classificação com Features")
    print("=" * 80)

    if not settings.ANTHROPIC_API_KEY:
        print("ERRO: ANTHROPIC_API_KEY não configurada")
        return

    service = create_anthropic_service(
        api_key=settings.ANTHROPIC_API_KEY,
        model=settings.ANTHROPIC_MODEL
    )

    available_types = [t.value for t in DocumentType]

    # Teste com features que indicam publicação científica
    print("\nCaso 1: Documento com características de publicação científica")
    print("-" * 80)

    features_scientific = {
        "num_paragraphs": 12,
        "text_density": 0.68,
        "num_figures": 8,
        "num_tables": 3,
        "num_equations": 15
    }

    result = await service.classify_document(
        document_name="unknown_document.pdf",
        available_types=available_types,
        features=features_scientific
    )

    print(f"Features fornecidas: {features_scientific}")
    print(f"\nTipo predito: {result['predicted_type']}")
    print(f"Confiança: {result['confidence']:.2%}")
    print(f"Custo: ${result['llm_metadata'].total_cost_usd}")

    # Teste com features que indicam email
    print("\n\nCaso 2: Documento com características de email")
    print("-" * 80)

    features_email = {
        "num_paragraphs": 3,
        "text_density": 0.15,
        "num_figures": 0,
        "num_tables": 0,
        "num_equations": 0
    }

    result = await service.classify_document(
        document_name="message.pdf",
        available_types=available_types,
        features=features_email
    )

    print(f"Features fornecidas: {features_email}")
    print(f"\nTipo predito: {result['predicted_type']}")
    print(f"Confiança: {result['confidence']:.2%}")
    print(f"Custo: ${result['llm_metadata'].total_cost_usd}")

    print("\n" + "=" * 80)


async def test_cost_analysis():
    """
    Análise de custos de diferentes modelos.

    Compara custos entre Claude Haiku (mais barato) e Sonnet.
    """
    print("\n" + "=" * 80)
    print("TESTE 3: Análise de Custos")
    print("=" * 80)

    if not settings.ANTHROPIC_API_KEY:
        print("ERRO: ANTHROPIC_API_KEY não configurada")
        return

    models_to_test = [
        {
            "name": "claude-3-5-haiku-20241022",
            "display": "Claude 3.5 Haiku (MAIS BARATO)",
            "input_price": 1.00,
            "output_price": 5.00
        },
        {
            "name": "claude-3-5-sonnet-20241022",
            "display": "Claude 3.5 Sonnet (MÉDIO)",
            "input_price": 3.00,
            "output_price": 15.00
        }
    ]

    available_types = [t.value for t in DocumentType]
    document_name = "sample_document.pdf"

    print(f"\nDocumento de teste: {document_name}\n")

    results = []

    for model_config in models_to_test:
        print(f"Testando: {model_config['display']}")
        print("-" * 80)

        service = create_anthropic_service(
            api_key=settings.ANTHROPIC_API_KEY,
            model=model_config["name"]
        )

        try:
            result = await service.classify_document(
                document_name=document_name,
                available_types=available_types
            )

            llm_meta = result['llm_metadata']

            results.append({
                "model": model_config["display"],
                "predicted_type": result["predicted_type"],
                "confidence": result["confidence"],
                "tokens": llm_meta.total_tokens,
                "cost": float(llm_meta.total_cost_usd),
                "latency_ms": llm_meta.latency_ms
            })

            print(f"Tipo: {result['predicted_type']}")
            print(f"Confiança: {result['confidence']:.2%}")
            print(f"Tokens: {llm_meta.total_tokens}")
            print(f"Custo: ${llm_meta.total_cost_usd}")
            print(f"Latência: {llm_meta.latency_ms:.0f}ms\n")

        except Exception as e:
            print(f"ERRO: {str(e)}\n")

    # Comparação
    if len(results) == 2:
        print("=" * 80)
        print("COMPARAÇÃO")
        print("=" * 80)

        haiku = results[0]
        sonnet = results[1]

        print(f"\nCusto Haiku:  ${haiku['cost']:.6f}")
        print(f"Custo Sonnet: ${sonnet['cost']:.6f}")
        print(f"Economia usando Haiku: {(1 - haiku['cost']/sonnet['cost'])*100:.1f}%")

        print(f"\nLatência Haiku:  {haiku['latency_ms']:.0f}ms")
        print(f"Latência Sonnet: {sonnet['latency_ms']:.0f}ms")

        print(f"\nProjeção de custos para 1000 documentos:")
        print(f"  Haiku:  ${haiku['cost'] * 1000:.2f}")
        print(f"  Sonnet: ${sonnet['cost'] * 1000:.2f}")
        print(f"  Economia: ${(sonnet['cost'] - haiku['cost']) * 1000:.2f}")

    print("\n" + "=" * 80)


async def main():
    """Executa todos os testes."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "TESTE DE CLASSIFICAÇÃO COM LLM" + " " * 28 + "║")
    print("║" + " " * 24 + "Anthropic Claude API" + " " * 34 + "║")
    print("╚" + "=" * 78 + "╝")

    # Verificar configuração
    if not settings.ANTHROPIC_API_KEY:
        print("\n" + "=" * 80)
        print("CONFIGURAÇÃO NECESSÁRIA")
        print("=" * 80)
        print("\nPara executar os testes, configure sua API key da Anthropic:")
        print("\n1. Obtenha uma API key em: https://console.anthropic.com/")
        print("\n2. Crie um arquivo .env na raiz do projeto:")
        print("   cp .env.example .env")
        print("\n3. Adicione sua API key:")
        print("   ANTHROPIC_API_KEY=sk-ant-api03-xxx")
        print("\n4. Execute novamente este script")
        print("\n" + "=" * 80)
        return

    try:
        # Executar testes
        await test_classification_simple()
        await test_classification_with_features()
        await test_cost_analysis()

        print("\n✓ TODOS OS TESTES CONCLUÍDOS")
        print("\nDica: Use Claude 3.5 Haiku para produção (mais barato)")
        print("      Use Claude 3.5 Sonnet para casos que exigem maior precisão\n")

    except KeyboardInterrupt:
        print("\n\nTestes interrompidos pelo usuário")
    except Exception as e:
        print(f"\n\nERRO FATAL: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
