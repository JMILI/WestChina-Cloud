import request from '@utils/request'

// 查询对象存储，存储租户的桶信息列表
export function listBucket(query) {
  return request({
    url: '/tenant/bucket/list',
    method: 'get',
    params: query

  })
}

// 查询对象存储，存储租户的桶信息详细
export function getBucket(query) {
  return request({
    url: '/tenant/bucket/byId',
    method: 'get',
    params: query

  })
}

// 新增对象存储，存储租户的桶信息
export function addBucket(data) {
  return request({
    url: '/tenant/bucket',
    method: 'post',
    data: data

  })
}

// 修改对象存储，存储租户的桶信息
export function updateBucket(data) {
  return request({
    url: '/tenant/bucket',
    method: 'put',
    data: data

  })
}

// 修改对象存储，存储租户的桶信息排序
export function updateBucketSort(data) {
  return request({
    url: '/tenant/bucket/sort',
    method: 'put',
    data: data

  })
}

// 删除对象存储，存储租户的桶信息
export function delBucket(data) {
  return request({
    url: '/tenant/bucket',
    method: 'delete',
    data: data

  })
}
