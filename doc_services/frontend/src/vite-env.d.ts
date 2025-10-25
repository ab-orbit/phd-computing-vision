/// <reference types="vite/client" />

/**
 * Declarações de tipo para assets importados no Vite
 *
 * Permite importar imagens, vídeos e outros assets como módulos
 */

declare module '*.png' {
  const value: string;
  export default value;
}

declare module '*.jpg' {
  const value: string;
  export default value;
}

declare module '*.jpeg' {
  const value: string;
  export default value;
}

declare module '*.svg' {
  const value: string;
  export default value;
}

declare module '*.gif' {
  const value: string;
  export default value;
}

declare module '*.mp4' {
  const value: string;
  export default value;
}

declare module '*.webm' {
  const value: string;
  export default value;
}

/**
 * Tipos para variáveis de ambiente do Vite
 */
interface ImportMetaEnv {
  readonly VITE_API_URL: string;
  // Adicione outras variáveis de ambiente aqui conforme necessário
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

/**
 * Tipos para biblioteca UTIF (conversão de TIFF)
 */
declare module 'utif' {
  export function decode(buffer: ArrayBuffer): any[];
  export function decodeImage(buffer: ArrayBuffer, ifd: any): void;
  export function toRGBA8(ifd: any): Uint8Array;
}
