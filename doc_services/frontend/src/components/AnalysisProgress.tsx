/**
 * Componente AnalysisProgress
 *
 * Visualiza o progresso da análise com simulação de fases
 *
 * Explicação:
 * - API processa tudo de uma vez (20-30s)
 * - Simulamos progresso por UCs para melhor feedback visual
 * - Distribuição estimada: UC1(25%) → UC2(35%) → UC3(20%) → UC4(20%)
 */

import { useState, useEffect } from 'react';
import { CheckCircle2, XCircle, Upload, FileSearch, Brain, BarChart3, CheckSquare } from 'lucide-react';
import { clsx } from 'clsx';
import { AnalysisStage } from '@/types';

interface AnalysisProgressProps {
  stage: AnalysisStage;
  uploadProgress?: number;
  error?: string | null;
}

interface ProcessingPhase {
  id: 'uc1' | 'uc2' | 'uc3' | 'uc4';
  name: string;
  description: string;
  icon: any;
  percentage: number;
}

const PHASES: ProcessingPhase[] = [
  {
    id: 'uc1',
    name: 'UC1: Classificação',
    description: 'Identificando tipo de documento com LLM',
    icon: FileSearch,
    percentage: 25,
  },
  {
    id: 'uc2',
    name: 'UC2: Detecção de Parágrafos',
    description: 'Extraindo estrutura do documento com Docling',
    icon: Brain,
    percentage: 35,
  },
  {
    id: 'uc3',
    name: 'UC3: Análise Textual',
    description: 'Processando frequência de palavras',
    icon: BarChart3,
    percentage: 20,
  },
  {
    id: 'uc4',
    name: 'UC4: Conformidade',
    description: 'Validando requisitos do documento',
    icon: CheckSquare,
    percentage: 20,
  },
];

