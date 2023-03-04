import request from '@utils/request'

// 查询该账号的企业账号所对应的minio 存储桶
export function getBucketName(query) {
  return request({
    url: '/ct/minio/getBucketName',
    method: 'get',
    params: query
  })
}

// 查询该账号的企业账号所对应的minio 存储桶
export function delFile(query) {
  return request({
    url: '/ct/minio/delFile',
    method: 'delete',
    params: query
  })
}
