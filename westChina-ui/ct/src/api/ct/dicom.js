import request from '@utils/request'

// 查询病人dicom存储记录列表
export function listDicom(query) {
  return request({
    url: '/ct/dicom/list',
    method: 'get',
    params: query

  })
}

// 查询病人dicom存储记录详细
export function getDicom(query) {
  return request({
    url: '/ct/dicom/byId',
    method: 'get',
    params: query

  })
}


// 新增病人dicom存储记录
export function addDicom(data) {
  return request({
    url: '/ct/dicom/add',
    method: 'post',
    data: data
  })
}

// 修改病人dicom存储记录
export function updateDicom(data) {
  return request({
    url: '/ct/dicom',
    method: 'put',
    data: data
  })
}

// 修改病人dicom存储记录排序
export function updateDicomSort(query) {
  return request({
    url: '/ct/dicom/sort',
    method: 'put',
    data: query
  })
}

// 删除病人dicom存储记录
export function delDicom(data) {
  return request({
    url: '/ct/dicom',
    method: 'delete',
    data: data
  })
}

export function getDicomByPatCardId(query) {
  return request({
    url: '/ct/dicom/getDicomByPatCardId',
    method: 'get',
    params: query
  })
}
export function getStudyListByPatCardId(query) {
  return request({
    url: '/ct/dicom/getStudyListByPatCardId',
    method: 'get',
    params: query
  })
}
