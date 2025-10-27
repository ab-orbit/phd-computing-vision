/**
 * Tipos TypeScript para a aplicação de geração de imagens.
 */

export interface Model {
  name: string;
  display_name: string;
  description: string;
  path: string;
  available: boolean;
}

export interface PromptExample {
  category: string;
  title: string;
  prompt: string;
  description: string;
}

export interface GenerateRequest {
  model_name: string;
  prompt: string;
  num_images: number;
  num_inference_steps?: number;
  guidance_scale?: number;
  seed?: number;
}

export interface GeneratedImage {
  image_data: string;
  seed: number;
  filename: string;
}

export interface GenerateResponse {
  success: boolean;
  model_name: string;
  prompt: string;
  num_images: number;
  images: GeneratedImage[];
  generation_time_seconds: number;
  metadata: Record<string, any>;
}

export interface HealthStatus {
  status: string;
  timestamp: string;
  device: string;
  models_cached: string[];
}
