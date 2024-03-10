import Vue from 'vue'

import Cookies from 'js-cookie'

import Element from 'element-ui'

import '@assets/styles/element-variables.scss'
import '@assets/styles/index.scss' // global css
import '@assets/styles/ruoyi.scss' // ruoyi css
import '@assets/styles/westChina.scss' //westChina css element-UI重置

import '@assets/icons' // icon
import '@utils/element' //js element-UI重置
import './permission' // permission control
import App from './App'
import store from './store'
import router from './router'

import directive from '@common/directive' //directive
import plugins from '@common/plugins' // plugins
import {download} from '@utils/request'

import {getDicts, getConfigKey} from "@api/common/common"

import {parseTime, resetForm, addDateRange, selectDictLabel, selectDictLabels, handleTree} from "@utils/ruoyi"
import {acquisition, updateParamIds, sortOrderListOnlyDynamic, excludeRepeatList, excludeEmptyList, sortOrderList, mergeTableRow, isMobile} from "@utils/westChina"
import RightToolbar from "@basicsComponents/RightToolbar"   // 自定义表格工具组件
import ImageUpload from "@basicsComponents/ImageUpload"   // 图片上传组件
import FileUpload from "@basicsComponents/FileUpload"   // 文件上传组件
import Pagination from "@basicsComponents/Pagination"
import ImageBox from "@customComponents/ImageBox"   // 图片管理组件
import DictTag from '@basicsComponents/DictTag'   // 字典标签组件
import Editor from "@basicsComponents/Editor"   // 富文本组件
import VueMeta from 'vue-meta'    // 头部标签组件
import DictData from '@basicsComponents/DictData'   // 字典数据组件
import JsonExcel from 'vue-json-excel'

import uploader from 'vue-simple-uploader'//上传组件
// import uploadBtn from 'vue-simple-uploader'
// import uploaderDrop from 'vue-simple-uploader'
// import uploaderUnsupport from 'vue-simple-uploader'
// import uploaderList from 'vue-simple-uploader'
// import uploaderFiles from 'vue-simple-uploader'
// import uploaderFile from 'vue-simple-uploader'
// import uploader from 'vue-simple-uploader'
// import uploader from 'vue-simple-uploader'
// import $ from 'jquery'
//
// Vue.prototype.$ = $












// 全局方法挂载
Vue.prototype.getDicts = getDicts
Vue.prototype.getConfigKey = getConfigKey
Vue.prototype.parseTime = parseTime
Vue.prototype.resetForm = resetForm
Vue.prototype.addDateRange = addDateRange
Vue.prototype.selectDictLabel = selectDictLabel
Vue.prototype.selectDictLabels = selectDictLabels
Vue.prototype.download = download
Vue.prototype.handleTree = handleTree

Vue.prototype.acquisition = acquisition
Vue.prototype.updateParamIds = updateParamIds

Vue.prototype.sortOrderList = sortOrderList
Vue.prototype.excludeEmptyList = excludeEmptyList
Vue.prototype.excludeRepeatList = excludeRepeatList
Vue.prototype.sortOrderListOnlyDynamic = sortOrderListOnlyDynamic
Vue.prototype.mergeTableRow = mergeTableRow
Vue.prototype.isMobile = isMobile

// 全局组件挂载
Vue.component('ImageBox', ImageBox)
Vue.component('DictTag', DictTag)
Vue.component('Pagination', Pagination)
Vue.component('RightToolbar', RightToolbar)
Vue.component('Editor', Editor)
Vue.component('FileUpload', FileUpload)
Vue.component('ImageUpload', ImageUpload)

Vue.component('uploader', uploader)
Vue.component('downloadExcel', JsonExcel)

// Vue.component('uploadBtn',uploadBtn)
// Vue.component('uploaderDrop',uploaderDrop)
// Vue.component('uploaderUnsupport',uploaderUnsupport)
// Vue.component('uploaderList',uploaderList)
// Vue.component('uploaderFiles',uploaderFiles)
// Vue.component('uploaderFile',uploaderFile)

Vue.use(directive)
Vue.use(plugins)
Vue.use(VueMeta)
Vue.use(uploader)
// Vue.use(uploadBtn)
// Vue.use(uploaderDrop)
// Vue.use(uploaderUnsupport)
// Vue.use(uploaderList)
// Vue.use(uploaderFiles)
// Vue.use(uploaderFile)
DictData.install()

/**
 * If you don't want to use mock-server
 * you want to use MockJs for mock api
 * you can execute: mockXHR()
 *
 * Currently MockJs will be used in the production environment,
 * please remove it before going online! ! !
 */

Vue.use(Element, {
  size: Cookies.get('size') || 'medium' // set element-ui default size
})

Vue.config.productionTip = false

new Vue({
  el: '#app',
  router,
  store,
  render: h => h(App)
})
