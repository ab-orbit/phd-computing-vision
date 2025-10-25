/**
 * Componente DocumentPreview
 *
 * Exibe preview do documento enviado (PDF ou imagem)
 * Permite visualização antes e durante a análise
 */

import { useState, useEffect } from 'react';
import { FileText, Image as ImageIcon, AlertCircle, ZoomIn, ZoomOut } from 'lucide-react';
import { clsx } from 'clsx';
import UTIF from 'utif';

interface DocumentPreviewProps {
  file: File | null;
  className?: string;
}

export function DocumentPreview({ file, className }: DocumentPreviewProps) {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [fileType, setFileType] = useState<'pdf' | 'image' | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [zoom, setZoom] = useState<number>(100);

  /**
   * Gera preview do arquivo
   *
   * Explicação:
   * - PDFs: Cria URL blob para embed
   * - Imagens: Cria data URL para exibição
   * - Cleanup automático ao desmontar
   */
  useEffect(() => {
    if (!file) {
      setPreviewUrl(null);
      setFileType(null);
      setError(null);
      return;
    }

    // Limpar preview anterior
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    try {
      const mimeType = file.type;
      const fileName = file.name.toLowerCase();

      // Verificar se é TIFF (converter para PNG usando UTIF)
      if (mimeType === 'image/tiff' || fileName.endsWith('.tif') || fileName.endsWith('.tiff')) {
        const reader = new FileReader();
        reader.onload = async (e) => {
          try {
            const buffer = e.target?.result as ArrayBuffer;

            // Decodificar TIFF
            const ifds = UTIF.decode(buffer);
            UTIF.decodeImage(buffer, ifds[0]);
            const rgba = UTIF.toRGBA8(ifds[0]);

            // Converter para canvas
            const canvas = document.createElement('canvas');
            canvas.width = ifds[0].width;
            canvas.height = ifds[0].height;
            const ctx = canvas.getContext('2d');

            if (ctx) {
              const imageData = ctx.createImageData(canvas.width, canvas.height);
              imageData.data.set(rgba);
              ctx.putImageData(imageData, 0, 0);

              // Criar data URL
              setPreviewUrl(canvas.toDataURL('image/png'));
              setFileType('image');
              setError(null);
            } else {
              setError('Erro ao criar contexto de canvas para conversão TIFF');
            }
          } catch (err) {
            console.error('Erro ao converter TIFF:', err);
            setError('Erro ao converter arquivo TIFF para visualização');
          }
        };
        reader.onerror = () => {
          setError('Erro ao ler arquivo TIFF');
        };
        reader.readAsArrayBuffer(file);
        return;
      }

      if (mimeType === 'application/pdf') {
        // PDF: Criar blob URL
        const blobUrl = URL.createObjectURL(file);
        setPreviewUrl(blobUrl);
        setFileType('pdf');
        setError(null);
      } else if (mimeType.startsWith('image/')) {
        // Imagem: Criar data URL
        const reader = new FileReader();
        reader.onload = (e) => {
          setPreviewUrl(e.target?.result as string);
          setFileType('image');
          setError(null);
        };
        reader.onerror = () => {
          setError('Erro ao carregar imagem');
        };
        reader.readAsDataURL(file);
      } else {
        setError('Formato não suportado para preview');
      }
    } catch (err) {
      setError('Erro ao gerar preview do documento');
      console.error('Preview error:', err);
    }

    // Cleanup
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [file]);

  /**
   * Controles de zoom
   */
  const handleZoomIn = () => {
    setZoom((prev) => Math.min(prev + 25, 200));
  };

  const handleZoomOut = () => {
    setZoom((prev) => Math.max(prev - 25, 50));
  };

  const handleZoomReset = () => {
    setZoom(100);
  };

  if (!file) {
    return (
      <div className={clsx(
        'flex flex-col items-center justify-center h-full min-h-[400px]',
        'bg-gradient-to-br from-parsey-white to-bg-surface',
        'rounded-parsey border-2 border-dashed border-border-default',
        className
      )}>
        <FileText className="w-16 h-16 text-text-muted opacity-50 mb-4" />
        <p className="text-sm text-text-muted">
          Nenhum documento selecionado
        </p>
      </div>
    );
  }

  if (error) {
    const isTiffError = error.includes('TIFF');
    return (
      <div className={clsx(
        'flex flex-col items-center justify-center h-full min-h-[400px]',
        isTiffError ? 'bg-amber-50 rounded-parsey border border-semantic-warning' : 'bg-red-50 rounded-parsey border border-semantic-danger',
        className
      )}>
        <AlertCircle className={clsx('w-16 h-16 mb-4', isTiffError ? 'text-semantic-warning' : 'text-semantic-danger')} />
        <p className={clsx('text-sm font-medium text-center px-6', isTiffError ? 'text-amber-700' : 'text-red-700')}>
          {error}
        </p>
        {isTiffError && file && (
          <div className="mt-6 p-4 bg-white rounded-lg border border-amber-200">
            <div className="flex items-start space-x-3">
              <ImageIcon className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-amber-900">{file.name}</p>
                <p className="text-xs text-amber-700 mt-1">
                  {(file.size / (1024 * 1024)).toFixed(2)} MB • Formato TIFF
                </p>
                <p className="text-xs text-amber-600 mt-2">
                  ✓ Arquivo aceito pela análise
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={clsx('flex flex-col h-full', className)}>
      {/* Header com controles */}
      <div className="flex items-center justify-between p-4 bg-white border-b border-border-subtle rounded-t-parsey">
        <div className="flex items-center space-x-3">
          {fileType === 'pdf' ? (
            <FileText className="w-5 h-5 text-brand-primary" />
          ) : (
            <ImageIcon className="w-5 h-5 text-brand-secondary" />
          )}
          <div>
            <p className="text-sm font-medium text-text-primary truncate max-w-[200px]">
              {file.name}
            </p>
            <p className="text-xs text-text-muted">
              {(file.size / (1024 * 1024)).toFixed(2)} MB
            </p>
          </div>
        </div>

        {/* Controles de zoom */}
        <div className="flex items-center space-x-2">
          <button
            onClick={handleZoomOut}
            className="p-2 text-text-muted hover:text-brand-primary hover:bg-brand-highlight hover:bg-opacity-20 rounded-lg transition-all duration-fast"
            title="Diminuir zoom"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <button
            onClick={handleZoomReset}
            className="px-3 py-1 text-xs font-medium text-text-muted hover:text-brand-primary hover:bg-brand-highlight hover:bg-opacity-20 rounded-lg transition-all duration-fast"
            title="Resetar zoom"
          >
            {zoom}%
          </button>
          <button
            onClick={handleZoomIn}
            className="p-2 text-text-muted hover:text-brand-primary hover:bg-brand-highlight hover:bg-opacity-20 rounded-lg transition-all duration-fast"
            title="Aumentar zoom"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Área de preview */}
      <div className="flex-1 overflow-auto bg-parsey-bg p-4 rounded-b-parsey">
        {fileType === 'pdf' && previewUrl && (
          <div className="flex justify-center">
            <iframe
              src={previewUrl}
              className="w-full h-[600px] bg-white rounded-lg shadow-md border border-border-subtle"
              style={{
                transform: `scale(${zoom / 100})`,
                transformOrigin: 'top center',
                transition: 'transform 0.2s ease',
              }}
              title="PDF Preview"
            />
          </div>
        )}

        {fileType === 'image' && previewUrl && (
          <div className="flex justify-center">
            <img
              src={previewUrl}
              alt={file.name}
              className="max-w-full h-auto rounded-lg shadow-md border border-border-subtle bg-white"
              style={{
                transform: `scale(${zoom / 100})`,
                transformOrigin: 'top center',
                transition: 'transform 0.2s ease',
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
}
