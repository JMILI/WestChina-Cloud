import router from './router'
import store from './store'
import {Message} from 'element-ui'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'
import {getToken} from '@utils/auth'
import {baseSystemUrl} from '@/settings'

NProgress.configure({showSpinner: false})

const whiteList = ['/login', '/auth-redirect', '/bind', '/register']
// 当一个导航触发时，全局前置守卫按照创建顺序调用。
// 守卫是异步解析执行，此时导航在所有守卫 resolve 完之前一直处于 等待中
// 所以一定要执行next(),一定要调用该方法来 resolve 这个钩子。执行效果依赖 next 方法的调用参数。
router.beforeEach((to, from, next) => {
  NProgress.start()
  // next()

  if (getToken()) {
    // console.log(getToken())
    to.meta.title && store.dispatch('settings/setTitle', to.meta.title)
    /* has token*/
    if (to.path === '/login') {
      next({path: '/'})
      NProgress.done()
    } else {
      if (store.getters.roles.length === 0) {
        // 判断当前用户是否已拉取完user_info信息
        console.log("没有userinfo，获取并获取动态路由")
        store.dispatch('GetInfo').then(() => {
          store.dispatch('GenerateRoutes').then(accessRoutes => {
            // 根据roles权限生成可访问的路由表
            router.addRoutes(accessRoutes) // 动态添加可访问路由表
            console.log(accessRoutes)
            next({...to, replace: true}) // hack方法 确保addRoutes已完成
          })
        }).catch(err => {
          store.dispatch('LogOut').then(() => {
            Message.error(err)
            next({path: '/'})
          })
        })
      } else {
        next()
      }
    }
  } else {
    // 没有token
    if (whiteList.indexOf(to.path) !== -1) {
      // 在免登录白名单，直接进入
      next()
    } else {
      if (baseSystemUrl != null && baseSystemUrl !== '') {
        window.location.href = baseSystemUrl // 否则全部重定向到指定登录页
      } else {
        next(`/login?redirect=${to.fullPath}`) // 否则全部重定向到当前系统的登录页
      }
      NProgress.done()
    }
  }
})
// 你也可以注册全局后置钩子，然而和守卫不同的是，这些钩子不会接受 next 函数也不会改变导航本身：
router.afterEach(() => {
  NProgress.done()
})
