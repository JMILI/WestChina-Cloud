import request from '@utils/request'

export function listAiLesion(query) {
  return request({
    url: '/ct/aiLesion/list',
    method: 'get',
    params: query
  })
}

export function getAiLesion(query) {
  return request({
    url: '/ct/aiLesion/byId',
    method: 'get',
    params: query
  })
}

export function getAiLesionByPatCardId(query) {
  return request({
    url: '/ct/aiLesion/getByPatCardId',
    method: 'get',
    params: query
  })
}

export function saveAiLesionResult(data) {
  return request({
    url: '/ct/aiLesion/save',
    method: 'post',
    data,
    timeout: 300000
  })
}

export function updateAiLesion(data) {
  return request({
    url: '/ct/aiLesion',
    method: 'put',
    data
  })
}

export function delAiLesion(data) {
  return request({
    url: '/ct/aiLesion',
    method: 'delete',
    data
  })
}
