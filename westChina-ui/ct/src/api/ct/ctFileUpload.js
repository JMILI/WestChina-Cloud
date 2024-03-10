import request from '@utils/request'
export function ctFile(data) {
  return request({
    url: '/ct/upload/ctFile',
    method: 'post',
    data: data
  })
}

// 删除文件
export function delFile(data) {
  console.log(data)
  return request({
    url: '/ct/upload/delFile',
    method: 'delete',
    data: data
  })
}

// 查询该账号的企业账号所对应的minio 存储桶
export function getBucketName(query) {
  return request({
    url: '/ct/upload/getBucketName',
    method: 'get',
    params: query
  })
}

// 删除桶
export function delBucketName(query) {
  return request({
    url: '/ct/upload/delBucketName',
    method: 'delete',
    params: query
  })
}
// 删除序列文件夹
export function delFolderFiles(data) {
  return request({
    url: '/ct/upload/delFolderFiles',
    method: 'delete',
    data: data
  })
}

