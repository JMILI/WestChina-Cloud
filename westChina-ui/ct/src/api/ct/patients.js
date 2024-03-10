import request from '@utils/request'

// 查询病人信息列表
export function listPatients(query) {
  return request({
    url: '/ct/patients/list',
    method: 'get',
    params: query

  })
}

// 查询病人信息详细
export function getPatients(query) {
  return request({
    url: '/ct/patients/byId',
    method: 'get',
    params: query

  })
}

// 新增病人信息
export function addPatients(data) {
  return request({
    url: '/ct/patients',
    method: 'post',
    data: data

  })
}

// 修改病人信息
export function updatePatients(data) {
  return request({
    url: '/ct/patients',
    method: 'put',
    data: data

  })
}

// 修改病人信息排序
export function updatePatientsSort(data) {
  return request({
    url: '/ct/patients/sort',
    method: 'put',
    data: data

  })
}

// 删除病人信息
export function delPatients(data) {
  return request({
    url: '/ct/patients',
    method: 'delete',
    data: data

  })
}
