/**
 * Componente ComplianceReportView
 *
 * Exibe resultado do UC4: Relatório de conformidade
 * Mostra se o documento atende às regras (2000 palavras, 8 parágrafos)
 */

import { CheckCircle, XCircle, AlertTriangle, FileCheck, Download } from 'lucide-react';
import { ComplianceReport } from '@/types';
import ReactMarkdown from 'react-markdown';
import { clsx } from 'clsx';
import { FeedbackRating } from './FeedbackRating';

interface ComplianceReportViewProps {
  report: ComplianceReport;
  onFeedback?: (rating: 'positive' | 'negative', comment?: string) => void;
}

export function ComplianceReportView({ report, onFeedback }: ComplianceReportViewProps) {
  const {
    file_name,
    word_count,
    paragraph_count,
    is_compliant,
    words_compliant,
    paragraphs_compliant,
    words_status,
    paragraphs_status,
    overall_status,
    recommended_actions,
    report_markdown,
  } = report;

  /**
   * Calcular diferenças das metas
   */
  const wordsDiff = word_count - 2000;
  const paragraphsDiff = paragraph_count - 8;

  /**
   * Handler para download do relatório
   */
  const handleDownload = () => {
    const blob = new Blob([report_markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `relatorio_conformidade_${file_name.replace(/\.[^/.]+$/, '')}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      {/* Cabeçalho */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-mono px-2 py-0.5 rounded bg-primary-100 text-primary-700">UC4</span>
          <h3 className="text-lg font-semibold text-gray-900">Relatório de Conformidade</h3>
        </div>

        {/* Botão de download */}
        <button
          onClick={handleDownload}
          className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Download className="w-4 h-4" />
          <span className="text-sm font-medium">Baixar Relatório</span>
        </button>
      </div>

      {/* Status Geral */}
      <div
        className={clsx('rounded-lg p-6 mb-6', {
          'bg-green-50 border border-green-200': is_compliant,
          'bg-red-50 border border-red-200': !is_compliant,
        })}
      >
        <div className="flex items-start space-x-4">
          <div
            className={clsx('w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0', {
              'bg-green-100': is_compliant,
              'bg-red-100': !is_compliant,
            })}
          >
            {is_compliant ? (
              <CheckCircle className="w-6 h-6 text-green-600" />
            ) : (
              <XCircle className="w-6 h-6 text-red-600" />
            )}
          </div>
          <div className="flex-1">
            <h4
              className={clsx('text-xl font-bold mb-2', {
                'text-green-900': is_compliant,
                'text-red-900': !is_compliant,
              })}
            >
              Documento {overall_status}
            </h4>
            <p
              className={clsx('text-sm', {
                'text-green-700': is_compliant,
                'text-red-700': !is_compliant,
              })}
            >
              {is_compliant
                ? 'O documento atende a todas as regras de conformidade estabelecidas.'
                : 'O documento não atende às regras de conformidade. Veja as ações recomendadas abaixo.'}
            </p>
          </div>
        </div>
      </div>

      {/* Métricas e Regras */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Palavras */}
        <div className={clsx('rounded-lg border-2 p-5', {
          'border-green-200 bg-green-50': words_compliant,
          'border-red-200 bg-red-50': !words_compliant,
        })}>
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Palavras</p>
              <p className="text-3xl font-bold text-gray-900">{word_count.toLocaleString()}</p>
            </div>
            <div className={clsx('w-10 h-10 rounded-full flex items-center justify-center', {
              'bg-green-100': words_compliant,
              'bg-red-100': !words_compliant,
            })}>
              {words_compliant ? (
                <CheckCircle className="w-5 h-5 text-green-600" />
              ) : (
                <XCircle className="w-5 h-5 text-red-600" />
              )}
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Mínimo exigido:</span>
              <span className="font-medium text-gray-900">2,000</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Diferença:</span>
              <span
                className={clsx('font-medium', {
                  'text-green-600': wordsDiff >= 0,
                  'text-red-600': wordsDiff < 0,
                })}
              >
                {wordsDiff >= 0 ? '+' : ''}{wordsDiff.toLocaleString()}
              </span>
            </div>
            <div className="pt-2">
              <span
                className={clsx('inline-block px-3 py-1 rounded-full text-xs font-medium', {
                  'bg-green-100 text-green-700': words_compliant,
                  'bg-red-100 text-red-700': !words_compliant,
                })}
              >
                {words_status}
              </span>
            </div>
          </div>
        </div>

        {/* Parágrafos */}
        <div className={clsx('rounded-lg border-2 p-5', {
          'border-green-200 bg-green-50': paragraphs_compliant,
          'border-red-200 bg-red-50': !paragraphs_compliant,
        })}>
          <div className="flex items-start justify-between mb-4">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">Parágrafos</p>
              <p className="text-3xl font-bold text-gray-900">{paragraph_count}</p>
            </div>
            <div className={clsx('w-10 h-10 rounded-full flex items-center justify-center', {
              'bg-green-100': paragraphs_compliant,
              'bg-red-100': !paragraphs_compliant,
            })}>
              {paragraphs_compliant ? (
                <CheckCircle className="w-5 h-5 text-green-600" />
              ) : (
                <XCircle className="w-5 h-5 text-red-600" />
              )}
            </div>
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Exigido:</span>
              <span className="font-medium text-gray-900">8</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Diferença:</span>
              <span
                className={clsx('font-medium', {
                  'text-green-600': paragraphsDiff === 0,
                  'text-amber-600': paragraphsDiff > 0,
                  'text-red-600': paragraphsDiff < 0,
                })}
              >
                {paragraphsDiff > 0 ? '+' : ''}{paragraphsDiff}
              </span>
            </div>
            <div className="pt-2">
              <span
                className={clsx('inline-block px-3 py-1 rounded-full text-xs font-medium', {
                  'bg-green-100 text-green-700': paragraphs_compliant,
                  'bg-red-100 text-red-700': !paragraphs_compliant,
                })}
              >
                {paragraphs_status}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Ações Recomendadas */}
      {!is_compliant && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-5 mb-6">
          <div className="flex items-start space-x-3 mb-4">
            <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="text-base font-semibold text-amber-900 mb-1">Ações Recomendadas</h4>
              <p className="text-sm text-amber-700">Para tornar o documento conforme, realize as seguintes ações:</p>
            </div>
          </div>

          <div className="space-y-3">
            {recommended_actions.words_action !== 'Nenhuma ação necessária' && (
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-amber-600 rounded-full mt-2 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-amber-900">Palavras:</p>
                  <p className="text-sm text-amber-700">{recommended_actions.words_action}</p>
                </div>
              </div>
            )}

            {recommended_actions.paragraphs_action !== 'Nenhuma ação necessária' && (
              <div className="flex items-start space-x-3">
                <div className="w-2 h-2 bg-amber-600 rounded-full mt-2 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-amber-900">Parágrafos:</p>
                  <p className="text-sm text-amber-700">{recommended_actions.paragraphs_action}</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Relatório Markdown */}
      <div className="border border-gray-200 rounded-lg p-5 bg-gray-50">
        <div className="flex items-center space-x-2 mb-4">
          <FileCheck className="w-5 h-5 text-primary-600" />
          <h4 className="text-base font-semibold text-gray-900">Relatório Completo</h4>
        </div>

        <div className="prose prose-sm max-w-none bg-white rounded-lg p-4">
          <ReactMarkdown>{report_markdown}</ReactMarkdown>
        </div>
      </div>

      {/* Feedback */}
      {onFeedback && (
        <div className="mt-6">
          <FeedbackRating
            title="O relatório de conformidade foi claro?"
            onSubmit={(rating, comment) => onFeedback(rating, comment)}
          />
        </div>
      )}
    </div>
  );
}
