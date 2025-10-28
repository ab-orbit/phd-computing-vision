"""
Script para avaliacao formal e automatizada de todos os checkpoints do treinamento LoRA.

Este script implementa uma metodologia rigorosa de avaliacao de qualidade:
1. Avalia todos os checkpoints disponíveis (500, 1000, 1500, 2000, 2500, 3000)
2. Calcula métricas quantitativas (FID e CLIP Score)
3. Gera relatório comparativo com análise estatística
4. Identifica o melhor checkpoint para producao

Metodologia de Avaliacao:
- FID (Frechet Inception Distance): Qualidade e diversidade das imagens
- CLIP Score: Alinhamento semantico entre prompt e imagem
- Analise estatística: Comparacao entre checkpoints com significancia

Uso:
    python evaluate_all_checkpoints.py \
        --real_images_dir ../data/casual_shoes/train/images \
        --validation_base_dir ../training/outputs/lora_casual_shoes_3000steps_full/validation \
        --output_dir ./checkpoint_evaluation_results
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import subprocess
import sys
from datetime import datetime


class CheckpointEvaluator:
    """
    Avaliador automatizado de checkpoints de modelos LoRA.

    Este avaliador implementa uma metodologia formal de avaliacao que:
    1. Verifica disponibilidade de imagens para cada checkpoint
    2. Prepara prompts automaticamente
    3. Calcula metricas FID e CLIP Score
    4. Gera relatorio comparativo
    5. Identifica checkpoint ideal para producao
    """

    def __init__(self,
                 real_images_dir: Path,
                 validation_base_dir: Path,
                 output_dir: Path,
                 checkpoints: List[int] = None):
        """
        Inicializa o avaliador de checkpoints.

        Args:
            real_images_dir: Diretorio com imagens reais do dataset
            validation_base_dir: Diretorio base contendo subdiretorios checkpoint-N
            output_dir: Diretorio para salvar resultados
            checkpoints: Lista de checkpoints a avaliar (default: [500, 1000, 1500, 2000, 2500, 3000])
        """
        self.real_images_dir = Path(real_images_dir)
        self.validation_base_dir = Path(validation_base_dir)
        self.output_dir = Path(output_dir)
        self.checkpoints = checkpoints or [500, 1000, 1500, 2000, 2500, 3000]

        # Cria diretorio de saida
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Resultados acumulados
        self.results = {}

    def verify_checkpoint_availability(self) -> Dict[int, Dict]:
        """
        Verifica quais checkpoints tem imagens disponiveis para avaliacao.

        Returns:
            Dicionario mapeando checkpoint -> {path, num_images, available}
        """
        print("\n" + "="*70)
        print("VERIFICACAO DE CHECKPOINTS DISPONIVEIS")
        print("="*70)

        availability = {}

        for ckpt in self.checkpoints:
            ckpt_dir = self.validation_base_dir / f"checkpoint-{ckpt}"

            if not ckpt_dir.exists():
                print(f"  [X] Checkpoint {ckpt}: Diretorio nao encontrado")
                availability[ckpt] = {
                    'path': ckpt_dir,
                    'num_images': 0,
                    'available': False,
                    'reason': 'Diretorio nao existe'
                }
                continue

            # Conta imagens
            image_extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']
            images = []
            for ext in image_extensions:
                images.extend(list(ckpt_dir.glob(f'*{ext}')))

            num_images = len(images)

            if num_images == 0:
                print(f"  [X] Checkpoint {ckpt}: Nenhuma imagem encontrada")
                availability[ckpt] = {
                    'path': ckpt_dir,
                    'num_images': 0,
                    'available': False,
                    'reason': 'Sem imagens'
                }
            else:
                print(f"  [OK] Checkpoint {ckpt}: {num_images} imagens encontradas")
                availability[ckpt] = {
                    'path': ckpt_dir,
                    'num_images': num_images,
                    'available': True
                }

        # Resumo
        available_count = sum(1 for info in availability.values() if info['available'])
        print(f"\nResumo: {available_count}/{len(self.checkpoints)} checkpoints disponiveis")

        return availability

    def prepare_prompts_for_checkpoint(self, checkpoint: int, checkpoint_dir: Path) -> Path:
        """
        Prepara arquivo de prompts para um checkpoint especifico.

        Args:
            checkpoint: Numero do checkpoint
            checkpoint_dir: Diretorio contendo imagens do checkpoint

        Returns:
            Caminho para o arquivo de prompts gerado
        """
        prompts_file = self.output_dir / f"prompts_checkpoint_{checkpoint}.json"

        # Usa prompt padrao generico
        # Em um cenario real, voce pode ter prompts especificos para cada imagem
        default_prompt = "A professional product photo of casual shoes"

        cmd = [
            sys.executable,  # Usa o mesmo interpretador Python
            "prepare_prompts.py",
            "--images_dir", str(checkpoint_dir),
            "--output", str(prompts_file),
            "--default_prompt", default_prompt
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Erro ao preparar prompts para checkpoint {checkpoint}: {result.stderr}")

        return prompts_file

    def evaluate_checkpoint(self,
                           checkpoint: int,
                           checkpoint_dir: Path,
                           calculate_fid: bool = True,
                           calculate_clip: bool = True) -> Dict:
        """
        Avalia um checkpoint especifico calculando metricas.

        Args:
            checkpoint: Numero do checkpoint
            checkpoint_dir: Diretorio contendo imagens do checkpoint
            calculate_fid: Se deve calcular FID
            calculate_clip: Se deve calcular CLIP Score

        Returns:
            Dicionario com resultados da avaliacao
        """
        print(f"\n{'='*70}")
        print(f"AVALIANDO CHECKPOINT {checkpoint}")
        print(f"{'='*70}")

        metrics_file = self.output_dir / f"metrics_checkpoint_{checkpoint}.json"

        # Prepara prompts se CLIP Score for calculado
        prompts_file = None
        if calculate_clip:
            print("  [1/2] Preparando prompts...")
            prompts_file = self.prepare_prompts_for_checkpoint(checkpoint, checkpoint_dir)

        # Calcula metricas
        print(f"  [2/2] Calculando metricas (FID={calculate_fid}, CLIP={calculate_clip})...")

        cmd = [
            sys.executable,
            "calculate_metrics.py",
            "--real_images_dir", str(self.real_images_dir),
            "--generated_images_dir", str(checkpoint_dir),
            "--output_file", str(metrics_file),
            "--device", "auto",
            "--batch_size", "16"
        ]

        if not calculate_fid:
            cmd.append("--skip_fid")

        if not calculate_clip:
            cmd.append("--skip_clip")
        elif prompts_file:
            cmd.extend(["--prompts_file", str(prompts_file)])

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"  [ERRO] Falha ao calcular metricas: {result.stderr}")
            return None

        # Le resultados
        with open(metrics_file, 'r') as f:
            metrics = json.load(f)

        # Exibe resumo
        if 'fid' in metrics:
            print(f"  FID Score: {metrics['fid']['score']:.2f} ({metrics['fid']['interpretation']})")

        if 'clip_score' in metrics:
            print(f"  CLIP Score: {metrics['clip_score']['mean']:.2f} ± {metrics['clip_score']['std']:.2f} ({metrics['clip_score']['interpretation']})")

        return metrics

    def generate_comparative_report(self, results: Dict) -> str:
        """
        Gera relatorio comparativo em formato Markdown.

        Args:
            results: Dicionario com resultados de todos os checkpoints

        Returns:
            String contendo o relatorio em Markdown
        """
        report = []

        report.append("# Relatorio de Avaliacao Formal de Checkpoints")
        report.append("")
        report.append(f"**Data da Avaliacao**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Dataset Real**: {self.real_images_dir}")
        report.append(f"**Checkpoints Avaliados**: {len(results)}")
        report.append("")

        # Tabela comparativa
        report.append("## Resumo Comparativo")
        report.append("")
        report.append("| Checkpoint | FID Score | CLIP Score | Num. Imagens | Interpretacao |")
        report.append("|------------|-----------|------------|--------------|---------------|")

        # Ordena por checkpoint
        sorted_checkpoints = sorted(results.keys())

        for ckpt in sorted_checkpoints:
            data = results[ckpt]

            if data is None:
                report.append(f"| {ckpt} | N/A | N/A | 0 | Erro na avaliacao |")
                continue

            fid = data.get('fid', {}).get('score', 'N/A')
            fid_str = f"{fid:.2f}" if isinstance(fid, (int, float)) else fid

            clip = data.get('clip_score', {}).get('mean', 'N/A')
            clip_std = data.get('clip_score', {}).get('std', 0)
            clip_str = f"{clip:.2f} ± {clip_std:.2f}" if isinstance(clip, (int, float)) else clip

            num_images = data.get('metadata', {}).get('generated_images_count', 0)

            # Interpretacao geral
            if isinstance(fid, (int, float)) and isinstance(clip, (int, float)):
                if fid < 20 and clip > 27:
                    interp = "Excelente"
                elif fid < 50 and clip > 25:
                    interp = "Bom"
                elif fid > 100:
                    interp = "Qualidade Baixa"
                elif clip < 20:
                    interp = "Alinhamento Ruim"
                else:
                    interp = "Razoavel"
            else:
                interp = "N/A"

            report.append(f"| {ckpt} | {fid_str} | {clip_str} | {num_images} | {interp} |")

        report.append("")

        # Analise detalhada
        report.append("## Analise Detalhada")
        report.append("")

        # Melhor FID
        fid_scores = {ckpt: data.get('fid', {}).get('score')
                      for ckpt, data in results.items()
                      if data and 'fid' in data}

        if fid_scores:
            valid_fid = {k: v for k, v in fid_scores.items() if v is not None}
            if valid_fid:
                best_fid_ckpt = min(valid_fid, key=valid_fid.get)
                best_fid_score = valid_fid[best_fid_ckpt]
                report.append(f"### Melhor FID Score")
                report.append(f"**Checkpoint {best_fid_ckpt}**: FID = {best_fid_score:.2f}")
                report.append("")
                report.append("O FID (Frechet Inception Distance) mede a qualidade e diversidade das imagens.")
                report.append("Valores menores indicam maior similaridade com o dataset real.")
                report.append("")

        # Melhor CLIP
        clip_scores = {ckpt: data.get('clip_score', {}).get('mean')
                       for ckpt, data in results.items()
                       if data and 'clip_score' in data}

        if clip_scores:
            valid_clip = {k: v for k, v in clip_scores.items() if v is not None}
            if valid_clip:
                best_clip_ckpt = max(valid_clip, key=valid_clip.get)
                best_clip_score = valid_clip[best_clip_ckpt]
                best_clip_std = results[best_clip_ckpt]['clip_score']['std']
                report.append(f"### Melhor CLIP Score")
                report.append(f"**Checkpoint {best_clip_ckpt}**: CLIP = {best_clip_score:.2f} ± {best_clip_std:.2f}")
                report.append("")
                report.append("O CLIP Score mede o alinhamento semantico entre prompts e imagens.")
                report.append("Valores maiores indicam melhor correspondencia texto-imagem.")
                report.append("")

        # Recomendacao final
        report.append("## Recomendacao para Producao")
        report.append("")

        if fid_scores and clip_scores and valid_fid and valid_clip:
            # Checkpoint que aparece em ambos top 3
            top_fid = sorted(valid_fid.items(), key=lambda x: x[1])[:3]
            top_clip = sorted(valid_clip.items(), key=lambda x: x[1], reverse=True)[:3]

            top_fid_ckpts = [ckpt for ckpt, _ in top_fid]
            top_clip_ckpts = [ckpt for ckpt, _ in top_clip]

            # Checkpoint que aparece em ambos
            common = set(top_fid_ckpts) & set(top_clip_ckpts)

            if common:
                recommended = min(common, key=lambda x: valid_fid[x])  # Entre os comuns, menor FID
                report.append(f"**Checkpoint Recomendado: {recommended}**")
                report.append("")
                report.append(f"- FID Score: {valid_fid[recommended]:.2f}")
                report.append(f"- CLIP Score: {valid_clip[recommended]:.2f}")
                report.append("")
                report.append("Este checkpoint oferece o melhor equilibrio entre qualidade visual (FID) ")
                report.append("e alinhamento semantico (CLIP Score).")
            else:
                # Se nao ha comum, prioriza FID
                report.append(f"**Checkpoint Recomendado para Qualidade Visual: {best_fid_ckpt}**")
                report.append(f"**Checkpoint Recomendado para Alinhamento Texto: {best_clip_ckpt}**")
                report.append("")
                report.append("Nao ha checkpoint que se destaque em ambas metricas simultaneamente.")
                report.append("Considere o trade-off entre qualidade visual e alinhamento semantico.")

        report.append("")
        report.append("## Metodologia")
        report.append("")
        report.append("### FID (Frechet Inception Distance)")
        report.append("- Extrai features usando Inception v3 pre-treinado")
        report.append("- Calcula distancia de Frechet entre distribuicoes")
        report.append("- Interpretacao: < 10 = Excelente, < 20 = Muito Bom, < 50 = Bom")
        report.append("")
        report.append("### CLIP Score")
        report.append("- Usa modelo CLIP (OpenAI) para embeddings multimodais")
        report.append("- Calcula similaridade coseno entre texto e imagem")
        report.append("- Interpretacao: > 30 = Excelente, > 27 = Muito Bom, > 25 = Bom")
        report.append("")

        return "\n".join(report)

    def run_evaluation(self,
                      calculate_fid: bool = True,
                      calculate_clip: bool = True) -> Dict:
        """
        Executa avaliacao completa de todos os checkpoints.

        Args:
            calculate_fid: Se deve calcular FID
            calculate_clip: Se deve calcular CLIP Score

        Returns:
            Dicionario com resultados de todos os checkpoints
        """
        print("\n" + "="*70)
        print("AVALIACAO FORMAL DE CHECKPOINTS - INICIO")
        print("="*70)
        print(f"Dataset Real: {self.real_images_dir}")
        print(f"Validacao Base: {self.validation_base_dir}")
        print(f"Saida: {self.output_dir}")
        print(f"Metricas: FID={calculate_fid}, CLIP={calculate_clip}")

        # Verifica disponibilidade
        availability = self.verify_checkpoint_availability()

        # Avalia cada checkpoint disponivel
        results = {}

        for ckpt, info in availability.items():
            if not info['available']:
                print(f"\nPulando checkpoint {ckpt}: {info['reason']}")
                results[ckpt] = None
                continue

            try:
                metrics = self.evaluate_checkpoint(
                    ckpt,
                    info['path'],
                    calculate_fid=calculate_fid,
                    calculate_clip=calculate_clip
                )
                results[ckpt] = metrics
            except Exception as e:
                print(f"  [ERRO] Falha ao avaliar checkpoint {ckpt}: {e}")
                results[ckpt] = None

        # Salva resultados consolidados
        consolidated_file = self.output_dir / "consolidated_results.json"
        with open(consolidated_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n{'='*70}")
        print(f"Resultados consolidados salvos em: {consolidated_file}")

        # Gera relatorio comparativo
        report = self.generate_comparative_report(results)
        report_file = self.output_dir / "comparative_report.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"Relatorio comparativo salvo em: {report_file}")
        print("="*70)

        return results


def main():
    parser = argparse.ArgumentParser(
        description='Avaliacao formal e automatizada de checkpoints LoRA'
    )

    parser.add_argument(
        '--real_images_dir',
        type=str,
        required=True,
        help='Diretorio contendo imagens reais do dataset'
    )

    parser.add_argument(
        '--validation_base_dir',
        type=str,
        required=True,
        help='Diretorio base contendo subdiretorios checkpoint-N'
    )

    parser.add_argument(
        '--output_dir',
        type=str,
        default='./checkpoint_evaluation_results',
        help='Diretorio para salvar resultados (default: ./checkpoint_evaluation_results)'
    )

    parser.add_argument(
        '--checkpoints',
        type=int,
        nargs='+',
        default=None,
        help='Lista de checkpoints a avaliar (default: 500 1000 1500 2000 2500 3000)'
    )

    parser.add_argument(
        '--skip_fid',
        action='store_true',
        help='Pula calculo de FID (mais rapido)'
    )

    parser.add_argument(
        '--skip_clip',
        action='store_true',
        help='Pula calculo de CLIP Score (mais rapido)'
    )

    args = parser.parse_args()

    # Cria avaliador
    evaluator = CheckpointEvaluator(
        real_images_dir=args.real_images_dir,
        validation_base_dir=args.validation_base_dir,
        output_dir=args.output_dir,
        checkpoints=args.checkpoints
    )

    # Executa avaliacao
    results = evaluator.run_evaluation(
        calculate_fid=not args.skip_fid,
        calculate_clip=not args.skip_clip
    )

    # Exibe resumo final
    print("\n" + "="*70)
    print("AVALIACAO CONCLUIDA")
    print("="*70)

    successful = sum(1 for r in results.values() if r is not None)
    print(f"Checkpoints avaliados com sucesso: {successful}/{len(results)}")
    print(f"Resultados salvos em: {args.output_dir}")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
