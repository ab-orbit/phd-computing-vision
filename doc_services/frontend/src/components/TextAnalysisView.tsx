/**
 * Componente TextAnalysisView
 *
 * Exibe resultado do UC3: Análise de texto
 * Mostra contagem total de palavras e frequências das mais comuns
 */

import { BarChart3, TrendingUp, Type } from 'lucide-react';
import { TextAnalysis } from '@/types';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { FeedbackRating } from './FeedbackRating';

interface TextAnalysisViewProps {
  analysis: TextAnalysis;
  onFeedback?: (rating: 'positive' | 'negative', comment?: string) => void;
}

export function TextAnalysisView({ analysis, onFeedback }: TextAnalysisViewProps) {
  const { total_words, top_words } = analysis;

  /**
   * Preparar dados para o gráfico
   * Limitar aos top 15 para melhor visualização
   *
   * Explicação:
   * - top_words vem como array de objetos: [{word: "in", count: 25}, ...]
   */
  const chartData = top_words.slice(0, 15).map((item) => ({
    word: item.word,
    count: item.count,
  }));

  /**
   * Cores alternadas para as barras
   */
  const COLORS = ['#3b82f6', '#6366f1', '#8b5cf6', '#a855f7'];

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      {/* Cabeçalho */}
      <div className="flex items-center space-x-2 mb-4">
        <span className="text-xs font-mono px-2 py-0.5 rounded bg-primary-100 text-primary-700">UC3</span>
        <h3 className="text-lg font-semibold text-gray-900">Análise de Texto</h3>
      </div>

      {/* Métrica principal */}
      <div className="bg-gradient-to-r from-primary-50 to-purple-50 rounded-lg p-6 mb-6">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 bg-white rounded-full flex items-center justify-center">
            <Type className="w-6 h-6 text-primary-600" />
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Total de palavras</p>
            <p className="text-3xl font-bold text-gray-900">{total_words.toLocaleString()}</p>
          </div>
        </div>
      </div>

      {/* Palavras mais frequentes - Tabela */}
      <div className="mb-6">
        <div className="flex items-center space-x-2 mb-3">
          <TrendingUp className="w-5 h-5 text-primary-600" />
          <h4 className="text-base font-semibold text-gray-900">Top 15 Palavras Mais Frequentes</h4>
        </div>

        <div className="overflow-hidden rounded-lg border border-gray-200">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Posição
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Palavra
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Frequência
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  %
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {top_words.slice(0, 15).map((item, index) => {
                const percentage = ((item.count / total_words) * 100).toFixed(2);

                return (
                  <tr key={item.word} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="flex items-center">
                        <span
                          className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium"
                          style={{
                            backgroundColor: COLORS[index % COLORS.length] + '20',
                            color: COLORS[index % COLORS.length],
                          }}
                        >
                          {index + 1}
                        </span>
                      </div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <p className="text-sm font-medium text-gray-900">{item.word}</p>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-right">
                      <p className="text-sm text-gray-900">{item.count.toLocaleString()}</p>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-right">
                      <p className="text-sm text-gray-500">{percentage}%</p>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Gráfico de barras */}
      <div>
        <div className="flex items-center space-x-2 mb-3">
          <BarChart3 className="w-5 h-5 text-primary-600" />
          <h4 className="text-base font-semibold text-gray-900">Visualização das Frequências</h4>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis
                dataKey="word"
                angle={-45}
                textAnchor="end"
                height={80}
                tick={{ fontSize: 12, fill: '#6b7280' }}
              />
              <YAxis tick={{ fontSize: 12, fill: '#6b7280' }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#ffffff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '0.5rem',
                  fontSize: '14px',
                }}
                labelStyle={{ fontWeight: 600, color: '#111827' }}
              />
              <Bar dataKey="count" radius={[8, 8, 0, 0]}>
                {chartData.map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Estatísticas adicionais */}
      <div className="mt-6 grid grid-cols-3 gap-4">
        <div className="bg-gray-50 rounded-lg p-4 text-center">
          <p className="text-xs text-gray-600 mb-1">Palavras únicas</p>
          <p className="text-lg font-bold text-gray-900">{Object.keys(analysis.word_frequencies).length}</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4 text-center">
          <p className="text-xs text-gray-600 mb-1">Palavra mais comum</p>
          <p className="text-lg font-bold text-gray-900">{top_words[0]?.word || '-'}</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-4 text-center">
          <p className="text-xs text-gray-600 mb-1">Frequência máxima</p>
          <p className="text-lg font-bold text-gray-900">{top_words[0]?.count.toLocaleString() || 0}</p>
        </div>
      </div>

      {/* Feedback */}
      {onFeedback && (
        <div className="mt-6">
          <FeedbackRating
            title="A análise textual foi útil?"
            onSubmit={(rating, comment) => onFeedback(rating, comment)}
          />
        </div>
      )}
    </div>
  );
}
