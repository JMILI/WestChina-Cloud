 import request from '@utils/request'


 // 查询病人标记过的dicom图像列表
 export function listMaker(query) {
   return request({
     url: '/ct/maker/list',
     method: 'get',
     params: query

   })
 }

 // 查询病人标记过的dicom图像详细
 export function getMaker(query) {
   return request({
     url: '/ct/maker/byId',
     method: 'get',
     params: query

   })
 }

 // 新增病人标记过的dicom图像
 export function addMaker(data) {
   return request({
     url: '/ct/maker',
     method: 'post',
     data: data

   })
 }

 // 修改病人标记过的dicom图像
 export function updateMaker(data) {
   return request({
     url: '/ct/maker',
     method: 'put',
     data: data

   })
 }

 // 修改病人标记过的dicom图像排序
 export function updateMakerSort(data) {
   return request({
     url: '/ct/maker/sort',
     method: 'put',
     data: data

   })
 }

 // 删除病人标记过的dicom图像
 export function delMaker(data) {
   return request({
     url: '/ct/maker',
     method: 'delete',
     data: data

   })
 }


 export function getDicomMakerByPatCardId(query) {
   return request({
     url: '/ct/maker/getDicomMakerByPatCardId',
     method: 'get',
     params: query
   })
 }
