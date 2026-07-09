import settings from '@/settings'

/** MinIO 访问前缀：公网隧道下自动用当前站点 origin，本机默认同源 /minio/ */
export function getMinioUrl() {
  if (typeof window !== 'undefined' && window.location && window.location.origin) {
    return `${window.location.origin}/minio/`
  }
  return settings.minioUrl || 'http://127.0.0.1:5000/minio/'
}
