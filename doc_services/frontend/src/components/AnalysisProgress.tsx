/**
 * Componente AnalysisProgress
 *
 * Visualiza o progresso da análise
 *
 * Explicação:
 * - API processa tudo de uma vez (UC1+UC2+UC3+UC4)
 * - Não são múltiplas chamadas sequenciais
 * - Estados: Uploading → Processing → Completed
 */

import { CheckCircle2, Loader2, XCircle, Upload, Cpu } from 'lucide-react';
import { clsx } from 'clsx';
import { AnalysisStage } from '@/types';

interface AnalysisProgressProps {
  stage: AnalysisStage;
  uploadProgress?: number;
  error?: string | null;
}

export function AnalysisProgress({ stage, uploadProgress = 0, error }: AnalysisProgressProps) {
  /**
   * Calcula progresso geral (0-100%)
   *
   * Explicação:
   * - Upload: 0-100% (conforme arquivo é enviado)
   * - Processing: 100% indeterminado (não sabemos quanto falta)
   * - Completed: 100%
   */
  const getProgress = (): number => {
    if (stage === AnalysisStage.UPLOADING) {
      return uploadProgress;
    }
    if (stage === AnalysisStage.PROCESSING) {
      return 100; // Upload completo, processando
    }
    if (stage === AnalysisStage.COMPLETED) {
      return 100;
    }
    return 0;
  };

  const progress = getProgress();

  /**
   * Mensagem de status
   */
  const getStatusMessage = (): string => {
    switch (stage) {
      case AnalysisStage.IDLE:
        return 'Aguardando documento';
      case AnalysisStage.UPLOADING:
        return 'Enviando documento para análise';
      case AnalysisStage.PROCESSING:
        return 'Processando documento (UC1 + UC2 + UC3 + UC4)';
      case AnalysisStage.COMPLETED:
        return 'Análise concluída com sucesso!';
      case AnalysisStage.ERROR:
        return 'Erro na análise';
      default:
        return '';
    }
  };

  return (
    <div className="w-full space-y-6">
      {/* Barra de progresso geral */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="font-medium text-text-primary">
            {getStatusMessage()}
          </span>
          {stage === AnalysisStage.UPLOADING && (
            <span className="text-text-muted">{Math.round(progress)}%</span>
          )}
        </div>

        <div className="w-full h-2 bg-border-default rounded-full overflow-hidden">
          <div
            className={clsx('h-full transition-all duration-300 ease-out', {
              'bg-brand-primary': stage !== AnalysisStage.ERROR,
              'bg-semantic-danger': stage === AnalysisStage.ERROR,
            })}
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Card de status visual */}
      <div className={clsx('p-6 rounded-parsey border-2 transition-all duration-base', {
        'bg-blue-50 border-brand-primary': stage === AnalysisStage.UPLOADING,
        'bg-violet-50 border-brand-emphasis': stage === AnalysisStage.PROCESSING,
        'bg-green-50 border-semantic-success': stage === AnalysisStage.COMPLETED,
        'bg-red-50 border-semantic-danger': stage === AnalysisStage.ERROR,
        'bg-parsey-white border-border-default': stage === AnalysisStage.IDLE,
      })}>
        <div className="flex items-start space-x-4">
          {/* Ícone */}
          <div className="flex-shrink-0">
            {stage === AnalysisStage.UPLOADING && (
              <Upload className="w-8 h-8 text-brand-primary animate-pulse" />
            )}
            {stage === AnalysisStage.PROCESSING && (
              <Cpu className="w-8 h-8 text-brand-emphasis animate-spin" />
            )}
            {stage === AnalysisStage.COMPLETED && (
              <CheckCircle2 className="w-8 h-8 text-semantic-success" />
            )}
            {stage === AnalysisStage.ERROR && (
              <XCircle className="w-8 h-8 text-semantic-danger" />
            )}
          </div>

          {/* Conteúdo */}
          <div className="flex-1">
            <p className="text-base font-display font-semibold text-text-primary mb-2">
              {getStatusMessage()}
            </p>

            {stage === AnalysisStage.UPLOADING && (
              <p className="text-sm text-text-muted">
                Enviando arquivo para o servidor... ({Math.round(progress)}%)
              </p>
            )}

            {stage === AnalysisStage.PROCESSING && (
              <div className="space-y-2">
                <p className="text-sm text-text-muted">
                  A API está processando o documento:
                </p>
                <div className="flex flex-wrap gap-2 mt-2">
                  <span className="px-2 py-1 text-xs font-medium bg-green-50 rounded-lg border border-green-500 text-green-700">
                    UC1: Classificação (implementado)
                  </span>
                  <span className="px-2 py-1 text-xs font-medium bg-amber-50 rounded-lg border border-amber-400 text-amber-700">
                    UC2: Parágrafos (em desenvolvimento)
                  </span>
                  <span className="px-2 py-1 text-xs font-medium bg-amber-50 rounded-lg border border-amber-400 text-amber-700">
                    UC3: Análise Textual (em desenvolvimento)
                  </span>
                  <span className="px-2 py-1 text-xs font-medium bg-amber-50 rounded-lg border border-amber-400 text-amber-700">
                    UC4: Conformidade (em desenvolvimento)
                  </span>
                </div>
                <p className="text-xs text-text-muted mt-2">
                  Aguarde... O tempo de processamento depende do tamanho do documento.
                </p>
              </div>
            )}

            {stage === AnalysisStage.COMPLETED && (
              <div className="space-y-2">
                <p className="text-sm text-green-700 font-medium">
                  UC1 (Classificação) executado com sucesso!
                </p>
                <p className="text-xs text-text-muted">
                  UC2, UC3 e UC4 estarão disponíveis quando o backend implementar o endpoint completo.
                  Confira os resultados de classificação abaixo.
                </p>
              </div>
            )}

            {stage === AnalysisStage.ERROR && error && (
              <div className="mt-2 space-y-2">
                <p className="text-sm font-medium text-red-800">Detalhes do erro:</p>
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
