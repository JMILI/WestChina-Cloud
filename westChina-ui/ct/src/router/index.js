import Vue from 'vue'
import Router from 'vue-router'
import defaultSettings from '@/settings'

//系统编号
const {homePageName, homePageIcon} = defaultSettings
Vue.use(Router)
//获取原型对象上的push函数
// const originalPush = Router.prototype.push
// //修改原型对象中的push方法
// Router.prototype.push = function push(location) {
//   return originalPush.call(this, location).catch(err => err)
// }
/* Layout */
import Layout from '@/layout'

/**
 * Note: 路由配置项
 *
 * hidden: true                     // 当设置 true 的时候该路由不会再侧边栏出现 如401，login等页面，或者如一些编辑页面/edit/1
 * alwaysShow: true                 // 当你一个路由下面的 children 声明的路由大于1个时，自动会变成嵌套的模式--如组件页面
 *                                  // 只有一个时，会将那个子路由当做根路由显示在侧边栏--如引导页面
 *                                  // 若你想不管路由下面的 children 声明的个数都显示你的根路由
 *                                  // 你可以设置 alwaysShow: true，这样它就会忽略之前定义的规则，一直显示根路由
 * redirect: noRedirect             // 当设置 noRedirect 的时候该路由在面包屑导航中不可被点击
 * name:'router-name'               // 设定路由的名字，一定要填写不然使用<keep-alive>时会出现各种问题
 * query: '{"id": 1, "name": "ry"}' // 访问路由的默认传递参数
 * meta : {
    noCache: true                   // 如果设置为true，则不会被 <keep-alive> 缓存(默认 false)
    title: 'title'                  // 设置该路由在侧边栏和面包屑中展示的名字
    icon: 'svg-name'                // 设置该路由的图标，对应路径src/assets/icons/svg
    breadcrumb: false               // 如果设置为false，则不会在breadcrumb面包屑中显示
    activeMenu: '/system/user'      // 当路由设置了该属性，则会高亮相对应的侧边栏。
  }
 */

// 公共路由
export const constantRoutes = [

  {
    path: '/login',
    component: (resolve) => require(['@views/login'], resolve),
    hidden: true
  },
  {
    path: '/404',
    component: (resolve) => require(['@views/error/404'], resolve),
    hidden: true
  },
  {
    path: '/401',
    component: (resolve) => require(['@views/error/401'], resolve),
    hidden: true
  },
  {
    path: '/',
    name: 'patients',
    meta: {keepAlive: true},
    component: (resolve) => require(['@/views/patients/index'], resolve),
  },
  {
    path: 'dicom',
    name: 'dicom',
    component: (resolve) => require(['@/views/dicom/index'], resolve),
  },
  {
    path: 'maker',
    name: 'maker',
    component: (resolve) => require(['@/views/maker/index'], resolve),
    meta: {
      keepAlive: true,
    }
  },

  {
    path: '/Layout',
    component: Layout,
    redirect: 'ct2',
    name: 'Layout',
    children: [
      {
        path: 'ct2',
        component: (resolve) => require(['@/views/ct2/index'], resolve),
        name: 'ct2',
      },
      {
        path: 'ct2row',
        component: (resolve) => require(['@/views/ct2row/ct2row'], resolve),
        name: 'ct2row',
      },
      {
        path: 'makerImage',
        name: 'makerImage',
        component: (resolve) => require(['@/views/makerImage/index'], resolve),
      },
    ]
  },

  {
    path: '/redirect',
    component: Layout,
    hidden: true,
    children: [
      {
        path: '/redirect/:path(.*)',
        component: (resolve) => require(['@/views/redirect'], resolve)
      }
    ]
  },
]

export default new Router({
  // base: "/ct/",
  //踩坑：注意vue.config.js中的proxy路径代理，
  // 会匹配这里写的路由，就是不要在这里路由和代理中的匹配关系相同。否则会找不到路由。
  mode: 'history', // 去掉url中的#
  scrollBehavior: () => ({y: 0}),
  routes: constantRoutes
})
