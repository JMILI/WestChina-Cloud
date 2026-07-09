/**
 * 解析系统跳转链接：自动适配本机 (127.0.0.1:5000) 与 Sealtun 隧道域名。
 * 数据库建议存相对路径：/ct/、/administrator/
 */
export function getAccessMode() {
  if (typeof window === 'undefined' || !window.location) return 'unknown'
  const host = window.location.hostname
  if (host === '127.0.0.1' || host === 'localhost') return 'local'
  return 'tunnel'
}

export function resolveSystemUrl(url) {
  if (!url) return ''
  if (typeof window === 'undefined' || !window.location || !window.location.origin) {
    return url
  }
  const origin = window.location.origin

  // 相对路径：跟随当前访问入口（本机或隧道同源）
  if (url.startsWith('/')) {
    return `${origin}${url}`
  }

  // 历史占位符
  if (url.startsWith('http://westChinaUI') || url.startsWith('https://westChinaUI')) {
    return `${origin}/main/`
  }

  // 库内曾写死的本机地址 → 换成当前 origin
  if (/^https?:\/\/(127\.0\.0\.1|localhost):5000/.test(url)) {
    return url.replace(/^https?:\/\/(127\.0\.0\.1|localhost):5000/, origin)
  }

  return url
}

/** 管理端「进入系统」跳转 URL */
export function resolveSystemJumpUrl(route) {
  return resolveSystemUrl(route)
}
