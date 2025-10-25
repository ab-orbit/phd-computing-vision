/**
 * Componente FileUploader
 *
 * Interface drag-and-drop para upload de documentos científicos
 * Suporta PDF e imagens (PNG, JPG, TIFF)
 */

import { useCallback, useState } from 'react';
import { Upload, FileText, X, AlertCircle } from 'lucide-react';
import { clsx } from 'clsx';

interface FileUploaderProps {
  onFileSelect: (file: File) => void;
  isUploading?: boolean;
  acceptedFormats?: string[];
  maxSizeMB?: number;
}

const DEFAULT_ACCEPTED_FORMATS = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.tif'];
const DEFAULT_MAX_SIZE_MB = 10;

export function FileUploader({
  onFileSelect,
  isUploading = false,
  acceptedFormats = DEFAULT_ACCEPTED_FORMATS,
  maxSizeMB = DEFAULT_MAX_SIZE_MB,
}: FileUploaderProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Valida arquivo selecionado
   *
   * Verifica:
   * - Formato permitido
   * - Tamanho máximo
   */
  const validateFile = useCallback(
    (file: File): string | null => {
      // Validar extensão
      const extension = `.${file.name.split('.').pop()?.toLowerCase()}`;
      if (!acceptedFormats.includes(extension)) {
        return `Formato não suportado. Use: ${acceptedFormats.join(', ')}`;
      }

      // Validar tamanho
      const fileSizeMB = file.size / (1024 * 1024);
      if (fileSizeMB > maxSizeMB) {
        return `Arquivo muito grande. Máximo: ${maxSizeMB}MB`;
      }

      return null;
    },
    [acceptedFormats, maxSizeMB]
  );

  /**
   * Handler para seleção de arquivo (input ou drag-and-drop)
   */
  const handleFile = useCallback(
    (file: File) => {
      const validationError = validateFile(file);

      if (validationError) {
        setError(validationError);
        setSelectedFile(null);
        return;
      }

      setError(null);
      setSelectedFile(file);
      onFileSelect(file);
    },
    [validateFile, onFileSelect]
  );

  /**
   * Handler para input file
   */
  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFile(file);
    }
  };

  /**
   * Handlers para drag-and-drop
   */
  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragging(false);

    const file = event.dataTransfer.files?.[0];
    if (file) {
      handleFile(file);
    }
  };

  /**
   * Limpar arquivo selecionado
   */
  const handleClear = () => {
    setSelectedFile(null);
    setError(null);
  };

  /**
   * Formatar tamanho do arquivo
   */
  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="w-full">
      {/* Área de upload */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={clsx(
          'relative border-2 border-dashed rounded-parsey p-8 transition-all duration-base',
          'hover:border-brand-primary hover:bg-brand-highlight hover:bg-opacity-10',
          {
            'border-brand-accent bg-parsey-white shadow-accent': isDragging,
            'border-border-default': !isDragging && !error,
            'border-semantic-danger bg-red-50': error,
            'opacity-50 cursor-not-allowed': isUploading,
          }
        )}
      >
        <input
          type="file"
          accept={acceptedFormats.join(',')}
          onChange={handleInputChange}
          disabled={isUploading}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed"
          id="file-upload"
        />

        <div className="flex flex-col items-center justify-center space-y-4">
          <div
            className={clsx(
              'w-16 h-16 rounded-full flex items-center justify-center transition-all duration-base',
              error ? 'bg-red-100' : 'bg-gradient-to-br from-brand-primary to-brand-accent bg-opacity-10'
            )}
          >
            {error ? (
              <AlertCircle className="w-8 h-8 text-semantic-danger" />
            ) : (
              <Upload className="w-8 h-8 text-brand-primary" />
            )}
          </div>

          <div className="text-center">
            <p className="text-lg font-display font-semibold text-text-primary">
              {isUploading ? 'Enviando documento...' : 'Arraste seu documento aqui'}
            </p>
            <p className="text-sm text-text-muted mt-1">
              ou{' '}
              <label htmlFor="file-upload" className="text-brand-primary hover:text-brand-emphasis cursor-pointer font-semibold transition-colors duration-fast">
                clique para selecionar
              </label>
            </p>
          </div>

          <div className="text-xs text-text-muted text-center">
            <p>Formatos aceitos: {acceptedFormats.join(', ')}</p>
            <p>Tamanho máximo: {maxSizeMB}MB</p>
          </div>
        </div>
      </div>

      {/* Arquivo selecionado */}
      {selectedFile && !error && (
        <div className="mt-4 p-4 bg-white border border-border-subtle rounded-lg shadow-sm hover:shadow-md transition-shadow duration-base">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-brand-primary to-brand-accent bg-opacity-10 rounded-lg flex items-center justify-center">
                <FileText className="w-5 h-5 text-brand-primary" />
              </div>
              <div>
                <p className="text-sm font-medium text-text-primary">{selectedFile.name}</p>
                <p className="text-xs text-text-muted">{formatFileSize(selectedFile.size)}</p>
              </div>
            </div>
            {!isUploading && (
              <button
                onClick={handleClear}
                className="p-2 text-text-muted hover:text-semantic-danger hover:bg-red-50 rounded-lg transition-all duration-fast"
                title="Remover arquivo"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>
        </div>
      )}

      {/* Mensagem de erro */}
      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-semantic-danger rounded-lg">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-semantic-danger flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-semibold text-red-800">Erro ao selecionar arquivo</p>
              <p className="text-sm text-red-600 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
