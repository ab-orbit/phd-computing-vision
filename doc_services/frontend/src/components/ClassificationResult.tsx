/**
 * Componente ClassificationResult
 *
 * Exibe resultado do UC1: Classificação do documento
 * Mostra se o documento é um artigo científico ou não
 */

import { CheckCircle, XCircle, FileText } from 'lucide-react';
import { ClassificationResult as ClassificationData } from '@/types';
import { clsx } from 'clsx';
import { FeedbackRating } from './FeedbackRating';

interface ClassificationResultProps {
  classification: ClassificationData;
  onFeedback?: (rating: 'positive' | 'negative', comment?: string) => void;
}

export function ClassificationResult({ classification, onFeedback }: ClassificationResultProps) {
  const { is_scientific_paper, document_type, confidence } = classification;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-start space-x-4">
        {/* Ícone */}
        <div
          className={clsx('w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0', {
            'bg-green-100': is_scientific_paper,
            'bg-red-100': !is_scientific_paper,
          })}
        >
          {is_scientific_paper ? (
            <CheckCircle className="w-6 h-6 text-green-600" />
          ) : (
            <XCircle className="w-6 h-6 text-red-600" />
          )}
        </div>

        {/* Conteúdo */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-primary-100 text-primary-700">UC1</span>
            <h3 className="text-lg font-semibold text-gray-900">Classificação do Documento</h3>
          </div>

          <div className="space-y-3">
            {/* Status principal */}
            <div>
              <p className="text-sm text-gray-600 mb-1">Status:</p>
              <p
                className={clsx('text-lg font-medium', {
                  'text-green-700': is_scientific_paper,
                  'text-red-700': !is_scientific_paper,
                })}
              >
                {is_scientific_paper ? 'Artigo científico válido' : 'Não é artigo científico'}
              </p>
            </div>

            {/* Tipo do documento */}
            <div>
              <p className="text-sm text-gray-600 mb-1">Tipo do documento:</p>
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4 text-gray-400" />
                <p className="text-base font-medium text-gray-900 capitalize">{document_type.replace('_', ' ')}</p>
              </div>
            </div>

            {/* Confiança */}
            <div>
              <p className="text-sm text-gray-600 mb-2">Confiança:</p>
              <div className="space-y-1">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-700">{Math.round(confidence * 100)}%</span>
                  <span className="text-gray-500">
                    {confidence >= 0.8 ? 'Alta' : confidence >= 0.5 ? 'Média' : 'Baixa'}
                  </span>
                </div>
                <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className={clsx('h-full transition-all duration-300', {
                      'bg-green-600': confidence >= 0.8,
                      'bg-yellow-500': confidence >= 0.5 && confidence < 0.8,
                      'bg-red-600': confidence < 0.5,
                    })}
                    style={{ width: `${confidence * 100}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Aviso se não for artigo científico */}
            {!is_scientific_paper && (
              <div className="mt-4 p-4 bg-amber-50 border border-amber-200 rounded-lg">
                <p className="text-sm text-amber-800">
                  <strong>Atenção:</strong> O documento não foi identificado como artigo científico. A análise
                  subsequente pode não ser relevante para este tipo de documento.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Feedback */}
      {onFeedback && (
        <div className="mt-4">
          <FeedbackRating
            title="Este resultado de classificação foi útil?"
            onSubmit={(rating, comment) => onFeedback(rating, comment)}
          />
        </div>
      )}
    </div>
  );
}
