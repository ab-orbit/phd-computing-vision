/**
 * Componente App Principal
 *
 * Aplicação para análise de documentos científicos
 * Integra todos os 4 casos de uso (UC1-UC4)
 */

import { useState, useMemo } from 'react';
import { FileText, RefreshCw, AlertCircle, ExternalLink } from 'lucide-react';
import { FileUploader } from './components/FileUploader';
import { AnalysisProgress } from './components/AnalysisProgress';
import { ClassificationResult } from './components/ClassificationResult';
import { ParagraphsList } from './components/ParagraphsList';
import { TextAnalysisView } from './components/TextAnalysisView';
import { ComplianceReportView } from './components/ComplianceReportView';
import { DocumentPreview } from './components/DocumentPreview';
import { OverallFeedback, OverallFeedbackData } from './components/OverallFeedback';
import { analyzeDocument } from './services/api';
import { AnalysisResult, AnalysisStage } from './types';
import parseyLogo from './images/parsey.png';
import parseyLogoHeader from './images/parsey-logo.png';
import parseyLayed from './images/parsey_layed.png';

function App() {
  // Estado da análise
  const [analysisStage, setAnalysisStage] = useState<AnalysisStage>(AnalysisStage.IDLE);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  // Estado de feedbacks
  const [feedbacks, setFeedbacks] = useState<{
    uc1?: { rating: 'positive' | 'negative'; comment?: string };
    uc2?: { rating: 'positive' | 'negative'; comment?: string };
    uc3?: { rating: 'positive' | 'negative'; comment?: string };
    uc4?: { rating: 'positive' | 'negative'; comment?: string };
    overall?: OverallFeedbackData;
  }>({});

  /**
   * Adapta resultado da API para formato esperado pelos componentes
   *
   * Explicação:
   * - Usa useMemo para evitar recálculo desnecessário
   * - API retorna estrutura flat
   * - Componentes esperam classificação separada
   */
  const adaptedResult = useMemo(() => {
    if (!result) return null;

    return {
      classification: {
        is_scientific_paper: result.is_scientific_paper,
        document_type: result.is_scientific_paper ? 'scientific_publication' : 'other',
        confidence: result.classification_confidence,
      },
      paragraphs: result.paragraphs,
      text_analysis: result.text_analysis,
      compliance_report: {
        file_name: result.filename,
        analysis_datetime: result.analyzed_at,
        word_count: result.compliance.word_count,
        paragraph_count: result.compliance.paragraph_count,
        is_compliant: result.compliance.is_compliant,
        words_compliant: result.compliance.words_compliant,
        paragraphs_compliant: result.compliance.paragraphs_compliant,
        words_status: result.compliance.words_compliant ? 'ok' : 'insufficient',
        paragraphs_status: result.compliance.paragraphs_compliant ? 'ok' : 'mismatch',
        overall_status: result.compliance.is_compliant ? 'compliant' : 'non-compliant',
        recommended_actions: {
          words_action: result.compliance.recommended_actions[0] || '',
          paragraphs_action: result.compliance.recommended_actions[1] || '',
        },
        report_markdown: result.compliance_report_markdown,
      },
    };
  }, [result]);

  /**
   * Handler para seleção e análise de arquivo
   *
   * Fluxo:
   * 1. Upload do arquivo (progresso 0-100%)
   * 2. API processa TUDO de uma vez (UC1+UC2+UC3+UC4)
   * 3. Exibe resultados
   *
   * Explicação:
   * - Única chamada à API: POST /api/v1/analyze
   * - Não são chamadas sequenciais, é tudo processado junto
   * - Estados: Uploading → Processing → Completed
   */
  const handleFileSelect = async (file: File) => {
    try {
      // Armazenar arquivo para preview
      setSelectedFile(file);

      // Resetar estado
      setResult(null);
      setError(null);
      setAnalysisStage(AnalysisStage.UPLOADING);
      setUploadProgress(0);

      console.log('Iniciando análise do arquivo:', file.name);

      // Fazer requisição à API
      // A API processa UC1+UC2+UC3+UC4 de uma vez
      const analysisResult = await analyzeDocument(file, (progress) => {
        setUploadProgress(progress);

        // Quando upload completa, mudar para PROCESSING
        if (progress === 100) {
          setAnalysisStage(AnalysisStage.PROCESSING);
        }
      });

      // Verificar se é artigo científico (UC1)
      if (!analysisResult.is_scientific_paper) {
        setAnalysisStage(AnalysisStage.ERROR);
        setError(
          'O documento não foi identificado como artigo científico. ' +
          'A análise subsequente não foi executada.'
        );
        setResult(analysisResult); // Ainda mostra resultado parcial
        return;
      }

      // Sucesso! API retornou todos os UCs
      setAnalysisStage(AnalysisStage.COMPLETED);
      setResult(analysisResult);

      console.log('Análise concluída com sucesso:', analysisResult);

    } catch (err) {
      console.error('Erro na análise:', err);
      setAnalysisStage(AnalysisStage.ERROR);
      setError(
        err instanceof Error
          ? err.message
          : 'Ocorreu um erro inesperado durante a análise. Tente novamente.'
      );
    }
  };

  /**
   * Reiniciar análise
   */
  const handleReset = () => {
    setAnalysisStage(AnalysisStage.IDLE);
    setResult(null);
    setError(null);
    setUploadProgress(0);
    setSelectedFile(null);
    setFeedbacks({});
  };

  /**
   * Handler para feedback do UC1
   */
  const handleUC1Feedback = (rating: 'positive' | 'negative', comment?: string) => {
    const feedback = { rating, comment };
    setFeedbacks((prev) => ({ ...prev, uc1: feedback }));

    console.log('Feedback UC1 (Classificação):', feedback);

    // Aqui você pode enviar para API
    // await api.post('/feedback/uc1', { ...feedback, document_id: result?.document_id });
  };

  /**
   * Handler para feedback do UC2
   */
  const handleUC2Feedback = (rating: 'positive' | 'negative', comment?: string) => {
    const feedback = { rating, comment };
    setFeedbacks((prev) => ({ ...prev, uc2: feedback }));

    console.log('Feedback UC2 (Parágrafos):', feedback);

    // Aqui você pode enviar para API
    // await api.post('/feedback/uc2', { ...feedback, document_id: result?.document_id });
  };

  /**
   * Handler para feedback do UC3
   */
  const handleUC3Feedback = (rating: 'positive' | 'negative', comment?: string) => {
    const feedback = { rating, comment };
    setFeedbacks((prev) => ({ ...prev, uc3: feedback }));

    console.log('Feedback UC3 (Análise Textual):', feedback);

    // Aqui você pode enviar para API
    // await api.post('/feedback/uc3', { ...feedback, document_id: result?.document_id });
  };

  /**
   * Handler para feedback do UC4
   */
  const handleUC4Feedback = (rating: 'positive' | 'negative', comment?: string) => {
    const feedback = { rating, comment };
    setFeedbacks((prev) => ({ ...prev, uc4: feedback }));

    console.log('Feedback UC4 (Conformidade):', feedback);

    // Aqui você pode enviar para API
    // await api.post('/feedback/uc4', { ...feedback, document_id: result?.document_id });
  };

  /**
   * Handler para feedback geral
   */
  const handleOverallFeedback = (feedback: OverallFeedbackData) => {
    setFeedbacks((prev) => ({ ...prev, overall: feedback }));

    console.log('Feedback Geral:', feedback);

    // Aqui você pode enviar para API
    // await api.post('/feedback/overall', { ...feedback, document_id: result?.document_id });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-parsey-bg via-parsey-white to-bg-surface">
      {/* Mascote Parsey Fixa no Lado Direito */}
      <div className="hidden lg:block fixed right-8 top-1/2 -translate-y-1/2 z-10 pointer-events-none">
        <div className="relative">
          <div className="absolute -inset-8 bg-gradient-to-r from-brand-primary via-brand-secondary to-brand-accent rounded-full opacity-15 blur-2xl animate-pulse"></div>
          <img
            src={parseyLogo}
            alt="Parsey"
            className="relative w-64 h-64 object-contain animate-bounce-soft drop-shadow-2xl"
          />
        </div>
      </div>

      {/* Header */}
      <header className="bg-white shadow-parsey border-b border-border-subtle backdrop-blur-sm bg-opacity-80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {/* Logo Parsey */}
              <div className="relative">
                <img
                  src={parseyLogoHeader}
                  alt="Parsey Logo"
                  className="h-16 object-contain"
                />
              </div>

              <div>
                <h1 className="text-3xl font-display font-bold bg-gradient-to-r from-brand-primary via-brand-secondary to-brand-accent bg-clip-text text-transparent">
                  Parsey Document Analyzer
                </h1>
                <p className="text-sm text-text-muted mt-1 font-medium">
                  Classificação • Detecção de Parágrafos • Análise de Texto • Conformidade
                </p>
              </div>
            </div>

            {/* Badge de versão e link API Docs */}
            <div className="hidden md:flex items-center space-x-3">
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-1 px-3 py-1 text-xs font-medium text-brand-primary hover:text-brand-emphasis hover:bg-brand-highlight hover:bg-opacity-20 rounded-lg transition-all duration-fast border border-brand-primary border-opacity-30"
              >
                <FileText className="w-3 h-3" />
                <span>API Docs</span>
                <ExternalLink className="w-3 h-3" />
              </a>
              <span className="px-3 py-1 bg-brand-primary bg-opacity-10 text-brand-emphasis text-xs font-semibold rounded-pill">
                v1.0.0
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {/* Upload Section */}
          <section className="bg-white rounded-parsey shadow-md border border-border-subtle overflow-hidden hover:shadow-parsey transition-shadow duration-base lg:mr-72">
            <div className="p-6">
              <h2 className="text-lg font-display font-semibold text-text-primary mb-6">1. Upload do Documento</h2>

              {analysisStage === AnalysisStage.IDLE ? (
                <FileUploader
                  onFileSelect={handleFileSelect}
                  acceptedFormats={['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.tif']}
                  maxSizeMB={10}
                />
              ) : (
                <div className="space-y-4">
                  <div className="p-4 bg-parsey-white border border-border-default rounded-lg">
                    <div className="flex items-center justify-between">
                      <p className="text-sm text-text-muted">Análise em andamento...</p>
                      <button
                        onClick={handleReset}
                        className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-brand-primary hover:text-brand-emphasis hover:bg-brand-highlight hover:bg-opacity-20 rounded-lg transition-all duration-fast"
                        disabled={analysisStage === AnalysisStage.UPLOADING}
                      >
                        <RefreshCw className="w-4 h-4" />
                        <span>Nova Análise</span>
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </section>

          {/* Document Preview Section */}
          {selectedFile && (
            <section className="bg-white rounded-parsey shadow-md border border-border-subtle overflow-hidden hover:shadow-parsey transition-shadow duration-base lg:mr-72">
              <div className="p-6 border-b border-border-subtle">
                <h2 className="text-lg font-display font-semibold text-text-primary">
                  2. Preview do Documento
                </h2>
              </div>
              <div className="p-6">
                <DocumentPreview file={selectedFile} />
              </div>
            </section>
          )}

          {/* Progress Section */}
          {analysisStage !== AnalysisStage.IDLE && (
            <section className="bg-white rounded-parsey shadow-md border border-border-subtle p-6 hover:shadow-parsey transition-shadow duration-base lg:mr-72">
              <h2 className="text-lg font-display font-semibold text-text-primary mb-4">
                {selectedFile ? '3' : '2'}. Progresso da Análise
              </h2>
              <AnalysisProgress
                stage={analysisStage}
                uploadProgress={uploadProgress}
                error={error}
              />
            </section>
          )}

          {/* Results Section */}
          {result && adaptedResult && (
            <>
              {/* UC1: Classification */}
              <section className="lg:mr-72">
                <ClassificationResult
                  classification={adaptedResult.classification}
                  onFeedback={handleUC1Feedback}
                />
              </section>

              {/* Mostrar resultados subsequentes apenas se for artigo científico */}
              {result.is_scientific_paper ? (
                <>
                  {/* UC2: Paragraphs */}
                  <section className="lg:mr-72">
                    <ParagraphsList
                      paragraphs={adaptedResult.paragraphs}
                      onFeedback={handleUC2Feedback}
                    />
                  </section>

                  {/* UC3: Text Analysis */}
                  <section className="lg:mr-72">
                    <TextAnalysisView
                      analysis={adaptedResult.text_analysis}
                      onFeedback={handleUC3Feedback}
                    />
                  </section>

                  {/* UC4: Compliance Report */}
                  <section className="lg:mr-72">
                    <ComplianceReportView
                      report={adaptedResult.compliance_report}
                      onFeedback={handleUC4Feedback}
                    />
                  </section>

                  {/* Feedback Geral - Após todos os UCs */}
                  <section className="lg:mr-72">
                    <OverallFeedback onSubmit={handleOverallFeedback} />
                  </section>
                </>
              ) : (
                <section className="bg-white rounded-parsey shadow-md border border-semantic-warning overflow-hidden lg:mr-72">
                  <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 p-6 bg-gradient-to-br from-white to-amber-50">
                    {/* Mascote Parsey Layed - Lado Esquerdo */}
                    <div className="lg:col-span-4 flex items-center justify-center">
                      <div className="relative">
                        <div className="absolute -inset-4 bg-gradient-to-r from-semantic-warning to-amber-400 rounded-full opacity-10 blur-xl"></div>
                        <img
                          src={parseyLayed}
                          alt="Parsey - Documento não científico"
                          className="relative w-48 h-48 object-contain"
                        />
                      </div>
                    </div>

                    {/* Mensagem - Lado Direito */}
                    <div className="lg:col-span-8 flex flex-col justify-center space-y-4">
                      <div className="flex items-start space-x-3">
                        <AlertCircle className="w-6 h-6 text-semantic-warning flex-shrink-0 mt-1" />
                        <div>
                          <h3 className="text-xl font-display font-bold text-amber-900 mb-3">
                            Análise Interrompida
                          </h3>
                          <p className="text-sm text-amber-700 leading-relaxed mb-3">
                            O documento não foi classificado como <strong>artigo científico</strong>.
                            As análises subsequentes (UC2, UC3, UC4) não foram executadas, pois são
                            específicas para artigos científicos.
                          </p>
                          <div className="bg-amber-100 border border-amber-300 rounded-lg p-4 mt-4">
                            <p className="text-sm text-amber-800 font-medium flex items-center space-x-2">
                              <FileText className="w-4 h-4" />
                              <span>Para continuar, faça upload de um documento que seja identificado como artigo científico.</span>
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </section>
              )}
            </>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-16 pb-8 border-t border-border-subtle bg-white bg-opacity-50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-3">
              <img
                src={parseyLogoHeader}
                alt="Parsey"
                className="h-6 object-contain"
              />
              <p className="text-sm font-mascot font-semibold bg-gradient-to-r from-brand-primary to-brand-accent bg-clip-text text-transparent">
                Powered by Parsey
              </p>
            </div>
            <p className="text-sm text-text-muted">
              Sistema de Análise de Documentos Científicos
            </p>
            <p className="mt-2 text-xs text-text-muted">
              UC1: Classificação • UC2: Detecção de Parágrafos • UC3: Análise Textual • UC4: Conformidade
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
