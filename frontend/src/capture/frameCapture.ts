import { CaptureSourceError } from './types'

export interface FrameCaptureOptions {
  imageType: string
  quality: number
  maxWidth: number
}

const captureEnv = (import.meta as ImportMeta & { env?: Record<string, string> }).env ?? {}

export const defaultFrameCaptureOptions: FrameCaptureOptions = {
  imageType: captureEnv.VITE_CAPTURE_IMAGE_TYPE ?? 'image/jpeg',
  quality: Number(captureEnv.VITE_CAPTURE_JPEG_QUALITY ?? 0.88),
  maxWidth: Number(captureEnv.VITE_CAPTURE_MAX_WIDTH ?? 1600),
}

export function frameDimensions(width: number, height: number, maxWidth: number) {
  const boundedMax = Number.isFinite(maxWidth) && maxWidth > 0 ? maxWidth : 1600
  if (width <= boundedMax) return { width, height }
  const ratio = boundedMax / width
  return { width: Math.round(width * ratio), height: Math.round(height * ratio) }
}

export async function captureVideoFrame(
  video: HTMLVideoElement,
  options: FrameCaptureOptions = defaultFrameCaptureOptions,
): Promise<File> {
  if (!video.videoWidth || !video.videoHeight) {
    throw new CaptureSourceError('capture_failed', '摄像头画面尚未准备好。')
  }
  const size = frameDimensions(video.videoWidth, video.videoHeight, options.maxWidth)
  const canvas = document.createElement('canvas')
  canvas.width = size.width
  canvas.height = size.height
  const context = canvas.getContext('2d')
  if (!context) throw new CaptureSourceError('capture_failed', '浏览器无法创建画布。')
  context.drawImage(video, 0, 0, size.width, size.height)
  const quality = Math.min(1, Math.max(0.1, options.quality))
  const blob = await new Promise<Blob | null>((resolve) =>
    canvas.toBlob(resolve, options.imageType, quality),
  )
  if (!blob) throw new CaptureSourceError('capture_failed', '无法压缩摄像头画面。')
  const extension = options.imageType === 'image/png' ? 'png' : options.imageType === 'image/webp' ? 'webp' : 'jpg'
  return new File([blob], `capture-${Date.now()}.${extension}`, { type: options.imageType })
}
