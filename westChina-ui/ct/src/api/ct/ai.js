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

/** 提交异步识别任务（RabbitMQ） */
export function submitDetectChestLesionTask(data) {
  return request({
    url: '/ct/ai/detectLesionTask',
    method: 'post',
    data,
    timeout: 300000
  })
}

/** 查询异步识别任务状态 */
export function queryDetectChestLesionTask(taskId) {
  return request({
    url: `/ct/ai/detectLesionTask/${taskId}`,
    method: 'get',
    timeout: 30000
  })
}

/** 取消异步识别任务 */
export function cancelDetectChestLesionTask(taskId) {
  return request({
    url: `/ct/ai/detectLesionTask/${taskId}/cancel`,
    method: 'post',
    timeout: 30000
  })
}

/** 获取可用识别引擎 */
export function listDetectEngines() {
  return request({
    url: '/ct/ai/engines',
    method: 'get',
    timeout: 30000
  })
}
