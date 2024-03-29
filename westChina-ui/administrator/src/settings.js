module.exports = {
  /** 侧边栏主题 深色主题theme-dark，浅色主题theme-light */
  sideTheme: 'theme-dark',

  /** 是否系统布局配置 */
  showSettings: false,

  /** 是否显示顶部导航 */
  topNav: false,

  /** 是否显示 tagsView */
  tagsView: true,

  /** 是否固定头部 */
  fixedHeader: true,

  /** 是否显示logo */
  sidebarLogo: true,

  /** 是否显示动态标题 */
  dynamicTitle: false,

  /** 系统编号 */
  systemId: '2',

  /** 初始页名称|图标 */
  homePageName: '首页',
  homePageIcon: 'xy_productCenter',

  /** 主登录页地址 | loginAddress='' 时则跳转至本地登录页 | 本参数目的为控制集中登录/分散登录 */
  // baseSystemUrl: 'http://westChinaUI:5000/main/',
  baseSystemUrl: 'http://westChinaUI',

  /**
   * @type {string | array} 'production' | ['production', 'development']
   * @description Need show err logs component.
   * The default is only used in the production env
   * If you want to also use it in dev, you can pass ['production', 'development']
   */
  errorLog: 'production'
}
