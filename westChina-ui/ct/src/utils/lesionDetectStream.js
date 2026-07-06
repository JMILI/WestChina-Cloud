import { getToken } from '@utils/auth'

/**
 * 流式病灶识别（SSE），onEvent 接收 Python/Java 转发的每条事件
 */
export function streamDetectChestLesion(data, onEvent) {
  const base = process.env.VUE_APP_BASE_API || ''
  const url = `${base}/ct/ai/detectLesionStream`

  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: 'Bearer ' + getToken()
    },
    body: JSON.stringify(data)
  }).then(async (response) => {
    if (!response.ok) {
      const text = await response.text().catch(() => '')
      throw new Error(text || `识别请求失败 (${response.status})`)
    }
    if (!response.body) {
      throw new Error('浏览器不支持流式响应')
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })

      let splitAt = buffer.indexOf('\n\n')
      while (splitAt >= 0) {
        const block = buffer.slice(0, splitAt)
        buffer = buffer.slice(splitAt + 2)
        parseSseBlock(block, onEvent)
        splitAt = buffer.indexOf('\n\n')
      }
    }
    if (buffer.trim()) {
      parseSseBlock(buffer, onEvent)
    }
  })
}

function parseSseBlock(block, onEvent) {
  const lines = block.split('\n')
  for (const line of lines) {
    if (!line.startsWith('data:')) continue
    const raw = line.slice(5).trim()
    if (!raw) continue
    try {
      onEvent(JSON.parse(raw))
    } catch (e) {
      onEvent({ type: 'log', level: 'warn', message: raw })
    }
  }
}
