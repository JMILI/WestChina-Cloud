'use strict'
const path = require('path')
const webpack = require('webpack')

function join(dir) {
  return path.join(__dirname, dir)
}

function resolve(dir) {
  return path.resolve(__dirname, dir)
}

const name = process.env.VUE_APP_TITLE || '阅片系统' // 网页标题

const port = process.env.port || process.env.npm_config_port || 83 // 端口

// vue.config.js 配置说明
//官方vue.config.js 参考文档 https://cli.vuejs.org/zh/config/#css-loaderoptions
// 这里只列一部分，具体配置参考文档
module.exports = {


  // 部署生产环境和开发环境下的URL。
  // 默认情况下，Vue CLI 会假设你的应用是被部署在一个域名的根路径上
  // 例如 https://westChinatt.cn/。如果应用被部署在一个子路径上，你就需要用这个选项指定这个子路径。例如，如果你的应用被部署在 https://westChinatt.cn/admin/，则设置 baseUrl 为 /admin/。
  publicPath: process.env.NODE_ENV === "production" ? "./" : "/",
  // publicPath: process.env.NODE_ENV === "production" ? "/ct/" : "/ct/",
  // 在npm run build 或 yarn build 时 ，生成文件的目录名称（要和baseUrl的生产环境路径一致）（默认dist）
  outputDir: 'dist',
  // 用于放置生成的静态资源 (js、css、img、fonts) 的；（项目打包之后，静态资源会放在这个文件夹下）
  assetsDir: 'static',
  // 是否开启eslint保存检测，有效值：ture | false | 'error'
  lintOnSave: process.env.NODE_ENV === 'development',
  // 如果你不需要生产环境的 source map，可以将其设置为 false 以加速生产环境构建。
  productionSourceMap: false,
  // webpack-dev-server 相关配置
  devServer: {
    host: '0.0.0.0',
    port: port,
    open: true,
    proxy: {
      // 第二个代理配置
      // [process.env.VUE_APP_CT_API]: {
      //   target: 'http://westChinaUI:8090',
      //   pathRewrite: {['^' +process.env.VUE_APP_CT_API]: ''},
      //   changeOrigin: true
      // },
      // detail: https://cli.vuejs.org/config/#devserver-proxy
      [process.env.VUE_APP_BASE_API]: {
        target: `http://westChinaUI:8080`,
        changeOrigin: true,
        pathRewrite: {
          ['^' + process.env.VUE_APP_BASE_API]: ''
        }
      },
      '/api-ct': {
        target: 'http://westChinaUI:8090',
        changeOrigin: true,
        pathRewrite: {'^/api-ct': ''},
      },
      '/api-ct-upload': {
        target: 'http://westChinaUI:8080',
        changeOrigin: true,
        pathRewrite: {'^/api-ct-upload': ''},
      },
      '/api-ct-minio': {
        target: 'http://westChinaBackend:9000',
        changeOrigin: true,
        pathRewrite: {'^/api-ct-minio': ''},
      }


    },
    disableHostCheck: true
  },
  css: {
    loaderOptions: {
      sass: {
        sassOptions: { outputStyle: "expanded" }
      }
    }
  },
  configureWebpack: {
    name: name,
    resolve: {
      alias: {
        '@': join('src'),
        '@common': resolve('node_modules/common/src'),
        '@api': resolve('node_modules/common/src/api'),
        '@views': resolve('node_modules/common/src/views'),
        '@utils': resolve('node_modules/common/src/utils'),
        '@assets': resolve('node_modules/common/src/assets'),
        '@constant': resolve('node_modules/common/src/constant'),
        '@components': resolve('node_modules/common/src/components'),
        '@basicsComponents': resolve('node_modules/common/src/components/basics'),
        '@customComponents': resolve('node_modules/common/src/components/custom'),
        '@cornerstoneTools':resolve('node_modules/cornerstone-tools/src')
      }
    },
    // devtool: 'source-map',
    plugins: [
      new webpack.ProvidePlugin({
        $: "jquery",
        jQuery: "jquery",
        "windows.jQuery": "jquery"
      })
    ]
  },
  chainWebpack(config) {
    config.plugins.delete('preload')
    config.plugins.delete('prefetch')

    // alert(path)
    // set svg-sprite-loader
    config.module
      .rule('svg')
      .exclude.add(resolve('node_modules/common/src/assets/icons'))
      .end()
    config.module
      .rule('icons')
      .test(/\.svg$/)
      .include.add(resolve('node_modules/common/src/assets/icons'))
      .end()
      .use('svg-sprite-loader')
      .loader('svg-sprite-loader')
      .options({
        symbolId: 'icon-[name]'
      })
      .end()

    config
      .when(process.env.NODE_ENV !== 'development',
        config => {
          config
            .plugin('ScriptExtHtmlWebpackPlugin')
            .after('html')
            .use('script-ext-html-webpack-plugin', [{
              // `runtime` must same as runtimeChunk name. default is `runtime`
              inline: /runtime\..*\.js$/
            }])
            .end()
          config
            .optimization.splitChunks({
            chunks: 'all',
            cacheGroups: {
              libs: {
                name: 'chunk-libs',
                test: /[\\/]node_modules[\\/]/,
                priority: 10,
                chunks: 'initial' // only package third parties that are initially dependent
              },
              elementUI: {
                name: 'chunk-elementUI', // split elementUI into a single package
                priority: 20, // the weight needs to be larger than libs and app or it will be packaged into libs or app
                test: /[\\/]node_modules[\\/]_?element-ui(.*)/ // in order to adapt to cnpm
              },
              commons: {
                name: 'chunk-commons',
                test: resolve('node_modules/common/src/components'), // can customize your rules
                minChunks: 3, //  minimum common number
                priority: 5,
                reuseExistingChunk: true
              }
            }
          })
          config.optimization.runtimeChunk('single'),
            {
              from: path.resolve(__dirname, './public/robots.txt'), //防爬虫文件
              to: './', //到根目录下
            }
        }
      )

  }
}
