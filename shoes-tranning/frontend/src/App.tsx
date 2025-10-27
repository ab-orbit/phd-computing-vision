import { useState, useEffect } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Sparkles,
  Image as ImageIcon,
  Loader2,
  Download,
  Clock,
  Zap,
  ChevronDown,
  Info,
  X
} from 'lucide-react';
import apiService from './api';
import type { Model, PromptExample, GeneratedImage, GenerateRequest } from './types';

function App() {
  // Estado
  const [models, setModels] = useState<Model[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [promptExamples, setPromptExamples] = useState<PromptExample[]>([]);
  const [prompt, setPrompt] = useState<string>('');
  const [numImages, setNumImages] = useState<number>(4);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedImages, setGeneratedImages] = useState<GeneratedImage[]>([]);
  const [generationTime, setGenerationTime] = useState<number>(0);
  const [showExamples, setShowExamples] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedImage, setSelectedImage] = useState<GeneratedImage | null>(null);

  // Carregar modelos e exemplos ao iniciar
  useEffect(() => {
    loadModels();
    loadPromptExamples();
  }, []);

  const loadModels = async () => {
    try {
      const data = await apiService.listModels();
      setModels(data.filter(m => m.available));
      if (data.length > 0 && !selectedModel) {
        const defaultModel = data.find(m => m.name !== 'base') || data[0];
        setSelectedModel(defaultModel.name);
      }
    } catch (error) {
      toast.error('Erro ao carregar modelos');
      console.error(error);
    }
  };

  const loadPromptExamples = async () => {
    try {
      const data = await apiService.getPromptExamples();
      setPromptExamples(data);
    } catch (error) {
      toast.error('Erro ao carregar exemplos de prompts');
      console.error(error);
    }
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      toast.error('Por favor, insira um prompt');
      return;
    }

    if (!selectedModel) {
      toast.error('Por favor, selecione um modelo');
      return;
    }

    setIsGenerating(true);
    setGeneratedImages([]);

    const toastId = toast.loading('Gerando imagens...', {
      duration: Infinity,
    });

    try {
      const request: GenerateRequest = {
        model_name: selectedModel,
        prompt: prompt.trim(),
        num_images: numImages,
        num_inference_steps: 50,
        guidance_scale: 7.5,
      };

      const response = await apiService.generateImages(request);

      setGeneratedImages(response.images);
      setGenerationTime(response.generation_time_seconds);

      toast.success(
        `${response.num_images} ${response.num_images === 1 ? 'imagem gerada' : 'imagens geradas'} em ${response.generation_time_seconds.toFixed(1)}s`,
        { id: toastId, duration: 4000 }
      );
    } catch (error: any) {
      toast.error(
        error.response?.data?.detail || 'Erro ao gerar imagens',
        { id: toastId, duration: 5000 }
      );
      console.error(error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleExampleClick = (example: PromptExample) => {
    setPrompt(example.prompt);
    setShowExamples(false);
    toast.success(`Prompt selecionado: ${example.title}`);
  };

  const downloadImage = (image: GeneratedImage) => {
    const link = document.createElement('a');
    link.href = `data:image/png;base64,${image.image_data}`;
    link.download = image.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    toast.success('Download iniciado!');
  };

  const categories = ['all', ...Array.from(new Set(promptExamples.map(p => p.category)))];
  const filteredExamples = selectedCategory === 'all'
    ? promptExamples
    : promptExamples.filter(p => p.category === selectedCategory);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#1f2937',
            color: '#fff',
            border: '1px solid #374151',
          },
        }}
      />

      {/* Header */}
      <header className="border-b border-gray-700 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center gap-3">
            <Sparkles className="w-8 h-8 text-purple-400" />
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                Shoes Image Generator
              </h1>
              <p className="text-gray-400 text-sm">Powered by Stable Diffusion + LoRA</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Controls Section */}
        <div className="bg-gray-800 rounded-2xl p-6 mb-8 border border-gray-700 shadow-2xl">
          {/* Model Selection */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Modelo
            </label>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              disabled={isGenerating}
            >
              <option value="">Selecione um modelo...</option>
              {models.map((model) => (
                <option key={model.name} value={model.name}>
                  {model.display_name}
                </option>
              ))}
            </select>
          </div>

          {/* Prompt Input */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-gray-300">
                Prompt
              </label>
              <button
                onClick={() => setShowExamples(!showExamples)}
                className="text-sm text-purple-400 hover:text-purple-300 flex items-center gap-1"
              >
                <Sparkles className="w-4 h-4" />
                Ver exemplos
              </button>
            </div>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="A professional product photo of brown leather casual shoes on white background, high quality, product photography"
              className="w-full px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              rows={3}
              disabled={isGenerating}
            />
          </div>

          {/* Examples Dropdown */}
          <AnimatePresence>
            {showExamples && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="mb-6 overflow-hidden"
              >
                <div className="bg-gray-700/50 rounded-lg p-4 border border-gray-600">
                  {/* Category filter */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    {categories.map((category) => (
                      <button
                        key={category}
                        onClick={() => setSelectedCategory(category)}
                        className={`px-3 py-1 rounded-full text-sm transition-colors ${
                          selectedCategory === category
                            ? 'bg-purple-500 text-white'
                            : 'bg-gray-600 text-gray-300 hover:bg-gray-500'
                        }`}
                      >
                        {category === 'all' ? 'Todos' : category}
                      </button>
                    ))}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-96 overflow-y-auto">
                    {filteredExamples.map((example, index) => (
                      <button
                        key={index}
                        onClick={() => handleExampleClick(example)}
                        className="text-left p-3 bg-gray-800 rounded-lg hover:bg-gray-750 transition-colors border border-gray-600 hover:border-purple-500"
                      >
                        <div className="text-sm font-medium text-purple-400 mb-1">
                          {example.title}
                        </div>
                        <div className="text-xs text-gray-400 mb-2">
                          {example.description}
                        </div>
                        <div className="text-xs text-gray-500 line-clamp-2">
                          {example.prompt}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Number of Images */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Número de Imagens: {numImages}
            </label>
            <input
              type="range"
              min="1"
              max="8"
              value={numImages}
              onChange={(e) => setNumImages(parseInt(e.target.value))}
              className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-500"
              disabled={isGenerating}
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>1</span>
              <span>4</span>
              <span>8</span>
            </div>
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !prompt.trim() || !selectedModel}
            className="w-full py-4 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 disabled:from-gray-600 disabled:to-gray-600 text-white font-medium rounded-lg transition-all flex items-center justify-center gap-2 shadow-lg disabled:cursor-not-allowed"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Gerando imagens...
              </>
            ) : (
              <>
                <Zap className="w-5 h-5" />
                Gerar Imagens
              </>
            )}
          </button>

          {/* Generation Info */}
          {generationTime > 0 && !isGenerating && (
            <div className="mt-4 flex items-center justify-center gap-4 text-sm text-gray-400">
              <div className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                <span>{generationTime.toFixed(2)}s</span>
              </div>
              <div className="flex items-center gap-1">
                <ImageIcon className="w-4 h-4" />
                <span>{generatedImages.length} imagens</span>
              </div>
            </div>
          )}
        </div>

        {/* Gallery Section */}
        {generatedImages.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gray-800 rounded-2xl p-6 border border-gray-700 shadow-2xl"
          >
            <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
              <ImageIcon className="w-6 h-6 text-purple-400" />
              Imagens Geradas
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {generatedImages.map((image, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className="group relative aspect-square rounded-lg overflow-hidden bg-gray-700 cursor-pointer"
                  onClick={() => setSelectedImage(image)}
                >
                  <img
                    src={`data:image/png;base64,${image.image_data}`}
                    alt={`Generated ${index + 1}`}
                    className="w-full h-full object-cover transition-transform group-hover:scale-110"
                  />

                  {/* Overlay */}
                  <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-all flex items-center justify-center">
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity flex gap-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          downloadImage(image);
                        }}
                        className="p-2 bg-purple-500 hover:bg-purple-600 rounded-lg transition-colors"
                      >
                        <Download className="w-5 h-5 text-white" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedImage(image);
                        }}
                        className="p-2 bg-purple-500 hover:bg-purple-600 rounded-lg transition-colors"
                      >
                        <Info className="w-5 h-5 text-white" />
                      </button>
                    </div>
                  </div>

                  {/* Seed badge */}
                  <div className="absolute bottom-2 left-2 px-2 py-1 bg-black/70 rounded text-xs text-gray-300">
                    Seed: {image.seed}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Empty State */}
        {!isGenerating && generatedImages.length === 0 && (
          <div className="bg-gray-800 rounded-2xl p-12 border border-gray-700 text-center">
            <ImageIcon className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-400 mb-2">
              Nenhuma imagem gerada ainda
            </h3>
            <p className="text-gray-500">
              Configure o prompt e clique em "Gerar Imagens" para começar
            </p>
          </div>
        )}
      </main>

      {/* Image Modal */}
      <AnimatePresence>
        {selectedImage && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedImage(null)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-gray-800 rounded-2xl overflow-hidden max-w-4xl w-full border border-gray-700"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-4 border-b border-gray-700 flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-white">
                    Detalhes da Imagem
                  </h3>
                  <p className="text-sm text-gray-400">Seed: {selectedImage.seed}</p>
                </div>
                <button
                  onClick={() => setSelectedImage(null)}
                  className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-gray-400" />
                </button>
              </div>

              <div className="p-4">
                <img
                  src={`data:image/png;base64,${selectedImage.image_data}`}
                  alt="Full size"
                  className="w-full h-auto rounded-lg"
                />
              </div>

              <div className="p-4 border-t border-gray-700 flex gap-2">
                <button
                  onClick={() => downloadImage(selectedImage)}
                  className="flex-1 py-3 bg-purple-500 hover:bg-purple-600 text-white font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  <Download className="w-5 h-5" />
                  Download
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
