import request from '@utils/request'

// 查询patientInfo列表
export function listPatient(query) {
  return request({
    url: '/ct/patient/list',
    method: 'get',
    params: query

  })
}

// 查询patientInfo详细
export function getPatient(query) {
  return request({
    url: '/ct/patient/byId',
    method: 'get',
    params: query

  })
}

// 新增patientInfo
export function addPatient(data) {
  return request({
    url: '/ct/patient',
    method: 'post',
    data: data

  })
}

// 修改patientInfo
export function updatePatient(data) {
  return request({
    url: '/ct/patient',
    method: 'put',
    data: data

  })
}

// 删除patientInfo
export function delPatient(data) {
  return request({
    url: '/ct/patient',
    method: 'delete',
    data: data

  })
}
