import request from '@utils/request'

/** 胸部 CT 病灶识别（序列级） */
export function detectChestLesion(data) {
  return request({
    url: '/ct/ai/detectLesion',
    method: 'post',
    data,
    timeout: 300000
  })
}

/** 获取可用识别引擎 */
export function listDetectEngines() {
  return request({
    url: '/ct/ai/engines',
    method: 'get'
  })
}
