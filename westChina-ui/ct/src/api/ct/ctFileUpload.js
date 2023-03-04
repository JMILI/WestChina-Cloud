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
  return request({
    url: '/ct/upload/delFile',
    method: 'delete',
    data: data
  })
}
