/*
 Navicat Premium Data Transfer

 Source Server         : huaxi
 Source Server Type    : MySQL
 Source Server Version : 50735
 Source Host           : localhost:3306
 Source Schema         : xy-config

 Target Server Type    : MySQL
 Target Server Version : 50735
 File Encoding         : 65001

 Date: 06/03/2022 21:51:10
*/
DROP DATABASE IF EXISTS `xy-config`;

CREATE DATABASE  `xy-config` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

USE `xy-config`;

-- ----------------------------
-- Table structure for config_info
-- ----------------------------
DROP TABLE IF EXISTS `config_info`;
CREATE TABLE `config_info`
(
    `id`           bigint(20)                                       NOT NULL AUTO_INCREMENT COMMENT 'id',
    `data_id`      varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL COMMENT 'data_id',
    `group_id`     varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NULL     DEFAULT NULL,
    `content`      longtext CHARACTER SET utf8 COLLATE utf8_bin     NOT NULL COMMENT 'content',
    `md5`          varchar(32) CHARACTER SET utf8 COLLATE utf8_bin  NULL     DEFAULT NULL COMMENT 'md5',
    `gmt_create`   datetime(0)                                      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `gmt_modified` datetime(0)                                      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
    `src_user`     text CHARACTER SET utf8 COLLATE utf8_bin         NULL COMMENT 'source user',
    `src_ip`       varchar(50) CHARACTER SET utf8 COLLATE utf8_bin  NULL     DEFAULT NULL COMMENT 'source ip',
    `app_name`     varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NULL     DEFAULT NULL,
    `tenant_id`    varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NULL     DEFAULT '' COMMENT '租户字段',
    `c_desc`       varchar(256) CHARACTER SET utf8 COLLATE utf8_bin NULL     DEFAULT NULL,
    `c_use`        varchar(64) CHARACTER SET utf8 COLLATE utf8_bin  NULL     DEFAULT NULL,
    `effect`       varchar(64) CHARACTER SET utf8 COLLATE utf8_bin  NULL     DEFAULT NULL,
    `type`         varchar(64) CHARACTER SET utf8 COLLATE utf8_bin  NULL     DEFAULT NULL,
    `c_schema`     text CHARACTER SET utf8 COLLATE utf8_bin         NULL,
    PRIMARY KEY (`id`) USING BTREE,
    UNIQUE INDEX `uk_configinfo_datagrouptenant` (`data_id`, `group_id`, `tenant_id`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 19
  CHARACTER SET = utf8
  COLLATE = utf8_bin COMMENT = 'config_info'
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of config_info
-- ----------------------------
INSERT INTO `config_info`
VALUES (1, 'application-dev.yml', 'DEFAULT_GROUP',
        'westChina:\n  # 演示模式开关\n  demo:\n    enabled: ${secret.demo.enabled}\n\nspring:\r\n  main:\r\n    allow-circular-references: true\r\n    allow-bean-definition-overriding: true\r\n  autoconfigure:\r\n    exclude: com.alibaba.druid.spring.boot.autoconfigure.DruidDataSourceAutoConfigure\r\n  mvc:\n    pathmatch:\n      matching-strategy: ant_path_matcher\n  cloud:\n    sentinel:\n      filter:\n        # sentinel 在 springboot 2.6.x 不兼容问题的处理\n        enabled: false\n\n# feign 配置\nfeign:\n  sentinel:\n    enabled: true\n  okhttp:\n    enabled: true\n  httpclient:\n    enabled: false\n  client:\n    config:\n      default:\n        connectTimeout: 10000\n        readTimeout: 10000\n  compression:\n    request:\n      enabled: true\n    response:\n      enabled: true\n\n# 暴露监控端点\nmanagement:\n  endpoints:\n    web:\n      exposure:\n        include: \' *\'\n',
        'db868af6c3e2b2bbc45a12787a3c33f6', '2022-03-06 13:21:09', '2022-03-06 13:21:09', NULL, '0:0:0:0:0:0:0:1', '',
        '', '通用配置', 'null', 'null', 'yaml', 'null');
INSERT INTO `config_info`
VALUES (2, 'application-secret-dev.yml', 'DEFAULT_GROUP',
        'secret:\n  # 演示模式参数信息\n  demo:\n    enabled: false\n\n  #redis参数信息\n  redis:\n    host: westChinaBackend\n    port: 6379\n    password:\n  #rabbitmq参数信息\n  rabbitmq:\n    host: westChinaBackend\n    port: 5672\n    username: guest\n    password: guest\n  #服务状态监控参数信息\n  security:\n    name: westChina\n    password: westChina123\n    title: 服务状态监控\n  # swagger参数信息\n  swagger:\n    title: 接口文档\n    license: Powered By westChina\n    licenseUrl: https://doc.westChinatt.cn\n  # datasource主库参数信息\n  datasource:\n    driver-class-name: com.mysql.cj.jdbc.Driver\n    url: jdbc:mysql://westChinaBackend:3306/xy-cloud?useUnicode=true&characterEncoding=utf8&zeroDateTimeBehavior=convertToNull&useSSL=true&serverTimezone=GMT%2B8\n    username: root\n    password: 123456\n  # druid控制台参数信息\n  druid:\n    stat-view-servlet:\n      enabled: true\n      loginUsername: admin\n      loginPassword: 123456\n  # nacos参数信息\n  nacos:\n    serverAddr: westChinaBackend:8848\n',
        '343a15e3f0d9390942dd1c65ea21649d', '2022-03-06 13:21:09', '2022-03-06 05:23:43', 'nacos', '192.168.80.1', '',
        '', '通用参数配置', 'null', 'null', 'yaml', 'null');
INSERT INTO `config_info`
VALUES (3, 'application-datasource-dev.yml', 'DEFAULT_GROUP',
        '# spring配置\r\nspring: \r\n  datasource:\r\n    druid:\r\n      stat-view-servlet:\r\n        enabled: ${secret.druid.stat-view-servlet.enabled}\r\n        loginUsername: ${secret.druid.stat-view-servlet.loginUsername}\r\n        loginPassword: ${secret.druid.stat-view-servlet.loginPassword}\r\n    dynamic:\r\n      druid:\r\n        initial-size: 5\r\n        min-idle: 5\r\n        maxActive: 20\r\n        maxWait: 60000\r\n        timeBetweenEvictionRunsMillis: 60000\r\n        minEvictableIdleTimeMillis: 300000\r\n        validationQuery: SELECT 1 FROM DUAL\r\n        testWhileIdle: true\r\n        testOnBorrow: false\r\n        testOnReturn: false\r\n        poolPreparedStatements: true\r\n        breakAfterAcquireFailure: true\r\n        ConnectionErrorRetryAttempts: 2\r\n        maxPoolPreparedStatementPerConnectionSize: 20\r\n        filters: stat,slf4j\r\n        connectionProperties: druid.stat.mergeSql\\=true;druid.stat.slowSqlMillis\\=5000\r\n      datasource:\r\n          # 主库数据源\r\n          master:\r\n            driver-class-name: ${secret.datasource.driver-class-name}\r\n            url: ${secret.datasource.url}\r\n            username: ${secret.datasource.username}\r\n            password: ${secret.datasource.password}\r\n          # 数据源信息会通过master库进行获取并生成，请在主库的xy_tenant_source中配置即可\r\n      # seata: true    # 开启seata代理，开启后默认每个数据源都代理，如果某个不需要代理可单独关闭\r\n\r\n# seata配置\r\nseata:\r\n  # 默认关闭，如需启用spring.datasource.dynami.seata需要同时开启\r\n  enabled: false\r\n  # Seata 应用编号，默认为 ${spring.application.name}\r\n  application-id: ${spring.application.name}\r\n  # Seata 事务组编号，用于 TC 集群名\r\n  tx-service-group: ${spring.application.name}-group\r\n  # 关闭自动代理\r\n  enable-auto-data-source-proxy: false\r\n  # 服务配置项\r\n  config:\r\n    type: nacos\r\n    nacos:\r\n      serverAddr: ${secret.nacos.serverAddr}\r\n      group: SEATA_GROUP\r\n      namespace:\r\n  registry:\r\n    type: nacos\r\n    nacos:\r\n      application: seata-server\r\n      server-addr: ${secret.nacos.serverAddr}\r\n      namespace:\r\n',
        '7d0baf11143dafe9e87220b52b6188b4', '2022-03-06 13:21:09', '2022-03-06 13:21:09', NULL, '0:0:0:0:0:0:0:1', '',
        '', '通用动态多数据源配置', 'null', 'null', 'yaml', 'null');
INSERT INTO `config_info`
VALUES (4, 'westChina-gateway-dev.yml', 'DEFAULT_GROUP',
        '# spring配置\nspring:\n  redis:\n    host: ${secret.redis.host}\n    port: ${secret.redis.port}\n    password: ${secret.redis.password}\n  cloud:\n    gateway:\n      discovery:\n        locator:\n          lowerCaseServiceId: true\n          enabled: true\n      routes:\n        # 认证中心\n        - id: westChina-auth\n          uri: lb://westChina-auth\n          predicates:\n            - Path=/auth/**\n          filters:\n            # 验证码处理\n            - CacheRequestFilter\n            - ValidateCodeFilter\n            - StripPrefix=1\n        # 代码生成\n        - id: westChina-gen\n          uri: lb://westChina-gen\n          predicates:\n            - Path=/code/**\n          filters:\n            - StripPrefix=1\n        # 定时任务\n        - id: westChina-job\n          uri: lb://westChina-job\n          predicates:\n            - Path=/schedule/**\n          filters:\n            - StripPrefix=1\n        # 系统模块\n        - id: westChina-system\n          uri: lb://westChina-system\n          predicates:\n            - Path=/system/**\n          filters:\n            - StripPrefix=1\n        # 租户模块\n        - id: westChina-tenant\n          uri: lb://westChina-tenant\n          predicates:\n            - Path=/tenant/**\n          filters:\n            - StripPrefix=1\n        # 文件服务\n        - id: westChina-file\n          uri: lb://westChina-file\n          predicates:\n            - Path=/file/**\n          filters:\n            - StripPrefix=1\n        # 阅片服务\n        - id: westChina-ct\n          uri: lb://westChina-ct\n          predicates:\n            - Path=/ct/**\n          filters:\n            - StripPrefix=1\n\n# 安全配置\nsecurity:\n  # 验证码\n  captcha:\n    enabled: true\n    type: math\n  # 防止XSS攻击\n  xss:\n    enabled: true\n    excludeUrls:\n      - /system/notice\n  # 不校验白名单\n  ignore:\n    whites:\n      - /auth/logout\n      - /auth/login\n      - /auth/register\n      - /*/v2/api-docs\n      - /csrf\n',
        'dedc5cef06b1945780534e0c9ce73fdb', '2022-03-06 13:21:09', '2022-03-06 12:35:47', 'nacos', '192.168.80.1', '',
        '', '网关模块', 'null', 'null', 'yaml', 'null');
INSERT INTO `config_info`
VALUES (5, 'westChina-auth-dev.yml', 'DEFAULT_GROUP',
        '# spring配置\r\nspring: \r\n  redis:\r\n    host: ${secret.redis.host}\r\n    port: ${secret.redis.port}\r\n    password: ${secret.redis.password}\r\n',
        'b7354e1eb62c2d846d44a796d9ec6930', '2022-03-06 13:21:09', '2022-03-06 13:21:09', NULL, '0:0:0:0:0:0:0:1', '',
        '', '认证中心', 'null', 'null', 'yaml', 'null');
INSERT INTO `config_info`
VALUES (6, 'westChina-monitor-dev.yml', 'DEFAULT_GROUP',
        '# spring配置\r\nspring: \r\n  security:\r\n    user:\r\n      name: ${secret.security.name}\r\n      password: ${secret.security.password}\r\n  boot:\r\n    admin:\r\n      ui:\r\n        title: ${secret.security.title}\r\n',
        'd8997d0707a2fd5d9fc4e8409da38129', '2022-03-06 13:21:09', '2022-03-06 13:21:09', NULL, '0:0:0:0:0:0:0:1', '',
        '', '监控中心', 'null', 'null', 'yaml', 'null');
INSERT INTO `config_info`
VALUES (7, 'westChina-tenant-dev.yml', 'DEFAULT_GROUP',
        '# spring配置\r\nspring: \r\n  redis:\r\n    host: ${secret.redis.host}\r\n    port: ${secret.redis.port}\r\n    password: ${secret.redis.password}\r\n  #rabbitmq配置\r\n  rabbitmq:\r\n    host: ${secret.rabbitmq.host}\r\n    port: ${secret.rabbitmq.port}\r\n    username: ${secret.rabbitmq.username}\r\n    password: ${secret.rabbitmq.password}\r\n    #虚拟host 可以不设置,使用server默认host\r\n    virtual-host: /\r\n    #确认消息已发送到交换机(Exchange)\r\n    publisher-confirms: true\r\n    #确认消息已发送到队列(Queue)\r\n    publisher-returns: true\r\n    queue-name: westChina-tenant\r\n    source-synchro:\r\n      exchange-name: exchange-source\r\n\r\n# seata配置\r\nseata:\r\n  # 服务配置项\r\n  service:\r\n    # 虚拟组和分组的映射\r\n    vgroup-mapping:\r\n      westChina-tenant-group: default\r\n\r\n# mybatis配置\r\nmybatis:\r\n    # 搜索指定包别名\r\n    typeAliasesPackage: com.westChina.tenant\r\n    # 配置mapper的扫描，找到所有的mapper.xml映射文件\r\n    mapperLocations: classpath:mapper/**/*.xml\r\n\r\n# swagger配置\r\nswagger:\r\n  title: 租户模块${secret.swagger.title}\r\n  license: ${secret.swagger.license}\r\n  licenseUrl: ${secret.swagger.licenseUrl}\r\n',
        '37aa8c4052266fe4ba8722210bd7525b', '2022-03-06 13:21:09', '2022-03-06 13:21:09', NULL, '0:0:0:0:0:0:0:1', '',
        '', '租户管理模块', 'null', 'null', 'yaml', 'null');
INSERT INTO `config_info`
VALUES (8, 'westChina-system-dev.yml', 'DEFAULT_GROUP',
        '# spring配置\r\nspring: \r\n  redis:\r\n    host: ${secret.redis.host}\r\n    port: ${secret.redis.port}\r\n    password: ${secret.redis.password}\r\n  rabbitmq:\r\n    host: ${secret.rabbitmq.host}\r\n    port: ${secret.rabbitmq.port}\r\n    username: ${secret.rabbitmq.username}\r\n    password: ${secret.rabbitmq.password}\r\n    #虚拟host 可以不设置,使用server默认host\r\n    virtual-host: /\r\n    queue-name: westChina-system\r\n    source-synchro:\r\n      exchange-name: exchange-source\r\n\r\n# seata配置\r\nseata:\r\n  # 服务配置项\r\n  service:\r\n    # 虚拟组和分组的映射\r\n    vgroup-mapping:\r\n      westChina-system-group: default\r\n\r\n# mybatis配置\r\nmybatis:\r\n    # 搜索指定包别名\r\n    typeAliasesPackage: com.westChina.system\r\n    # 配置mapper的扫描，找到所有的mapper.xml映射文件\r\n    mapperLocations: classpath:mapper/**/*.xml\r\n\r\n# swagger配置\r\nswagger:\r\n  title: 系统模块${secret.swagger.title}\r\n  license: ${secret.swagger.license}\r\n  licenseUrl: ${secret.swagger.licenseUrl}\r\n',
        '5241d073dc33e0e240174bc71ddcce63', '2022-03-06 13:21:09', '2022-03-06 13:21:09', NULL, '0:0:0:0:0:0:0:1', '',
        '', '系统模块', 'null', 'null', 'yaml', 'null');
INSERT INTO `config_info`
VALUES (9, 'westChina-gen-dev.yml', 'DEFAULT_GROUP',
        '# spring配置\nspring: \n  redis:\n    host: ${secret.redis.host}\n    port: ${secret.redis.port}\n    password: ${secret.redis.password}\n  datasource: \n    driver-class-name: ${secret.datasource.driver-class-name}\n    url: ${secret.datasource.url}\n    username: ${secret.datasource.username}\n    password: ${secret.datasource.password}\n\n# mybatis配置\nmybatis:\n    # 搜索指定包别名\n    typeAliasesPackage: com.westChina.gen.domain\n    # 配置mapper的扫描，找到所有的mapper.xml映射文件\n    mapperLocations: classpath:mapper/**/*.xml\n\n# swagger配置\nswagger:\n  title: 代码生成${secret.swagger.title}\n  license: ${secret.swagger.license}\n  licenseUrl: ${secret.swagger.licenseUrl}\n\n# 代码生成\ngen: \n  # 作者\n  author: westChina\n  # 默认生成包路径 system 需改成自己的模块名称 如 system monitor tool\n  packageName: com.westChina.ct\n  # 自动去除表前缀，默认是true\n  autoRemovePre: true\n  # 表前缀（生成类名不会包含表前缀，多个用逗号分隔）\n  tablePrefix: ct_\n',
        'cab0e396dc96d54b7d86021487c439ed', '2022-03-06 13:21:09', '2022-03-06 05:25:58', 'nacos', '192.168.80.1', '',
        '', '代码生成', 'null', 'null', 'yaml', 'null');
INSERT INTO `config_info`
VALUES (10, 'westChina-job-dev.yml', 'DEFAULT_GROUP',
        '# spring配置\r\nspring: \r\n  redis:\r\n    host: ${secret.redis.host}\r\n    port: ${secret.redis.port}\r\n    password: ${secret.redis.password}\r\n  datasource:\r\n    driver-class-name: ${secret.datasource.driver-class-name}\r\n    url: ${secret.datasource.url}\r\n    username: ${secret.datasource.username}\r\n    password: ${secret.datasource.password}\r\n\r\n# mybatis配置\r\nmybatis:\r\n    # 搜索指定包别名\r\n    typeAliasesPackage: com.westChina.job.domain\r\n    # 配置mapper的扫描，找到所有的mapper.xml映射文件\r\n    mapperLocations: classpath:mapper/**/*.xml\r\n\r\n# swagger配置\r\nswagger:\r\n  title: 定时任务${secret.swagger.title}\r\n  license: ${secret.swagger.license}\r\n  licenseUrl: ${secret.swagger.licenseUrl}\r\n',
        'd6dfade9a2c93c463ae857cd503cb172', '2022-03-06 13:21:09', '2022-03-06 13:21:09', NULL, '0:0:0:0:0:0:0:1', '',
        '', '定时任务', 'null', 'null', 'yaml', 'null');
INSERT INTO `config_info`
VALUES (11, 'westChina-file-dev.yml', 'DEFAULT_GROUP',
        '# 本地文件上传    \nfile:\n    domain: http://westChinaBackend:9300\n    path: D:/westChina/uploadPath\n    prefix: /statics\n\n# FastDFS配置\nfdfs:\n  domain: http://8.129.231.12\n  soTimeout: 3000\n  connectTimeout: 2000\n  trackerList: 8.129.231.12:22122\n\n# Minio配置\nminio:\n  url: http://westChinaBackend:9000\n  accessKey: admin\n  secretKey: admin123456\n  bucketName: common',
        '0f67a238cfc6529eb2ddc5ed6a785d95', '2022-03-06 13:21:09', '2022-03-06 05:26:42', 'nacos', '192.168.80.1', '',
        '', '文件服务', 'null', 'null', 'yaml', 'null');
INSERT INTO `config_info`
VALUES (12, 'sentinel-westChina-gateway', 'DEFAULT_GROUP',
        '[\r\n    {\r\n        \"resource\": \"westChina-auth\",\r\n        \"count\": 500,\r\n        \"grade\": 1,\r\n        \"limitApp\": \"default\",\r\n        \"strategy\": 0,\r\n        \"controlBehavior\": 0\r\n    },\r\n	{\r\n        \"resource\": \"westChina-system\",\r\n        \"count\": 1000,\r\n        \"grade\": 1,\r\n        \"limitApp\": \"default\",\r\n        \"strategy\": 0,\r\n        \"controlBehavior\": 0\r\n    },\r\n	{\r\n        \"resource\": \"westChina-tenant\",\r\n        \"count\": 500,\r\n        \"grade\": 1,\r\n        \"limitApp\": \"default\",\r\n        \"strategy\": 0,\r\n        \"controlBehavior\": 0\r\n    },\r\n	{\r\n        \"resource\": \"westChina-gen\",\r\n        \"count\": 200,\r\n        \"grade\": 1,\r\n        \"limitApp\": \"default\",\r\n        \"strategy\": 0,\r\n        \"controlBehavior\": 0\r\n    },\r\n	{\r\n        \"resource\": \"westChina-job\",\r\n        \"count\": 300,\r\n        \"grade\": 1,\r\n        \"limitApp\": \"default\",\r\n        \"strategy\": 0,\r\n        \"controlBehavior\": 0\r\n    }\r\n]',
        '9f3a3069261598f74220bc47958ec252', '2022-03-06 13:21:09', '2022-03-06 13:21:09', NULL, '0:0:0:0:0:0:0:1', '',
        '', '限流策略', 'null', 'null', 'json', 'null');
INSERT INTO `config_info`
VALUES (16, 'westChina-ct-dev.yml', 'DEFAULT_GROUP',
        '# spring配置\nspring: \n  redis:\n    host: ${secret.redis.host}\n    port: ${secret.redis.port}\n    password: ${secret.redis.password}\n  rabbitmq:\n    host: ${secret.rabbitmq.host}\n    port: ${secret.rabbitmq.port}\n    username: ${secret.rabbitmq.username}\n    password: ${secret.rabbitmq.password}\n    #虚拟host 可以不设置,使用server默认host\n    virtual-host: /\n    queue-name: westChina-ct\n    source-synchro:\n      exchange-name: exchange-source\n\n# seata配置\nseata:\n  # 服务配置项\n  service:\n    # 虚拟组和分组的映射\n    vgroup-mapping:\n      westChina-system-group: default\n\n# mybatis配置\nmybatis:\n    # 搜索指定包别名\n    typeAliasesPackage: com.westChina.ct\n    # 配置mapper的扫描，找到所有的mapper.xml映射文件\n    mapperLocations: classpath:mapper/**/*.xml\n\n# swagger配置\nswagger:\n  title: 系统模块${secret.swagger.title}\n  license: ${secret.swagger.license}\n  licenseUrl: ${secret.swagger.licenseUrl}\n',
        '291dd2e4bc070e3aeefb7ba28c867c27', '2022-03-06 05:27:12', '2022-03-06 05:27:38', 'nacos', '192.168.80.1', '',
        '', '系统模块', '', '', 'yaml', '');

-- ----------------------------
-- Table structure for config_info_aggr
-- ----------------------------
DROP TABLE IF EXISTS `config_info_aggr`;
CREATE TABLE `config_info_aggr`
(
    `id`           bigint(20)                                       NOT NULL AUTO_INCREMENT COMMENT 'id',
    `data_id`      varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL COMMENT 'data_id',
    `group_id`     varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL COMMENT 'group_id',
    `datum_id`     varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL COMMENT 'datum_id',
    `content`      longtext CHARACTER SET utf8 COLLATE utf8_bin     NOT NULL COMMENT '内容',
    `gmt_modified` datetime(0)                                      NOT NULL COMMENT '修改时间',
    `app_name`     varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL,
    `tenant_id`    varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT '' COMMENT '租户字段',
    PRIMARY KEY (`id`) USING BTREE,
    UNIQUE INDEX `uk_configinfoaggr_datagrouptenantdatum` (`data_id`, `group_id`, `tenant_id`, `datum_id`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 1
  CHARACTER SET = utf8
  COLLATE = utf8_bin COMMENT = '增加租户字段'
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for config_info_beta
-- ----------------------------
DROP TABLE IF EXISTS `config_info_beta`;
CREATE TABLE `config_info_beta`
(
    `id`           bigint(20)                                        NOT NULL AUTO_INCREMENT COMMENT 'id',
    `data_id`      varchar(255) CHARACTER SET utf8 COLLATE utf8_bin  NOT NULL COMMENT 'data_id',
    `group_id`     varchar(128) CHARACTER SET utf8 COLLATE utf8_bin  NOT NULL COMMENT 'group_id',
    `app_name`     varchar(128) CHARACTER SET utf8 COLLATE utf8_bin  NULL     DEFAULT NULL COMMENT 'app_name',
    `content`      longtext CHARACTER SET utf8 COLLATE utf8_bin      NOT NULL COMMENT 'content',
    `beta_ips`     varchar(1024) CHARACTER SET utf8 COLLATE utf8_bin NULL     DEFAULT NULL COMMENT 'betaIps',
    `md5`          varchar(32) CHARACTER SET utf8 COLLATE utf8_bin   NULL     DEFAULT NULL COMMENT 'md5',
    `gmt_create`   datetime(0)                                       NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `gmt_modified` datetime(0)                                       NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
    `src_user`     text CHARACTER SET utf8 COLLATE utf8_bin          NULL COMMENT 'source user',
    `src_ip`       varchar(50) CHARACTER SET utf8 COLLATE utf8_bin   NULL     DEFAULT NULL COMMENT 'source ip',
    `tenant_id`    varchar(128) CHARACTER SET utf8 COLLATE utf8_bin  NULL     DEFAULT '' COMMENT '租户字段',
    PRIMARY KEY (`id`) USING BTREE,
    UNIQUE INDEX `uk_configinfobeta_datagrouptenant` (`data_id`, `group_id`, `tenant_id`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 1
  CHARACTER SET = utf8
  COLLATE = utf8_bin COMMENT = 'config_info_beta'
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for config_info_tag
-- ----------------------------
DROP TABLE IF EXISTS `config_info_tag`;
CREATE TABLE `config_info_tag`
(
    `id`           bigint(20)                                       NOT NULL AUTO_INCREMENT COMMENT 'id',
    `data_id`      varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL COMMENT 'data_id',
    `group_id`     varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL COMMENT 'group_id',
    `tenant_id`    varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NULL     DEFAULT '' COMMENT 'tenant_id',
    `tag_id`       varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL COMMENT 'tag_id',
    `app_name`     varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NULL     DEFAULT NULL COMMENT 'app_name',
    `content`      longtext CHARACTER SET utf8 COLLATE utf8_bin     NOT NULL COMMENT 'content',
    `md5`          varchar(32) CHARACTER SET utf8 COLLATE utf8_bin  NULL     DEFAULT NULL COMMENT 'md5',
    `gmt_create`   datetime(0)                                      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `gmt_modified` datetime(0)                                      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
    `src_user`     text CHARACTER SET utf8 COLLATE utf8_bin         NULL COMMENT 'source user',
    `src_ip`       varchar(50) CHARACTER SET utf8 COLLATE utf8_bin  NULL     DEFAULT NULL COMMENT 'source ip',
    PRIMARY KEY (`id`) USING BTREE,
    UNIQUE INDEX `uk_configinfotag_datagrouptenanttag` (`data_id`, `group_id`, `tenant_id`, `tag_id`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 1
  CHARACTER SET = utf8
  COLLATE = utf8_bin COMMENT = 'config_info_tag'
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for config_tags_relation
-- ----------------------------
DROP TABLE IF EXISTS `config_tags_relation`;
CREATE TABLE `config_tags_relation`
(
    `id`        bigint(20)                                       NOT NULL COMMENT 'id',
    `tag_name`  varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL COMMENT 'tag_name',
    `tag_type`  varchar(64) CHARACTER SET utf8 COLLATE utf8_bin  NULL DEFAULT NULL COMMENT 'tag_type',
    `data_id`   varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL COMMENT 'data_id',
    `group_id`  varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL COMMENT 'group_id',
    `tenant_id` varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT '' COMMENT 'tenant_id',
    `nid`       bigint(20)                                       NOT NULL AUTO_INCREMENT,
    PRIMARY KEY (`nid`) USING BTREE,
    UNIQUE INDEX `uk_configtagrelation_configidtag` (`id`, `tag_name`, `tag_type`) USING BTREE,
    INDEX `idx_tenant_id` (`tenant_id`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 1
  CHARACTER SET = utf8
  COLLATE = utf8_bin COMMENT = 'config_tag_relation'
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for group_capacity
-- ----------------------------
DROP TABLE IF EXISTS `group_capacity`;
CREATE TABLE `group_capacity`
(
    `id`                bigint(20) UNSIGNED                              NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `group_id`          varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL DEFAULT '' COMMENT 'Group ID，空字符表示整个集群',
    `quota`             int(10) UNSIGNED                                 NOT NULL DEFAULT 0 COMMENT '配额，0表示使用默认值',
    `usage`             int(10) UNSIGNED                                 NOT NULL DEFAULT 0 COMMENT '使用量',
    `max_size`          int(10) UNSIGNED                                 NOT NULL DEFAULT 0 COMMENT '单个配置大小上限，单位为字节，0表示使用默认值',
    `max_aggr_count`    int(10) UNSIGNED                                 NOT NULL DEFAULT 0 COMMENT '聚合子配置最大个数，，0表示使用默认值',
    `max_aggr_size`     int(10) UNSIGNED                                 NOT NULL DEFAULT 0 COMMENT '单个聚合数据的子配置大小上限，单位为字节，0表示使用默认值',
    `max_history_count` int(10) UNSIGNED                                 NOT NULL DEFAULT 0 COMMENT '最大变更历史数量',
    `gmt_create`        datetime(0)                                      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `gmt_modified`      datetime(0)                                      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
    PRIMARY KEY (`id`) USING BTREE,
    UNIQUE INDEX `uk_group_id` (`group_id`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 1
  CHARACTER SET = utf8
  COLLATE = utf8_bin COMMENT = '集群、各Group容量信息表'
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for his_config_info
-- ----------------------------
DROP TABLE IF EXISTS `his_config_info`;
CREATE TABLE `his_config_info`
(
    `id`           bigint(64) UNSIGNED                              NOT NULL,
    `nid`          bigint(20) UNSIGNED                              NOT NULL AUTO_INCREMENT,
    `data_id`      varchar(255) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
    `group_id`     varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL,
    `app_name`     varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NULL     DEFAULT NULL COMMENT 'app_name',
    `content`      longtext CHARACTER SET utf8 COLLATE utf8_bin     NOT NULL,
    `md5`          varchar(32) CHARACTER SET utf8 COLLATE utf8_bin  NULL     DEFAULT NULL,
    `gmt_create`   datetime(0)                                      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `gmt_modified` datetime(0)                                      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `src_user`     text CHARACTER SET utf8 COLLATE utf8_bin         NULL,
    `src_ip`       varchar(50) CHARACTER SET utf8 COLLATE utf8_bin  NULL     DEFAULT NULL,
    `op_type`      char(10) CHARACTER SET utf8 COLLATE utf8_bin     NULL     DEFAULT NULL,
    `tenant_id`    varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NULL     DEFAULT '' COMMENT '租户字段',
    PRIMARY KEY (`nid`) USING BTREE,
    INDEX `idx_gmt_create` (`gmt_create`) USING BTREE,
    INDEX `idx_gmt_modified` (`gmt_modified`) USING BTREE,
    INDEX `idx_did` (`data_id`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 7
  CHARACTER SET = utf8
  COLLATE = utf8_bin COMMENT = '多租户改造'
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of his_config_info
-- ----------------------------
INSERT INTO `his_config_info`
VALUES (2, 1, 'application-secret-dev.yml', 'DEFAULT_GROUP', '',
        'secret:\n  # 演示模式参数信息\n  demo:\n    enabled: false\n\n  #redis参数信息\n  redis:\n    host: westChinaBackend\n    port: 6379\n    password:\n  #rabbitmq参数信息\n  rabbitmq:\n    host: westChinaBackend\n    port: 5672\n    username: guest\n    password: guest\n  #服务状态监控参数信息\n  security:\n    name: westChina\n    password: westChina123\n    title: 服务状态监控\n  # swagger参数信息\n  swagger:\n    title: 接口文档\n    license: Powered By westChina\n    licenseUrl: https://doc.westChinatt.cn\n  # datasource主库参数信息\n  datasource:\n    driver-class-name: com.mysql.cj.jdbc.Driver\n    url: jdbc:mysql://westChinaBackend:3306/xy-cloud?useUnicode=true&characterEncoding=utf8&zeroDateTimeBehavior=convertToNull&useSSL=true&serverTimezone=GMT%2B8\n    username: root\n    password: password\n  # druid控制台参数信息\n  druid:\n    stat-view-servlet:\n      enabled: true\n      loginUsername: admin\n      loginPassword: 123456\n  # nacos参数信息\n  nacos:\n    serverAddr: westChinaBackend:8848\n',
        '5c29e913666c5a1e4f65f9f2fb24baf3', '2022-03-06 13:23:43', '2022-03-06 05:23:43', 'nacos', '192.168.80.1', 'U',
        '');
INSERT INTO `his_config_info`
VALUES (9, 2, 'westChina-gen-dev.yml', 'DEFAULT_GROUP', '',
        '# spring配置\r\nspring: \r\n  redis:\r\n    host: ${secret.redis.host}\r\n    port: ${secret.redis.port}\r\n    password: ${secret.redis.password}\r\n  datasource: \r\n    driver-class-name: ${secret.datasource.driver-class-name}\r\n    url: ${secret.datasource.url}\r\n    username: ${secret.datasource.username}\r\n    password: ${secret.datasource.password}\r\n\r\n# mybatis配置\r\nmybatis:\r\n    # 搜索指定包别名\r\n    typeAliasesPackage: com.westChina.gen.domain\r\n    # 配置mapper的扫描，找到所有的mapper.xml映射文件\r\n    mapperLocations: classpath:mapper/**/*.xml\r\n\r\n# swagger配置\r\nswagger:\r\n  title: 代码生成${secret.swagger.title}\r\n  license: ${secret.swagger.license}\r\n  licenseUrl: ${secret.swagger.licenseUrl}\r\n\r\n# 代码生成\r\ngen: \r\n  # 作者\r\n  author: westChina\r\n  # 默认生成包路径 system 需改成自己的模块名称 如 system monitor tool\r\n  packageName: com.westChina.system\r\n  # 自动去除表前缀，默认是true\r\n  autoRemovePre: true\r\n  # 表前缀（生成类名不会包含表前缀，多个用逗号分隔）\r\n  tablePrefix: sys_,xy_\r\n',
        '167ee972bb2540fe2028e55dd3f42c9e', '2022-03-06 13:25:58', '2022-03-06 05:25:58', 'nacos', '192.168.80.1', 'U',
        '');
INSERT INTO `his_config_info`
VALUES (11, 3, 'westChina-file-dev.yml', 'DEFAULT_GROUP', '',
        '# 本地文件上传    \r\nfile:\r\n    domain: http://westChinaBackend:9300\r\n    path: D:/westChina/uploadPath\r\n    prefix: /statics\r\n\r\n# FastDFS配置\r\nfdfs:\r\n  domain: http://8.129.231.12\r\n  soTimeout: 3000\r\n  connectTimeout: 2000\r\n  trackerList: 8.129.231.12:22122\r\n\r\n# Minio配置\r\nminio:\r\n  url: http://8.129.231.12:9000\r\n  accessKey: minioadmin\r\n  secretKey: minioadmin\r\n  bucketName: test',
        'dc9739607d5b9593111eb3fbd478a3bc', '2022-03-06 13:26:41', '2022-03-06 05:26:42', 'nacos', '192.168.80.1', 'U',
        '');
INSERT INTO `his_config_info`
VALUES (0, 4, 'westChina-ct-dev.yml', 'DEFAULT_GROUP', '',
        '# spring配置\r\nspring: \r\n  redis:\r\n    host: ${secret.redis.host}\r\n    port: ${secret.redis.port}\r\n    password: ${secret.redis.password}\r\n  rabbitmq:\r\n    host: ${secret.rabbitmq.host}\r\n    port: ${secret.rabbitmq.port}\r\n    username: ${secret.rabbitmq.username}\r\n    password: ${secret.rabbitmq.password}\r\n    #虚拟host 可以不设置,使用server默认host\r\n    virtual-host: /\r\n    queue-name: westChina-system\r\n    source-synchro:\r\n      exchange-name: exchange-source\r\n\r\n# seata配置\r\nseata:\r\n  # 服务配置项\r\n  service:\r\n    # 虚拟组和分组的映射\r\n    vgroup-mapping:\r\n      westChina-system-group: default\r\n\r\n# mybatis配置\r\nmybatis:\r\n    # 搜索指定包别名\r\n    typeAliasesPackage: com.westChina.system\r\n    # 配置mapper的扫描，找到所有的mapper.xml映射文件\r\n    mapperLocations: classpath:mapper/**/*.xml\r\n\r\n# swagger配置\r\nswagger:\r\n  title: 系统模块${secret.swagger.title}\r\n  license: ${secret.swagger.license}\r\n  licenseUrl: ${secret.swagger.licenseUrl}\r\n',
        '0c77e2aefa92646f01c2021e7a7192d1', '2022-03-06 13:27:11', '2022-03-06 05:27:12', NULL, '192.168.80.1', 'I',
        '');
INSERT INTO `his_config_info`
VALUES (16, 5, 'westChina-ct-dev.yml', 'DEFAULT_GROUP', '',
        '# spring配置\r\nspring: \r\n  redis:\r\n    host: ${secret.redis.host}\r\n    port: ${secret.redis.port}\r\n    password: ${secret.redis.password}\r\n  rabbitmq:\r\n    host: ${secret.rabbitmq.host}\r\n    port: ${secret.rabbitmq.port}\r\n    username: ${secret.rabbitmq.username}\r\n    password: ${secret.rabbitmq.password}\r\n    #虚拟host 可以不设置,使用server默认host\r\n    virtual-host: /\r\n    queue-name: westChina-system\r\n    source-synchro:\r\n      exchange-name: exchange-source\r\n\r\n# seata配置\r\nseata:\r\n  # 服务配置项\r\n  service:\r\n    # 虚拟组和分组的映射\r\n    vgroup-mapping:\r\n      westChina-system-group: default\r\n\r\n# mybatis配置\r\nmybatis:\r\n    # 搜索指定包别名\r\n    typeAliasesPackage: com.westChina.system\r\n    # 配置mapper的扫描，找到所有的mapper.xml映射文件\r\n    mapperLocations: classpath:mapper/**/*.xml\r\n\r\n# swagger配置\r\nswagger:\r\n  title: 系统模块${secret.swagger.title}\r\n  license: ${secret.swagger.license}\r\n  licenseUrl: ${secret.swagger.licenseUrl}\r\n',
        '0c77e2aefa92646f01c2021e7a7192d1', '2022-03-06 13:27:37', '2022-03-06 05:27:38', 'nacos', '192.168.80.1', 'U',
        '');
INSERT INTO `his_config_info`
VALUES (4, 6, 'westChina-gateway-dev.yml', 'DEFAULT_GROUP', '',
        '# spring配置\r\nspring:\n  redis:\n    host: ${secret.redis.host}\n    port: ${secret.redis.port}\n    password: ${secret.redis.password}\n  cloud:\n    gateway:\n      discovery:\n        locator:\n          lowerCaseServiceId: true\n          enabled: true\n      routes:\n        # 认证中心\n        - id: westChina-auth\n          uri: lb://westChina-auth\n          predicates:\n            - Path=/auth/**\n          filters:\n            # 验证码处理\n            - CacheRequestFilter\n            - ValidateCodeFilter\n            - StripPrefix=1\n        # 代码生成\n        - id: westChina-gen\n          uri: lb://westChina-gen\n          predicates:\n            - Path=/code/**\n          filters:\n            - StripPrefix=1\n        # 定时任务\n        - id: westChina-job\n          uri: lb://westChina-job\n          predicates:\n            - Path=/schedule/**\n          filters:\n            - StripPrefix=1\n        # 系统模块\n        - id: westChina-system\n          uri: lb://westChina-system\n          predicates:\n            - Path=/system/**\n          filters:\n            - StripPrefix=1\n        # 租户模块\n        - id: westChina-tenant\n          uri: lb://westChina-tenant\n          predicates:\n            - Path=/tenant/**\n          filters:\n            - StripPrefix=1\n        # 文件服务\n        - id: westChina-file\n          uri: lb://westChina-file\n          predicates:\n            - Path=/file/**\n          filters:\n            - StripPrefix=1\n\n# 安全配置\nsecurity:\n  # 验证码\n  captcha:\n    enabled: true\n    type: math\n  # 防止XSS攻击\n  xss:\n    enabled: true\n    excludeUrls:\n      - /system/notice\n  # 不校验白名单\n  ignore:\n    whites:\n      - /auth/logout\n      - /auth/login\n      - /auth/register\n      - /*/v2/api-docs\n      - /csrf\n',
        '6bcfb3de91291e601248fb25a8e87e56', '2022-03-06 20:35:47', '2022-03-06 12:35:47', 'nacos', '192.168.80.1', 'U',
        '');

-- ----------------------------
-- Table structure for permissions
-- ----------------------------
DROP TABLE IF EXISTS `permissions`;
CREATE TABLE `permissions`
(
    `role`     varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NOT NULL,
    `resource` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `action`   varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL,
    UNIQUE INDEX `uk_role_permission` (`role`, `resource`, `action`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for roles
-- ----------------------------
DROP TABLE IF EXISTS `roles`;
CREATE TABLE `roles`
(
    `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `role`     varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    UNIQUE INDEX `idx_user_role` (`username`, `role`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of roles
-- ----------------------------
INSERT INTO `roles`
VALUES ('nacos', 'ROLE_ADMIN');

-- ----------------------------
-- Table structure for tenant_capacity
-- ----------------------------
DROP TABLE IF EXISTS `tenant_capacity`;
CREATE TABLE `tenant_capacity`
(
    `id`                bigint(20) UNSIGNED                              NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `tenant_id`         varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL DEFAULT '' COMMENT 'Tenant ID',
    `quota`             int(10) UNSIGNED                                 NOT NULL DEFAULT 0 COMMENT '配额，0表示使用默认值',
    `usage`             int(10) UNSIGNED                                 NOT NULL DEFAULT 0 COMMENT '使用量',
    `max_size`          int(10) UNSIGNED                                 NOT NULL DEFAULT 0 COMMENT '单个配置大小上限，单位为字节，0表示使用默认值',
    `max_aggr_count`    int(10) UNSIGNED                                 NOT NULL DEFAULT 0 COMMENT '聚合子配置最大个数',
    `max_aggr_size`     int(10) UNSIGNED                                 NOT NULL DEFAULT 0 COMMENT '单个聚合数据的子配置大小上限，单位为字节，0表示使用默认值',
    `max_history_count` int(10) UNSIGNED                                 NOT NULL DEFAULT 0 COMMENT '最大变更历史数量',
    `gmt_create`        datetime(0)                                      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `gmt_modified`      datetime(0)                                      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '修改时间',
    PRIMARY KEY (`id`) USING BTREE,
    UNIQUE INDEX `uk_tenant_id` (`tenant_id`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 1
  CHARACTER SET = utf8
  COLLATE = utf8_bin COMMENT = '租户容量信息表'
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for tenant_info
-- ----------------------------
DROP TABLE IF EXISTS `tenant_info`;
CREATE TABLE `tenant_info`
(
    `id`            bigint(20)                                       NOT NULL AUTO_INCREMENT COMMENT 'id',
    `kp`            varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NOT NULL COMMENT 'kp',
    `tenant_id`     varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT '' COMMENT 'tenant_id',
    `tenant_name`   varchar(128) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT '' COMMENT 'tenant_name',
    `tenant_desc`   varchar(256) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL COMMENT 'tenant_desc',
    `create_source` varchar(32) CHARACTER SET utf8 COLLATE utf8_bin  NULL DEFAULT NULL COMMENT 'create_source',
    `gmt_create`    bigint(20)                                       NOT NULL COMMENT '创建时间',
    `gmt_modified`  bigint(20)                                       NOT NULL COMMENT '修改时间',
    PRIMARY KEY (`id`) USING BTREE,
    UNIQUE INDEX `uk_tenant_info_kptenantid` (`kp`, `tenant_id`) USING BTREE,
    INDEX `idx_tenant_id` (`tenant_id`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 1
  CHARACTER SET = utf8
  COLLATE = utf8_bin COMMENT = 'tenant_info'
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`
(
    `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NOT NULL,
    `password` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    `enabled`  tinyint(1)                                                    NOT NULL,
    PRIMARY KEY (`username`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users`
VALUES ('nacos', '$2a$10$EuWPZHzz32dJN7jexM34MOeYirDdFAZm2kuWj7VEOJhhZkDrxfvUu', 1);

SET
    FOREIGN_KEY_CHECKS = 1;