export function AnalysisProgress({ stage, uploadProgress = 0, error }: AnalysisProgressProps) {
  const [currentPhaseIndex, setCurrentPhaseIndex] = useState(0);
  const [phaseProgress, setPhaseProgress] = useState(0);

  /**
   * Simula progresso através das fases durante o processamento
   *
   * Explicação:
   * - Cada fase tem duração proporcional à sua porcentagem
   * - Total estimado: 25 segundos (médio entre 20-30s)
   * - UC1: 6.25s, UC2: 8.75s, UC3: 5s, UC4: 5s
   */
  useEffect(() => {
    if (stage !== AnalysisStage.PROCESSING) {
      setCurrentPhaseIndex(0);
      setPhaseProgress(0);
      return;
    }

    const totalDuration = 25000; // 25 segundos
    let elapsedTime = 0;
    const updateInterval = 100; // Atualizar a cada 100ms

    const timer = setInterval(() => {
      elapsedTime += updateInterval;

      // Calcular progresso acumulado
      let cumulativePercentage = 0;
      let currentIndex = 0;

      for (let i = 0; i < PHASES.length; i++) {
        const phaseStart = cumulativePercentage;
        const phaseEnd = cumulativePercentage + PHASES[i].percentage;

        const currentProgress = Math.min((elapsedTime / totalDuration) * 100, 100);

        if (currentProgress >= phaseStart && currentProgress < phaseEnd) {
          currentIndex = i;
          const phaseLocalProgress = ((currentProgress - phaseStart) / PHASES[i].percentage) * 100;
          setPhaseProgress(Math.min(phaseLocalProgress, 100));
          break;
        }

        cumulativePercentage = phaseEnd;
      }

      setCurrentPhaseIndex(currentIndex);

      // Parar quando atingir 100%
      if (elapsedTime >= totalDuration) {
        clearInterval(timer);
        setCurrentPhaseIndex(3);
        setPhaseProgress(100);
      }
    }, updateInterval);

    return () => clearInterval(timer);
  }, [stage]);

  /**
   * Calcula progresso geral (0-100%)
   */
  const getProgress = (): number => {
    if (stage === AnalysisStage.UPLOADING) {
      return uploadProgress;
    }
    if (stage === AnalysisStage.PROCESSING) {
      // Calcular progresso baseado na fase atual
      let cumulativeProgress = 0;
      for (let i = 0; i < currentPhaseIndex; i++) {
        cumulativeProgress += PHASES[i].percentage;
      }
      cumulativeProgress += (PHASES[currentPhaseIndex].percentage * phaseProgress) / 100;
      return Math.min(cumulativeProgress, 100);
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
        return PHASES[currentPhaseIndex].description;
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
          {(stage === AnalysisStage.UPLOADING || stage === AnalysisStage.PROCESSING) && (
            <span className="text-text-muted font-mono">{Math.round(progress)}%</span>
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

      {/* Timeline de fases - Durante processamento */}
      {stage === AnalysisStage.PROCESSING && (
        <div className="bg-gradient-to-br from-violet-50 to-blue-50 rounded-parsey border-2 border-brand-primary p-6">
          <div className="space-y-4">
            {PHASES.map((phase, index) => {
              const PhaseIcon = phase.icon;
              const isCompleted = index < currentPhaseIndex;
              const isCurrent = index === currentPhaseIndex;
              const isPending = index > currentPhaseIndex;

              return (
                <div
                  key={phase.id}
                  className={clsx(
                    'flex items-start space-x-4 p-4 rounded-lg transition-all duration-500',
                    {
                      'bg-white shadow-md border-2 border-brand-primary scale-105': isCurrent,
                      'bg-green-50 border border-green-300': isCompleted,
                      'bg-white border border-border-subtle opacity-60': isPending,
                    }
                  )}
                >
                  {/* Ícone */}
                  <div className="flex-shrink-0">
                    {isCompleted ? (
                      <div className="w-10 h-10 rounded-full bg-green-500 flex items-center justify-center">
                        <CheckCircle2 className="w-6 h-6 text-white" />
                      </div>
                    ) : isCurrent ? (
                      <div className="w-10 h-10 rounded-full bg-brand-primary flex items-center justify-center animate-pulse">
                        <PhaseIcon className="w-6 h-6 text-white animate-spin" />
                      </div>
                    ) : (
                      <div className="w-10 h-10 rounded-full bg-border-default flex items-center justify-center">
                        <PhaseIcon className="w-6 h-6 text-text-muted" />
                      </div>
                    )}
                  </div>

                  {/* Conteúdo */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <p className={clsx('text-sm font-semibold', {
                        'text-green-700': isCompleted,
                        'text-brand-emphasis': isCurrent,
                        'text-text-muted': isPending,
                      })}>
                        {phase.name}
                      </p>
                      {isCurrent && (
                        <span className="text-xs font-mono text-brand-primary">
                          {Math.round(phaseProgress)}%
                        </span>
                      )}
                      {isCompleted && (
                        <span className="text-xs font-medium text-green-600">
                          Concluído
                        </span>
                      )}
                    </div>
                    <p className={clsx('text-xs', {
                      'text-green-600': isCompleted,
                      'text-text-primary': isCurrent,
                      'text-text-muted': isPending,
                    })}>
                      {phase.description}
                    </p>

                    {/* Barra de progresso da fase */}
                    {isCurrent && (
                      <div className="mt-2 w-full h-1 bg-border-default rounded-full overflow-hidden">
                        <div
                          className="h-full bg-brand-primary transition-all duration-300"
                          style={{ width: `${phaseProgress}%` }}
                        />
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-4 p-3 bg-blue-100 border border-blue-300 rounded-lg">
            <p className="text-xs text-blue-800 text-center font-medium">
              A análise está em andamento. Tempo estimado: 20-30 segundos
            </p>
          </div>
        </div>
      )}

      {/* Card de upload */}
      {stage === AnalysisStage.UPLOADING && (
        <div className="bg-blue-50 rounded-parsey border-2 border-brand-primary p-6">
          <div className="flex items-start space-x-4">
            <Upload className="w-8 h-8 text-brand-primary animate-pulse flex-shrink-0" />
            <div className="flex-1">
              <p className="text-base font-display font-semibold text-text-primary mb-2">
                Enviando documento para análise
              </p>
              <p className="text-sm text-text-muted">
                Enviando arquivo para o servidor... ({Math.round(progress)}%)
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Card de sucesso */}
      {stage === AnalysisStage.COMPLETED && (
        <div className="bg-green-50 rounded-parsey border-2 border-semantic-success p-6">
          <div className="flex items-start space-x-4">
            <CheckCircle2 className="w-8 h-8 text-semantic-success flex-shrink-0" />
            <div className="flex-1">
              <p className="text-base font-display font-semibold text-green-700 mb-2">
                Todos os casos de uso executados com sucesso!
              </p>
              <p className="text-sm text-green-600">
                UC1 (Classificação) + UC2 (Parágrafos) + UC3 (Análise Textual) + UC4 (Conformidade)
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Card de erro */}
      {stage === AnalysisStage.ERROR && error && (
        <div className="bg-red-50 rounded-parsey border-2 border-semantic-danger p-6">
          <div className="flex items-start space-x-4">
            <XCircle className="w-8 h-8 text-semantic-danger flex-shrink-0" />
            <div className="flex-1">
              <p className="text-base font-display font-semibold text-red-800 mb-2">
                Erro na análise
              </p>
              <p className="text-sm text-red-600">{error}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
