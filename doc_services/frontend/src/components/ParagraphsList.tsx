/**
 * Componente ParagraphsList
 *
 * Exibe resultado do UC2: Lista de parágrafos detectados
 * Mostra os parágrafos extraídos pelo docling com suas métricas
 */

import { FileText, Hash, Type } from 'lucide-react';
import { Paragraph } from '@/types';
import { useState } from 'react';
import { FeedbackRating } from './FeedbackRating';

interface ParagraphsListProps {
  paragraphs: Paragraph[];
  onFeedback?: (rating: 'positive' | 'negative', comment?: string) => void;
}

export function ParagraphsList({ paragraphs, onFeedback }: ParagraphsListProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const totalWords = paragraphs.reduce((sum, p) => sum + p.word_count, 0);

  /**
   * Toggle expansão de parágrafo
   */
  const toggleParagraph = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  /**
   * Truncar texto longo
   */
  const truncateText = (text: string, maxLength: number = 150): string => {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '...';
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      {/* Cabeçalho */}
      <div className="flex items-center space-x-2 mb-4">
        <span className="text-xs font-mono px-2 py-0.5 rounded bg-primary-100 text-primary-700">UC2</span>
        <h3 className="text-lg font-semibold text-gray-900">Parágrafos Detectados</h3>
      </div>

      {/* Métricas resumidas */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-1">
            <Hash className="w-4 h-4 text-gray-600" />
            <p className="text-sm text-gray-600">Total de parágrafos</p>
          </div>
          <p className="text-2xl font-bold text-gray-900">{paragraphs.length}</p>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-1">
            <Type className="w-4 h-4 text-gray-600" />
            <p className="text-sm text-gray-600">Total de palavras</p>
          </div>
          <p className="text-2xl font-bold text-gray-900">{totalWords.toLocaleString()}</p>
        </div>
      </div>

      {/* Lista de parágrafos */}
      <div className="space-y-3">
        {paragraphs.map((paragraph) => {
          const isExpanded = expandedIndex === paragraph.index;

          return (
            <div key={paragraph.index} className="border border-gray-200 rounded-lg overflow-hidden hover:border-primary-300 transition-colors">
              {/* Cabeçalho do parágrafo */}
              <button
                onClick={() => toggleParagraph(paragraph.index)}
                className="w-full p-4 text-left hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-primary-700">{paragraph.index + 1}</span>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">Parágrafo {paragraph.index + 1}</p>
                      <p className="text-xs text-gray-500">{paragraph.word_count} palavras</p>
                    </div>
                  </div>
                  <FileText className="w-5 h-5 text-gray-400" />
                </div>

                {/* Preview do texto (quando fechado) */}
                {!isExpanded && (
                  <p className="text-sm text-gray-600 mt-3 line-clamp-2">{truncateText(paragraph.text)}</p>
                )}
              </button>

              {/* Conteúdo expandido */}
              {isExpanded && (
                <div className="px-4 pb-4 border-t border-gray-200 bg-gray-50">
                  <div className="pt-4 space-y-3">
                    {/* Texto completo */}
                    <div>
                      <p className="text-xs font-medium text-gray-600 mb-2">Texto completo:</p>
                      <p className="text-sm text-gray-900 leading-relaxed whitespace-pre-wrap">{paragraph.text}</p>
                    </div>

                    {/* Métricas */}
                    <div className="flex items-center space-x-4 text-xs text-gray-600">
                      <div className="flex items-center space-x-1">
                        <Type className="w-3 h-3" />
                        <span>{paragraph.word_count} palavras</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <FileText className="w-3 h-3" />
                        <span>{paragraph.text.length} caracteres</span>
                      </div>
                    </div>

                    {/* Bounding box (se disponível) */}
                    {paragraph.bbox && (
                      <div className="text-xs text-gray-500">
                        <p>Posição: x={paragraph.bbox.x}, y={paragraph.bbox.y}, w={paragraph.bbox.width}, h={paragraph.bbox.height}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Mensagem se não houver parágrafos */}
      {paragraphs.length === 0 && (
        <div className="text-center py-8">
          <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-sm text-gray-600">Nenhum parágrafo detectado</p>
        </div>
      )}

      {/* Feedback */}
      {onFeedback && paragraphs.length > 0 && (
        <div className="mt-6">
          <FeedbackRating
            title="A detecção de parágrafos foi precisa?"
            onSubmit={(rating, comment) => onFeedback(rating, comment)}
          />
        </div>
      )}
    </div>
  );
}
