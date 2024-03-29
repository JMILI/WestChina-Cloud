## 开发

```bash
# 克隆项目
git clone https://gitee.com/westChinatiantang/westChina-cloud.git

# 进入项目目录
cd westChina-ui

# 依赖安装
# 方式1
yarn install && npm-run-all install:*
# 方式2
yarn install; npm run install-all
# 方式3
npm install --legacy-peer-deps
cd main && npm install
cd administrator && npm install

# 只安装各模块依赖
npm-run-all install:*

# 启动服务
# 方式1
npm-run-all --parallel start:*
# 方式2
npm run start-all
# 方式3
cd main && vue-cli-service serve
cd administrator && vue-cli-service serve
```

浏览器访问 http://westChinaUI:80

## 发布

```bash
# 构建主模块的生产环境
cd main && npm run build:prod
cd main && yarn run build:prod
# 构建租户管理模块的生产环境
cd administrator && npm run build:prod
cd administrator && yarn run build:prod
# ct系统
cd ct && npm run build:prod
cd ct && yarn run build:prod

# 构建全部模块的生产环境 | 可以运行npm 脚本 的build-all
concurrently "cd administrator && vue-cli-service build" "cd main && vue-cli-service build"
```

### 前端结构

~~~  
westChina-ui              // 前端框架 [80、81]
├── common                            // 公共组件
│     ├── src                         // 源代码
│          ├── api                    // 全局公用请求
│          ├── assets                 // 主题 字体等静态资源
│          ├── components             // 全局公用组件
│          ├── constant               // 全局公用常量
│          ├── directive              // 全局公用指令
│          ├── plugins                // 全局公用插件
│          ├── utils                  // 全局公用方法
│          └── views                  // 全局公用view
│     └── package.json                // package.json
│
├── main                              // 默认系统 [80]
│     ├── build                       // 构建相关  
│     ├── bin                         // 执行脚本
│     ├── public                      // 公共文件
│          ├── favicon.ico            // favicon图标
│          └── index.html             // html模板
│     ├── src                         // 源代码
│          ├── api                    // 所有请求
│          ├── layout                 // 布局
│          ├── router                 // 路由
│          ├── store                  // store管理
│          ├── utils                  // 公用方法
│          ├── views                  // view
│          ├── App.vue                // 入口页面
│          ├── main.js                // 入口 加载组件 初始化等
│          ├── permission.js          // 权限管理
│          └── settings.js            // 系统配置
│     ├── .editorconfig               // 编码格式
│     ├── .env.development            // 开发环境配置
│     ├── .env.production             // 生产环境配置
│     ├── .env.staging                // 测试环境配置
│     ├── .eslintignore               // 忽略语法检查
│     ├── .eslintrc.js                // eslint 配置项
│     ├── .gitignore                  // git 忽略项
│     ├── babel.config.js             // babel.config.js
│     ├── package.json                // package.json
│     └── vue.config.js               // vue.config.js
│
├── administrator                     // 租管系统 [81]
│     ├── build                       // 构建相关  
│     ├── bin                         // 执行脚本
│     ├── public                      // 公共文件
│          ├── favicon.ico            // favicon图标
│          └── index.html             // html模板
│     ├── src                         // 源代码
│          ├── api                    // 所有请求
│          ├── layout                 // 布局
│          ├── router                 // 路由
│          ├── store                  // store管理
│          ├── utils                  // 公用方法
│          ├── views                  // view
│          ├── App.vue                // 入口页面
│          ├── main.js                // 入口 加载组件 初始化等
│          ├── permission.js          // 权限管理
│          └── settings.js            // 系统配置
│     ├── .editorconfig               // 编码格式
│     ├── .env.development            // 开发环境配置
│     ├── .env.production             // 生产环境配置
│     ├── .env.staging                // 测试环境配置
│     ├── .eslintignore               // 忽略语法检查
│     ├── .eslintrc.js                // eslint 配置项
│     ├── .gitignore                  // git 忽略项
│     ├── babel.config.js             // babel.config.js
│     ├── package.json                // package.json
│     └── vue.config.js               // vue.config.js
│   
│
├── .gitignore                        // git 忽略项
└── package.json                      // package.json
~~~
