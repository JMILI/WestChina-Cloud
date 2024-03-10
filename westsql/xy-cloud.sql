/*
 Navicat MySQL Data Transfer

 Source Server         : huaxi
 Source Server Type    : MySQL
 Source Server Version : 80032 (8.0.32-0ubuntu0.20.04.2)
 Source Host           : westChinaBackend:3306
 Source Schema         : xy-cloud

 Target Server Type    : MySQL
 Target Server Version : 80032 (8.0.32-0ubuntu0.20.04.2)
 File Encoding         : 65001

 Date: 22/02/2023 16:12:11
*/
DROP
    DATABASE IF EXISTS `xy-cloud`;

CREATE
    DATABASE `xy-cloud` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;


USE
    `xy-cloud`;
SET NAMES utf8mb4;
SET
    FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `dicom_maker`;
CREATE TABLE `dicom_maker`
(
    `dicom_maker_id`        bigint                                                         NOT NULL COMMENT 'id',
    `instance_uid`          varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NOT NULL COMMENT '单张图像instanceID',
    `study_uid`             varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT NULL COMMENT '研究id',
    `series_uid`            varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT NULL COMMENT '序列UId',
    `study_date`            varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL     DEFAULT NULL COMMENT 'ct拍摄时间',
    `pat_card_id`           varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL     DEFAULT NULL COMMENT '身份证号',
    `patient_name`          varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '病人姓名',
    `maker_doctor`          varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '标记医生',
    `maker_enterprise_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '医院名',
    `maker_time`            varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL     DEFAULT NULL COMMENT '标记时间',
    `maker_image_address`   varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT NULL COMMENT '标记图像地址',
    `maker_description`     varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    `maker_image`           varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL     DEFAULT NULL COMMENT '用来存储图像元数据，临时用',

    `maker_columns`               int                                                            NULL     DEFAULT NULL COMMENT '列值',
    `maker_rows`                  int                                                            NULL     DEFAULT NULL COMMENT '行值',
    `maker_column_pixel_spacing`  float                                                          NULL     DEFAULT NULL COMMENT '列像素间距',
    `maker_row_pixel_spacing`     float                                                          NULL     DEFAULT NULL COMMENT '行像素间距',
    `maker_slope`                 int                                                            NULL     DEFAULT NULL COMMENT '转换系数，用于像素到CT值的转换',
    `maker_intercept`             int                                                            NULL     DEFAULT NULL COMMENT '截距，用于像素到CT值的转换',
    `maker_window_center`         int                                                            NULL     DEFAULT NULL COMMENT '窗位',
    `maker_window_width`          int                                                            NULL     DEFAULT NULL COMMENT '窗宽',
    `maker_is_dicom`              tinyint                                                        NULL     DEFAULT NULL COMMENT '是否时dicom p10格式文件',
    `maker_scale`                 float                                                          NULL     DEFAULT NULL COMMENT '缩放比例',


    `sort`                  int UNSIGNED                                                   NOT NULL DEFAULT 0 COMMENT '显示顺序',
    `create_by`             bigint                                                         NULL     DEFAULT NULL COMMENT '创建者',
    `create_time`           datetime                                                       NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`             bigint                                                         NULL     DEFAULT NULL COMMENT '更新者',
    `update_time`           datetime                                                       NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `remark`                varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    `del_flag`              tinyint                                                        NOT NULL DEFAULT 0 COMMENT '删除标志（0正常 1删除）',
    `tenant_id`             bigint                                                         NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`dicom_maker_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '病人标记过的dicom图像表'
  ROW_FORMAT = DYNAMIC;
-- ----------------------------
-- Table structure for ct_dicom
-- ----------------------------
DROP TABLE IF EXISTS `ct_dicom`;
CREATE TABLE `ct_dicom`
(
    `dicom_id`             bigint                                                         NOT NULL COMMENT 'id',
    `pat_card_id`          varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '身份证号',
    `dicom_ct_time`        varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL     DEFAULT NULL COMMENT 'ct拍摄时间',
    `dicom_ct_study_uid`   varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT NULL COMMENT '研究UId',
    `dicom_ct_series_uid`  varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT NULL COMMENT '序列UId',
    `dicom_ct_body`        varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT NULL COMMENT '检查的身体部位',
    `dicom_ct_path`        varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '序列第一张的存储地址',
    `dicom_ct_count`       int                                                            NULL     DEFAULT NULL COMMENT '一个序列的dicom数量',
    `dicom_ct_description` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    `sort`                 int UNSIGNED                                                   NOT NULL DEFAULT 0 COMMENT '显示顺序',
    `create_by`            bigint                                                         NULL     DEFAULT NULL COMMENT '创建者',
    `create_time`          datetime                                                       NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`            bigint                                                         NULL     DEFAULT NULL COMMENT '更新者',
    `update_time`          datetime                                                       NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `remark`               varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    `del_flag`             tinyint                                                        NOT NULL DEFAULT 0 COMMENT '删除标志（0正常 1删除）',
    `tenant_id`            bigint                                                         NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`dicom_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '病人dicom存储记录表'
  ROW_FORMAT = DYNAMIC;


-- ----------------------------
-- Records of ct_dicom
-- ----------------------------

-- ----------------------------
-- Table structure for ct_patients
-- ----------------------------
DROP TABLE IF EXISTS `ct_patients`;
CREATE TABLE `ct_patients`
(
    `pat_id`      bigint                                                         NOT NULL COMMENT '唯一id，标识病人',
    `pat_card_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '身份证号',
    `pat_name`    varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL     DEFAULT NULL COMMENT '病人姓名',
    `pat_phone`   varchar(11) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL     DEFAULT NULL COMMENT '病人手机号码',
    `sort`        int UNSIGNED                                                   NOT NULL DEFAULT 0 COMMENT '显示顺序',
    `create_by`   bigint                                                         NULL     DEFAULT NULL COMMENT '创建者',
    `create_time` datetime                                                       NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`   bigint                                                         NULL     DEFAULT NULL COMMENT '更新者',
    `update_time` datetime                                                       NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `remark`      varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    `del_flag`    tinyint                                                        NOT NULL DEFAULT 0 COMMENT '删除标志（0正常 1删除）',
    `tenant_id`   bigint                                                         NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`pat_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '病人信息表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of ct_patients
-- ----------------------------

-- ----------------------------
-- Table structure for gen_table
-- ----------------------------
DROP TABLE IF EXISTS `gen_table`;
CREATE TABLE `gen_table`
(
    `table_id`          bigint                                                         NOT NULL AUTO_INCREMENT COMMENT '编号',
    `table_name`        varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL DEFAULT '' COMMENT '表名称',
    `table_comment`     varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL DEFAULT '' COMMENT '表描述',
    `sub_table_name`    varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL DEFAULT NULL COMMENT '关联子表的表名',
    `sub_table_fk_name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL DEFAULT NULL COMMENT '子表关联的外键名',
    `class_name`        varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL DEFAULT '' COMMENT '实体类名称',
    `prefix`            varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL DEFAULT '' COMMENT '前缀名称',
    `tpl_category`      varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL DEFAULT 'crud' COMMENT '使用的模板（crud单表操作 tree树表操作）',
    `package_name`      varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL DEFAULT NULL COMMENT '生成包路径',
    `module_name`       varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL DEFAULT NULL COMMENT '生成模块名',
    `business_name`     varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL DEFAULT NULL COMMENT '生成业务名',
    `function_name`     varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL DEFAULT NULL COMMENT '生成功能名',
    `function_author`   varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL DEFAULT NULL COMMENT '生成功能作者',
    `gen_type`          char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NULL DEFAULT '0' COMMENT '生成代码方式（0zip压缩包 1自定义路径）',
    `gen_path`          varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL DEFAULT '/' COMMENT '生成路径（不填默认项目路径）',
    `options`           varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '其它生成选项',
    `create_by`         varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL DEFAULT '' COMMENT '创建者',
    `create_time`       datetime                                                       NULL DEFAULT NULL COMMENT '创建时间',
    `update_by`         varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL DEFAULT '' COMMENT '更新者',
    `update_time`       datetime                                                       NULL DEFAULT NULL COMMENT '更新时间',
    `remark`            varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL DEFAULT NULL COMMENT '备注',
    PRIMARY KEY (`table_id`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 1
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '代码生成业务表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of gen_table
-- ----------------------------

-- ----------------------------
-- Table structure for gen_table_column
-- ----------------------------
DROP TABLE IF EXISTS `gen_table_column`;
CREATE TABLE `gen_table_column`
(
    `column_id`      bigint                                                        NOT NULL AUTO_INCREMENT COMMENT '编号',
    `table_id`       varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL DEFAULT NULL COMMENT '归属表编号',
    `column_name`    varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '列名称',
    `column_comment` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '列描述',
    `column_type`    varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '列类型',
    `java_type`      varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'JAVA类型',
    `java_field`     varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'JAVA字段名',
    `is_pk`          char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci      NULL DEFAULT NULL COMMENT '是否主键（1是）',
    `is_increment`   char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci      NULL DEFAULT NULL COMMENT '是否自增（1是）',
    `is_required`    char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci      NULL DEFAULT NULL COMMENT '是否必填（1是）',
    `is_insert`      char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci      NULL DEFAULT NULL COMMENT '是否为插入字段（1是）',
    `is_edit`        char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci      NULL DEFAULT NULL COMMENT '是否编辑字段（1是）',
    `is_list`        char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci      NULL DEFAULT NULL COMMENT '是否列表字段（1是）',
    `is_query`       char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci      NULL DEFAULT NULL COMMENT '是否查询字段（1是）',
    `query_type`     varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT 'EQ' COMMENT '查询方式（等于、不等于、大于、小于、范围）',
    `html_type`      varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '显示类型（文本框、文本域、下拉框、复选框、单选框、日期控件）',
    `dict_type`      varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT '' COMMENT '字典类型',
    `sort`           int                                                           NULL DEFAULT NULL COMMENT '排序',
    `create_by`      varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL DEFAULT '' COMMENT '创建者',
    `create_time`    datetime                                                      NULL DEFAULT NULL COMMENT '创建时间',
    `update_by`      varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL DEFAULT '' COMMENT '更新者',
    `update_time`    datetime                                                      NULL DEFAULT NULL COMMENT '更新时间',
    PRIMARY KEY (`column_id`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 1
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '代码生成业务表字段'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of gen_table_column
-- ----------------------------

-- ----------------------------
-- Table structure for qrtz_blob_triggers
-- ----------------------------
DROP TABLE IF EXISTS `qrtz_blob_triggers`;
CREATE TABLE `qrtz_blob_triggers`
(
    `sched_name`    varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '调度名称',
    `trigger_name`  varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'qrtz_triggers表trigger_name的外键',
    `trigger_group` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'qrtz_triggers表trigger_group的外键',
    `blob_data`     blob                                                          NULL COMMENT '存放持久化Trigger对象',
    PRIMARY KEY (`sched_name`, `trigger_name`, `trigger_group`) USING BTREE,
    CONSTRAINT `qrtz_blob_triggers_ibfk_1` FOREIGN KEY (`sched_name`, `trigger_name`, `trigger_group`) REFERENCES `qrtz_triggers` (`sched_name`, `trigger_name`, `trigger_group`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = 'Blob类型的触发器表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of qrtz_blob_triggers
-- ----------------------------

-- ----------------------------
-- Table structure for qrtz_calendars
-- ----------------------------
DROP TABLE IF EXISTS `qrtz_calendars`;
CREATE TABLE `qrtz_calendars`
(
    `sched_name`    varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '调度名称',
    `calendar_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '日历名称',
    `calendar`      blob                                                          NOT NULL COMMENT '存放持久化calendar对象',
    PRIMARY KEY (`sched_name`, `calendar_name`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '日历信息表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of qrtz_calendars
-- ----------------------------

-- ----------------------------
-- Table structure for qrtz_cron_triggers
-- ----------------------------
DROP TABLE IF EXISTS `qrtz_cron_triggers`;
CREATE TABLE `qrtz_cron_triggers`
(
    `sched_name`      varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '调度名称',
    `trigger_name`    varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'qrtz_triggers表trigger_name的外键',
    `trigger_group`   varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'qrtz_triggers表trigger_group的外键',
    `cron_expression` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'cron表达式',
    `time_zone_id`    varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL DEFAULT NULL COMMENT '时区',
    PRIMARY KEY (`sched_name`, `trigger_name`, `trigger_group`) USING BTREE,
    CONSTRAINT `qrtz_cron_triggers_ibfk_1` FOREIGN KEY (`sched_name`, `trigger_name`, `trigger_group`) REFERENCES `qrtz_triggers` (`sched_name`, `trigger_name`, `trigger_group`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = 'Cron类型的触发器表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of qrtz_cron_triggers
-- ----------------------------

-- ----------------------------
-- Table structure for qrtz_fired_triggers
-- ----------------------------
DROP TABLE IF EXISTS `qrtz_fired_triggers`;
CREATE TABLE `qrtz_fired_triggers`
(
    `sched_name`        varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '调度名称',
    `entry_id`          varchar(95) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NOT NULL COMMENT '调度器实例id',
    `trigger_name`      varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'qrtz_triggers表trigger_name的外键',
    `trigger_group`     varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'qrtz_triggers表trigger_group的外键',
    `instance_name`     varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '调度器实例名',
    `fired_time`        bigint                                                        NOT NULL COMMENT '触发的时间',
    `sched_time`        bigint                                                        NOT NULL COMMENT '定时器制定的时间',
    `priority`          int                                                           NOT NULL COMMENT '优先级',
    `state`             varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NOT NULL COMMENT '状态',
    `job_name`          varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '任务名称',
    `job_group`         varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '任务组名',
    `is_nonconcurrent`  varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL DEFAULT NULL COMMENT '是否并发',
    `requests_recovery` varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL DEFAULT NULL COMMENT '是否接受恢复执行',
    PRIMARY KEY (`sched_name`, `entry_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '已触发的触发器表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of qrtz_fired_triggers
-- ----------------------------

-- ----------------------------
-- Table structure for qrtz_job_details
-- ----------------------------
DROP TABLE IF EXISTS `qrtz_job_details`;
CREATE TABLE `qrtz_job_details`
(
    `sched_name`        varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '调度名称',
    `job_name`          varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '任务名称',
    `job_group`         varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '任务组名',
    `description`       varchar(250) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '相关介绍',
    `job_class_name`    varchar(250) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '执行任务类名称',
    `is_durable`        varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '是否持久化',
    `is_nonconcurrent`  varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '是否并发',
    `is_update_data`    varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '是否更新数据',
    `requests_recovery` varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '是否接受恢复执行',
    `job_data`          blob                                                          NULL COMMENT '存放持久化job对象',
    PRIMARY KEY (`sched_name`, `job_name`, `job_group`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '任务详细信息表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of qrtz_job_details
-- ----------------------------

-- ----------------------------
-- Table structure for qrtz_locks
-- ----------------------------
DROP TABLE IF EXISTS `qrtz_locks`;
CREATE TABLE `qrtz_locks`
(
    `sched_name` varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '调度名称',
    `lock_name`  varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NOT NULL COMMENT '悲观锁名称',
    PRIMARY KEY (`sched_name`, `lock_name`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '存储的悲观锁信息表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of qrtz_locks
-- ----------------------------

-- ----------------------------
-- Table structure for qrtz_paused_trigger_grps
-- ----------------------------
DROP TABLE IF EXISTS `qrtz_paused_trigger_grps`;
CREATE TABLE `qrtz_paused_trigger_grps`
(
    `sched_name`    varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '调度名称',
    `trigger_group` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'qrtz_triggers表trigger_group的外键',
    PRIMARY KEY (`sched_name`, `trigger_group`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '暂停的触发器表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of qrtz_paused_trigger_grps
-- ----------------------------

-- ----------------------------
-- Table structure for qrtz_scheduler_state
-- ----------------------------
DROP TABLE IF EXISTS `qrtz_scheduler_state`;
CREATE TABLE `qrtz_scheduler_state`
(
    `sched_name`        varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '调度名称',
    `instance_name`     varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '实例名称',
    `last_checkin_time` bigint                                                        NOT NULL COMMENT '上次检查时间',
    `checkin_interval`  bigint                                                        NOT NULL COMMENT '检查间隔时间',
    PRIMARY KEY (`sched_name`, `instance_name`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '调度器状态表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of qrtz_scheduler_state
-- ----------------------------
INSERT INTO `qrtz_scheduler_state`
VALUES ('RuoyiScheduler', 'JIMILI1677046636199', 1677053530480, 15000);

-- ----------------------------
-- Table structure for qrtz_simple_triggers
-- ----------------------------
DROP TABLE IF EXISTS `qrtz_simple_triggers`;
CREATE TABLE `qrtz_simple_triggers`
(
    `sched_name`      varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '调度名称',
    `trigger_name`    varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'qrtz_triggers表trigger_name的外键',
    `trigger_group`   varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'qrtz_triggers表trigger_group的外键',
    `repeat_count`    bigint                                                        NOT NULL COMMENT '重复的次数统计',
    `repeat_interval` bigint                                                        NOT NULL COMMENT '重复的间隔时间',
    `times_triggered` bigint                                                        NOT NULL COMMENT '已经触发的次数',
    PRIMARY KEY (`sched_name`, `trigger_name`, `trigger_group`) USING BTREE,
    CONSTRAINT `qrtz_simple_triggers_ibfk_1` FOREIGN KEY (`sched_name`, `trigger_name`, `trigger_group`) REFERENCES `qrtz_triggers` (`sched_name`, `trigger_name`, `trigger_group`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '简单触发器的信息表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of qrtz_simple_triggers
-- ----------------------------

-- ----------------------------
-- Table structure for qrtz_simprop_triggers
-- ----------------------------
DROP TABLE IF EXISTS `qrtz_simprop_triggers`;
CREATE TABLE `qrtz_simprop_triggers`
(
    `sched_name`    varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '调度名称',
    `trigger_name`  varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'qrtz_triggers表trigger_name的外键',
    `trigger_group` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'qrtz_triggers表trigger_group的外键',
    `str_prop_1`    varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'String类型的trigger的第一个参数',
    `str_prop_2`    varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'String类型的trigger的第二个参数',
    `str_prop_3`    varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'String类型的trigger的第三个参数',
    `int_prop_1`    int                                                           NULL DEFAULT NULL COMMENT 'int类型的trigger的第一个参数',
    `int_prop_2`    int                                                           NULL DEFAULT NULL COMMENT 'int类型的trigger的第二个参数',
    `long_prop_1`   bigint                                                        NULL DEFAULT NULL COMMENT 'long类型的trigger的第一个参数',
    `long_prop_2`   bigint                                                        NULL DEFAULT NULL COMMENT 'long类型的trigger的第二个参数',
    `dec_prop_1`    decimal(13, 4)                                                NULL DEFAULT NULL COMMENT 'decimal类型的trigger的第一个参数',
    `dec_prop_2`    decimal(13, 4)                                                NULL DEFAULT NULL COMMENT 'decimal类型的trigger的第二个参数',
    `bool_prop_1`   varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL DEFAULT NULL COMMENT 'Boolean类型的trigger的第一个参数',
    `bool_prop_2`   varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL DEFAULT NULL COMMENT 'Boolean类型的trigger的第二个参数',
    PRIMARY KEY (`sched_name`, `trigger_name`, `trigger_group`) USING BTREE,
    CONSTRAINT `qrtz_simprop_triggers_ibfk_1` FOREIGN KEY (`sched_name`, `trigger_name`, `trigger_group`) REFERENCES `qrtz_triggers` (`sched_name`, `trigger_name`, `trigger_group`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '同步机制的行锁表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of qrtz_simprop_triggers
-- ----------------------------

-- ----------------------------
-- Table structure for qrtz_triggers
-- ----------------------------
DROP TABLE IF EXISTS `qrtz_triggers`;
CREATE TABLE `qrtz_triggers`
(
    `sched_name`     varchar(120) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '调度名称',
    `trigger_name`   varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '触发器的名字',
    `trigger_group`  varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '触发器所属组的名字',
    `job_name`       varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'qrtz_job_details表job_name的外键',
    `job_group`      varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT 'qrtz_job_details表job_group的外键',
    `description`    varchar(250) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '相关介绍',
    `next_fire_time` bigint                                                        NULL DEFAULT NULL COMMENT '上一次触发时间（毫秒）',
    `prev_fire_time` bigint                                                        NULL DEFAULT NULL COMMENT '下一次触发时间（默认为-1表示不触发）',
    `priority`       int                                                           NULL DEFAULT NULL COMMENT '优先级',
    `trigger_state`  varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NOT NULL COMMENT '触发器状态',
    `trigger_type`   varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '触发器的类型',
    `start_time`     bigint                                                        NOT NULL COMMENT '开始时间',
    `end_time`       bigint                                                        NULL DEFAULT NULL COMMENT '结束时间',
    `calendar_name`  varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '日程表名称',
    `misfire_instr`  smallint                                                      NULL DEFAULT NULL COMMENT '补偿执行的策略',
    `job_data`       blob                                                          NULL COMMENT '存放持久化job对象',
    PRIMARY KEY (`sched_name`, `trigger_name`, `trigger_group`) USING BTREE,
    INDEX `sched_name` (`sched_name` ASC, `job_name` ASC, `job_group` ASC) USING BTREE,
    CONSTRAINT `qrtz_triggers_ibfk_1` FOREIGN KEY (`sched_name`, `job_name`, `job_group`) REFERENCES `qrtz_job_details` (`sched_name`, `job_name`, `job_group`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '触发器详细信息表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of qrtz_triggers
-- ----------------------------

-- ----------------------------
-- Table structure for sys_config
-- ----------------------------
DROP TABLE IF EXISTS `sys_config`;
CREATE TABLE `sys_config`
(
    `config_id`    bigint                                                         NOT NULL COMMENT '参数主键',
    `config_name`  varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT '参数名称',
    `config_key`   varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT '参数键名',
    `config_value` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT '参数键值',
    `config_type`  char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NULL     DEFAULT 'N' COMMENT '系统内置（Y是 N否）',
    `create_by`    bigint                                                         NULL     DEFAULT NULL COMMENT '创建者',
    `create_time`  datetime                                                       NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`    bigint                                                         NULL     DEFAULT NULL COMMENT '更新者',
    `update_time`  datetime                                                       NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `remark`       varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    `del_flag`     tinyint                                                        NOT NULL DEFAULT 0 COMMENT '删除标志(0正常 1删除)',
    `tenant_id`    bigint                                                         NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`config_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '参数配置表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of sys_config
-- ----------------------------
INSERT INTO `sys_config`
VALUES (1, '主框架页-默认皮肤样式名称', 'sys.index.skinName', 'skin-blue', 'Y', NULL, '2022-03-06 21:36:40', NULL, NULL,
        '蓝色 skin-blue、绿色 skin-green、紫色 skin-purple、红色 skin-red、黄色 skin-yellow', 0, 0);
INSERT INTO `sys_config`
VALUES (2, '用户管理-账号初始密码', 'sys.user.initPassword', '123456', 'Y', NULL, '2022-03-06 21:36:40', NULL, NULL,
        '初始化密码 123456', 0, 0);
INSERT INTO `sys_config`
VALUES (3, '主框架页-侧边栏主题', 'sys.index.sideTheme', 'theme-dark', 'Y', NULL, '2022-03-06 21:36:40', NULL, NULL,
        '深色主题theme-dark，浅色主题theme-light', 0, 0);
INSERT INTO `sys_config`
VALUES (4, '账号自助-是否开启租户注册功能', 'sys.account.registerTenant', 'false', 'Y', NULL, '2022-03-06 21:36:40',
        NULL, NULL, '是否开启注册租户功能（true开启，false关闭）', 0, -1);

-- ----------------------------
-- Table structure for sys_dept
-- ----------------------------
DROP TABLE IF EXISTS `sys_dept`;
CREATE TABLE `sys_dept`
(
    `dept_id`     bigint                                                          NOT NULL COMMENT '部门id',
    `parent_id`   bigint                                                          NULL     DEFAULT 0 COMMENT '父部门id',
    `dept_code`   varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci    NULL     DEFAULT NULL COMMENT '部门编码',
    `dept_name`   varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci    NULL     DEFAULT '' COMMENT '部门名称',
    `ancestors`   varchar(10000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT '' COMMENT '祖级列表',
    `leader`      varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci    NULL     DEFAULT '' COMMENT '负责人',
    `phone`       varchar(11) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci    NULL     DEFAULT '' COMMENT '联系电话',
    `email`       varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci    NULL     DEFAULT '' COMMENT '邮箱',
    `sort`        int UNSIGNED                                                    NOT NULL DEFAULT 0 COMMENT '显示顺序',
    `status`      char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci        NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
    `is_change`   char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci        NOT NULL DEFAULT 'N' COMMENT '系统部门（Y是 N否）',
    `create_by`   bigint                                                          NULL     DEFAULT NULL COMMENT '创建者',
    `create_time` datetime                                                        NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`   bigint                                                          NULL     DEFAULT NULL COMMENT '更新者',
    `update_time` datetime                                                        NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `remark`      varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT NULL COMMENT '备注',
    `del_flag`    tinyint                                                         NOT NULL DEFAULT 0 COMMENT '删除标志(0正常 1删除)',
    `tenant_id`   bigint                                                          NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`dept_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '部门表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of sys_dept
-- ----------------------------
INSERT INTO `sys_dept`
VALUES (-4, 0, '-4', '华西运维', '0', '', '', '', 0, '0', 'N', NULL, '2022-03-06 16:24:06', -2, '2022-03-06 20:48:35',
        NULL, 0, -1);

-- ----------------------------
-- Table structure for sys_dict_data
-- ----------------------------
DROP TABLE IF EXISTS `sys_dict_data`;
CREATE TABLE `sys_dict_data`
(
    `dict_code`   bigint                                                         NOT NULL AUTO_INCREMENT COMMENT '字典编码',
    `dict_sort`   int                                                            NULL     DEFAULT 0 COMMENT '字典排序',
    `dict_label`  varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT '字典标签',
    `dict_value`  varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT '字典键值',
    `dict_type`   varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT '字典类型',
    `css_class`   varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT NULL COMMENT '样式属性（其他样式扩展）',
    `list_class`  varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT NULL COMMENT '表格回显样式',
    `is_default`  char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NULL     DEFAULT 'N' COMMENT '是否默认（Y是 N否）',
    `status`      char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
    `create_by`   bigint                                                         NULL     DEFAULT NULL COMMENT '创建者',
    `create_time` datetime                                                       NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`   bigint                                                         NULL     DEFAULT NULL COMMENT '更新者',
    `update_time` datetime                                                       NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `remark`      varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    PRIMARY KEY (`dict_code`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 100
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '字典数据表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of sys_dict_data
-- ----------------------------
INSERT INTO `sys_dict_data`
VALUES (1, 1, '男', '0', 'sys_user_sex', '', '', 'Y', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '性别男');
INSERT INTO `sys_dict_data`
VALUES (2, 2, '女', '1', 'sys_user_sex', '', '', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '性别女');
INSERT INTO `sys_dict_data`
VALUES (3, 3, '未知', '2', 'sys_user_sex', '', '', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '性别未知');
INSERT INTO `sys_dict_data`
VALUES (4, 1, '显示', '0', 'sys_show_hide', '', 'primary', 'Y', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '显示菜单');
INSERT INTO `sys_dict_data`
VALUES (5, 2, '隐藏', '1', 'sys_show_hide', '', 'danger', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '隐藏菜单');
INSERT INTO `sys_dict_data`
VALUES (6, 1, '正常', '0', 'sys_normal_disable', '', 'primary', 'Y', '0', 0, '2022-03-06 21:36:39', NULL, NULL,
        '正常状态');
INSERT INTO `sys_dict_data`
VALUES (7, 2, '停用', '1', 'sys_normal_disable', '', 'danger', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL,
        '停用状态');
INSERT INTO `sys_dict_data`
VALUES (8, 1, '正常', '0', 'sys_job_status', '', 'primary', 'Y', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '正常状态');
INSERT INTO `sys_dict_data`
VALUES (9, 2, '暂停', '1', 'sys_job_status', '', 'danger', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '停用状态');
INSERT INTO `sys_dict_data`
VALUES (10, 1, '默认', 'DEFAULT', 'sys_job_group', '', '', 'Y', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '默认分组');
INSERT INTO `sys_dict_data`
VALUES (11, 2, '系统', 'SYSTEM', 'sys_job_group', '', '', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '系统分组');
INSERT INTO `sys_dict_data`
VALUES (12, 1, '是', 'Y', 'sys_yes_no', '', 'primary', 'Y', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '系统默认是');
INSERT INTO `sys_dict_data`
VALUES (13, 2, '否', 'N', 'sys_yes_no', '', 'danger', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '系统默认否');
INSERT INTO `sys_dict_data`
VALUES (14, 1, '通知', '1', 'sys_notice_type', '', 'warning', 'Y', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '通知');
INSERT INTO `sys_dict_data`
VALUES (15, 2, '公告', '2', 'sys_notice_type', '', 'success', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '公告');
INSERT INTO `sys_dict_data`
VALUES (16, 1, '正常', '0', 'sys_notice_status', '', 'primary', 'Y', '0', 0, '2022-03-06 21:36:39', NULL, NULL,
        '正常状态');
INSERT INTO `sys_dict_data`
VALUES (17, 2, '关闭', '1', 'sys_notice_status', '', 'danger', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL,
        '关闭状态');
INSERT INTO `sys_dict_data`
VALUES (18, 1, '新增', '1', 'sys_oper_type', '', 'info', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '新增操作');
INSERT INTO `sys_dict_data`
VALUES (19, 2, '修改', '2', 'sys_oper_type', '', 'info', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '修改操作');
INSERT INTO `sys_dict_data`
VALUES (20, 3, '删除', '3', 'sys_oper_type', '', 'danger', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '删除操作');
INSERT INTO `sys_dict_data`
VALUES (21, 4, '授权', '4', 'sys_oper_type', '', 'primary', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '授权操作');
INSERT INTO `sys_dict_data`
VALUES (22, 5, '导出', '5', 'sys_oper_type', '', 'warning', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '导出操作');
INSERT INTO `sys_dict_data`
VALUES (23, 6, '导入', '6', 'sys_oper_type', '', 'warning', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '导入操作');
INSERT INTO `sys_dict_data`
VALUES (24, 7, '强退', '7', 'sys_oper_type', '', 'danger', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '强退操作');
INSERT INTO `sys_dict_data`
VALUES (25, 8, '生成代码', '8', 'sys_oper_type', '', 'warning', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL,
        '生成操作');
INSERT INTO `sys_dict_data`
VALUES (26, 9, '清空数据', '9', 'sys_oper_type', '', 'danger', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL,
        '清空操作');
INSERT INTO `sys_dict_data`
VALUES (27, 1, '成功', '0', 'sys_common_status', '', 'primary', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL,
        '正常状态');
INSERT INTO `sys_dict_data`
VALUES (28, 2, '失败', '1', 'sys_common_status', '', 'danger', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL,
        '停用状态');
INSERT INTO `sys_dict_data`
VALUES (29, 1, '授权码模式', 'authorization_code', 'sys_grant_type', '', '', 'N', '0', 0, '2022-03-06 21:36:39', NULL,
        NULL, '授权码模式');
INSERT INTO `sys_dict_data`
VALUES (30, 2, '密码模式', 'password', 'sys_grant_type', '', '', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL,
        '密码模式');
INSERT INTO `sys_dict_data`
VALUES (31, 3, '客户端模式', 'client_credentials', 'sys_grant_type', '', '', 'N', '0', 0, '2022-03-06 21:36:39', NULL,
        NULL, '客户端模式');
INSERT INTO `sys_dict_data`
VALUES (32, 4, '简化模式', 'implicit', 'sys_grant_type', '', '', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL,
        '简化模式');
INSERT INTO `sys_dict_data`
VALUES (33, 5, '刷新模式', 'refresh_token', 'sys_grant_type', '', '', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL,
        '刷新模式');
INSERT INTO `sys_dict_data`
VALUES (34, 1, '内部跳转', '0', 'sys_jump_type', '', '', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL,
        '路由内部跳转');
INSERT INTO `sys_dict_data`
VALUES (35, 2, '外部跳转', '1', 'sys_jump_type', '', '', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL,
        '路由外部跳转');
INSERT INTO `sys_dict_data`
VALUES (36, 1, '读&写', '0', 'sys_source_type', '', 'primary', 'Y', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '读&写');
INSERT INTO `sys_dict_data`
VALUES (37, 2, '只读', '1', 'sys_source_type', '', 'success', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '只读');
INSERT INTO `sys_dict_data`
VALUES (38, 3, '只写', '2', 'sys_source_type', '', 'warning', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '只写');
INSERT INTO `sys_dict_data`
VALUES (39, 1, '子数据源', '0', 'sys_database_type', '', 'success', 'Y', '0', 0, '2022-03-06 21:36:39', NULL, NULL,
        '子数据源');
INSERT INTO `sys_dict_data`
VALUES (40, 2, '主数据源', '1', 'sys_database_type', '', 'danger', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL,
        '主数据源');
INSERT INTO `sys_dict_data`
VALUES (41, 1, '自动配置', '0', 'sys_tenant_configuration_type', '', '', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL,
        '自动配置');
INSERT INTO `sys_dict_data`
VALUES (42, 2, '手动配置', '1', 'sys_tenant_configuration_type', '', '', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL,
        '手动配置');
INSERT INTO `sys_dict_data`
VALUES (43, 0, '公共', 'Y', 'sys_common_type', '', '', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '公共');
INSERT INTO `sys_dict_data`
VALUES (44, 1, '私有', 'N', 'sys_common_type', '', '', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '私有');
INSERT INTO `sys_dict_data`
VALUES (45, 0, '全部数据权限', '1', 'sys_data_scope', '', '', 'Y', '0', 0, '2022-03-06 21:36:39', NULL, NULL,
        '全部数据权限');
INSERT INTO `sys_dict_data`
VALUES (46, 1, '自定数据权限', '2', 'sys_data_scope', '', '', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL,
        '自定数据权限');
INSERT INTO `sys_dict_data`
VALUES (47, 2, '本部门数据权限', '3', 'sys_data_scope', '', '', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL,
        '本部门数据权限');
INSERT INTO `sys_dict_data`
VALUES (48, 3, '本部门及以下数据权限', '4', 'sys_data_scope', '', '', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL,
        '本部门及以下数据权限');
INSERT INTO `sys_dict_data`
VALUES (49, 4, '本岗位数据权限', '5', 'sys_data_scope', '', '', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL,
        '本岗位数据权限');
INSERT INTO `sys_dict_data`
VALUES (50, 5, '仅本人数据权限', '6', 'sys_data_scope', '', '', 'N', '0', 0, '2022-03-06 21:36:39', NULL, NULL,
        '仅本人数据权限');

-- ----------------------------
-- Table structure for sys_dict_type
-- ----------------------------
DROP TABLE IF EXISTS `sys_dict_type`;
CREATE TABLE `sys_dict_type`
(
    `dict_id`     bigint                                                         NOT NULL AUTO_INCREMENT COMMENT '字典主键',
    `dict_name`   varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT '字典名称',
    `dict_type`   varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT '字典类型',
    `status`      char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
    `create_by`   bigint                                                         NULL     DEFAULT NULL COMMENT '创建者',
    `create_time` datetime                                                       NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`   bigint                                                         NULL     DEFAULT NULL COMMENT '更新者',
    `update_time` datetime                                                       NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `remark`      varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    PRIMARY KEY (`dict_id`) USING BTREE,
    UNIQUE INDEX `dict_type` (`dict_type` ASC) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 100
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '字典类型表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of sys_dict_type
-- ----------------------------
INSERT INTO `sys_dict_type`
VALUES (1, '用户性别', 'sys_user_sex', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '用户性别列表');
INSERT INTO `sys_dict_type`
VALUES (2, '菜单状态', 'sys_show_hide', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '菜单状态列表');
INSERT INTO `sys_dict_type`
VALUES (3, '系统开关', 'sys_normal_disable', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '系统开关列表');
INSERT INTO `sys_dict_type`
VALUES (4, '任务状态', 'sys_job_status', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '任务状态列表');
INSERT INTO `sys_dict_type`
VALUES (5, '任务分组', 'sys_job_group', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '任务分组列表');
INSERT INTO `sys_dict_type`
VALUES (6, '系统是否', 'sys_yes_no', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '系统是否列表');
INSERT INTO `sys_dict_type`
VALUES (7, '通知类型', 'sys_notice_type', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '通知类型列表');
INSERT INTO `sys_dict_type`
VALUES (8, '通知状态', 'sys_notice_status', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '通知状态列表');
INSERT INTO `sys_dict_type`
VALUES (9, '操作类型', 'sys_oper_type', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '操作类型列表');
INSERT INTO `sys_dict_type`
VALUES (10, '系统状态', 'sys_common_status', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '登录状态列表');
INSERT INTO `sys_dict_type`
VALUES (11, '授权类型', 'sys_grant_type', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '授权类型列表');
INSERT INTO `sys_dict_type`
VALUES (12, '跳转类型', 'sys_jump_type', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '跳转类型列表');
INSERT INTO `sys_dict_type`
VALUES (13, '读写类型', 'sys_source_type', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '读写类型列表');
INSERT INTO `sys_dict_type`
VALUES (14, '数据源类型', 'sys_database_type', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '数据源类型列表');
INSERT INTO `sys_dict_type`
VALUES (15, '配置类型', 'sys_tenant_configuration_type', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '配置类型列表');
INSERT INTO `sys_dict_type`
VALUES (16, '公共是否', 'sys_common_type', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '公共是否列表');
INSERT INTO `sys_dict_type`
VALUES (17, '数据范围', 'sys_data_scope', '0', 0, '2022-03-06 21:36:39', NULL, NULL, '公数据范围列表');

-- ----------------------------
-- Table structure for sys_job
-- ----------------------------
DROP TABLE IF EXISTS `sys_job`;
CREATE TABLE `sys_job`
(
    `job_id`          bigint                                                         NOT NULL COMMENT '任务Id',
    `job_name`        varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL DEFAULT '' COMMENT '任务名称',
    `job_group`       varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL DEFAULT 'DEFAULT' COMMENT '任务组名',
    `invoke_target`   varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NOT NULL COMMENT '调用目标字符串',
    `cron_expression` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT 'cron执行表达式',
    `misfire_policy`  varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL     DEFAULT '3' COMMENT '计划执行错误策略（1立即执行 2执行一次 3放弃执行）',
    `concurrent`      char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NULL     DEFAULT '1' COMMENT '是否并发执行（0允许 1禁止）',
    `status`          char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT '0' COMMENT '状态（0正常 1暂停）',
    `create_by`       bigint                                                         NULL     DEFAULT NULL COMMENT '创建者',
    `create_time`     datetime                                                       NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`       bigint                                                         NULL     DEFAULT NULL COMMENT '更新者',
    `update_time`     datetime                                                       NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `remark`          varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    `del_flag`        tinyint                                                        NOT NULL DEFAULT 0 COMMENT '删除标志(0正常 1删除)',
    `tenant_id`       bigint                                                         NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`job_id`, `job_name`, `job_group`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '定时任务调度表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of sys_job
-- ----------------------------
INSERT INTO `sys_job`
VALUES (1, '系统默认（无参）', 'DEFAULT', 'ryTask.ryNoParams', '0/10 * * * * ?', '3', '1', '1', NULL,
        '2022-03-06 21:36:40', NULL, NULL, NULL, 0, 0);
INSERT INTO `sys_job`
VALUES (2, '系统默认（有参）', 'DEFAULT', 'ryTask.ryParams(\'ry\')', '0/15 * * * * ?', '3', '1', '1', NULL,
        '2022-03-06 21:36:40', NULL, NULL, NULL, 0, 0);
INSERT INTO `sys_job`
VALUES (3, '系统默认（多参）', 'DEFAULT', 'ryTask.ryMultipleParams(\'ry\', true, 2000L, 316.50D, 100)', '0/20 * * * * ?',
        '3', '1', '1', NULL, '2022-03-06 21:36:40', NULL, NULL, NULL, 0, 0);

-- ----------------------------
-- Table structure for sys_job_log
-- ----------------------------
DROP TABLE IF EXISTS `sys_job_log`;
CREATE TABLE `sys_job_log`
(
    `job_log_id`     bigint                                                         NOT NULL AUTO_INCREMENT COMMENT '任务日志Id',
    `job_name`       varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '任务名称',
    `job_group`      varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '任务组名',
    `invoke_target`  varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NOT NULL COMMENT '调用目标字符串',
    `job_message`    varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT NULL COMMENT '日志信息',
    `status`         char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT '0' COMMENT '执行状态（0正常 1失败）',
    `exception_info` varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT '' COMMENT '异常信息',
    `create_time`    datetime                                                       NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `del_time`       datetime                                                       NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '删除时间',
    `del_flag`       tinyint                                                        NOT NULL DEFAULT 0 COMMENT '删除标志(0正常 1删除)',
    `tenant_id`      bigint                                                         NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`job_log_id`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 1
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '定时任务调度日志表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of sys_job_log
-- ----------------------------

-- ----------------------------
-- Table structure for sys_logininfor
-- ----------------------------
DROP TABLE IF EXISTS `sys_logininfor`;
CREATE TABLE `sys_logininfor`
(
    `info_id`         bigint                                                        NOT NULL AUTO_INCREMENT COMMENT '访问Id',
    `enterprise_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT '企业账号',
    `user_name`       varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT '用户账号',
    `user_id`         bigint                                                        NULL     DEFAULT NULL COMMENT '用户Id',
    `ipaddr`          varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT '' COMMENT '登录IP地址',
    `status`          char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci      NULL     DEFAULT '0' COMMENT '登录状态（0成功 1失败）',
    `msg`             varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT '' COMMENT '提示信息',
    `access_time`     datetime                                                      NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '访问时间',
    `del_time`        datetime                                                      NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '删除时间',
    `del_flag`        tinyint                                                       NOT NULL DEFAULT 0 COMMENT '删除标志(0正常 1删除)',
    `tenant_id`       bigint                                                        NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`info_id`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 100
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '系统访问记录'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of sys_logininfor
-- ----------------------------

-- ----------------------------
-- Table structure for sys_menu
-- ----------------------------
DROP TABLE IF EXISTS `sys_menu`;
CREATE TABLE `sys_menu`
(
    `menu_id`     bigint                                                         NOT NULL COMMENT '菜单Id',
    `parent_id`   bigint                                                         NULL     DEFAULT 0 COMMENT '父菜单Id',
    `name`        varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '菜单名称',
    `path`        varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT '路由地址',
    `component`   varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT NULL COMMENT '组件路径',
    `query`       varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT NULL COMMENT '路由参数',
    `is_common`   char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT 'N' COMMENT '公共菜单（Y是 N否）',
    `is_change`   char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT 'N' COMMENT '系统菜单（Y是 N否）',
    `is_frame`    char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT 'N' COMMENT '是否为外链（Y是 N否）',
    `is_cache`    char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT 'Y' COMMENT '是否缓存（Y缓存 N不缓存）',
    `menu_type`   char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NULL     DEFAULT '' COMMENT '菜单类型（M目录 C菜单 F按钮）',
    `visible`     char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT 'Y' COMMENT '菜单状态（Y显示 N隐藏）',
    `perms`       varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT NULL COMMENT '权限标识',
    `icon`        varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '#' COMMENT '菜单图标',
    `sort`        int UNSIGNED                                                   NOT NULL DEFAULT 0 COMMENT '显示顺序',
    `status`      char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
    `create_by`   bigint                                                         NULL     DEFAULT NULL COMMENT '创建者',
    `create_time` datetime                                                       NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`   bigint                                                         NULL     DEFAULT NULL COMMENT '更新者',
    `update_time` datetime                                                       NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `remark`      varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    `del_flag`    tinyint                                                        NOT NULL DEFAULT 0 COMMENT '删除标志(0正常 1删除)',
    `system_id`   bigint                                                         NOT NULL COMMENT '系统Id',
    `tenant_id`   bigint                                                         NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`menu_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '菜单权限表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of sys_menu
-- ----------------------------
INSERT INTO `sys_menu`
VALUES (10100, 0, '组织管理', 'organize', NULL, '', 'Y', 'N', 'N', 'N', 'M', 'Y', '', 'xy_organization', 1, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '组织管理目录', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10110, 10100, '部门管理', 'dept', 'system/organize/dept/index', '', 'Y', 'N', 'N', 'N', 'C', 'Y',
        'system:dept:list', 'xy_dept', 1, '0', 0, '2022-03-06 21:36:38', NULL, NULL, '部门管理菜单', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10111, 10110, '部门查询', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:dept:query', '#', 1, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10112, 10110, '部门新增', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:dept:add', '#', 2, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10113, 10110, '部门修改', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:dept:edit', '#', 3, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10114, 10110, '部门删除', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:dept:remove', '#', 4, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10120, 10100, '岗位管理', 'post', 'system/organize/post/index', '', 'Y', 'N', 'N', 'N', 'C', 'Y',
        'system:post:list', 'xy_post', 2, '0', 0, '2022-03-06 21:36:38', NULL, NULL, '岗位管理菜单', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10121, 10120, '岗位查询', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:post:query', '#', 1, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10122, 10120, '岗位新增', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:post:add', '#', 2, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10123, 10120, '岗位修改', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:post:edit', '#', 3, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10124, 10120, '岗位删除', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:post:remove', '#', 4, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10125, 10120, '岗位导出', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:post:export', '#', 5, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10130, 10100, '用户管理', 'user', 'system/organize/user/index', '', 'Y', 'N', 'N', 'N', 'C', 'Y',
        'system:user:list', 'xy_user', 3, '0', 0, '2022-03-06 21:36:38', NULL, NULL, '用户管理菜单', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10131, 10130, '用户查询', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:user:query', '#', 1, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10132, 10130, '用户新增', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:user:add', '#', 2, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10133, 10130, '用户修改', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:user:edit', '#', 3, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10134, 10130, '用户删除', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:user:remove', '#', 4, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10135, 10130, '用户导出', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:user:export', '#', 5, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10136, 10130, '用户导入', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:user:import', '#', 6, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10137, 10130, '重置密码', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:user:resetPwd', '#', 7, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10200, 0, '企业账户', 'enterprise', NULL, '', 'Y', 'N', 'N', 'N', 'M', 'Y', '', 'xy_enterprise', 2, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '企业账户目录', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10210, 10200, '资料管理', 'dict', 'system/dataSetting/enterprise/profile/index', '', 'Y', 'N', 'N', 'N', 'C',
        'Y', 'system:enterprise:list', 'xy_dict', 1, '0', 0, '2022-03-06 21:36:38', NULL, NULL, '资料管理菜单', 0, 0,
        0);
INSERT INTO `sys_menu`
VALUES (10211, 10210, '资料查看权限', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:enterprise:list', '#', 1, '0',
        0, '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10212, 10210, '普通操作权限', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:enterprise:edit', '#', 2, '0',
        0, '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10213, 10210, '超管操作权限', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:enterpriseAdmin:edit', '#', 3,
        '0', 0, '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10300, 0, '系统管理', 'system', NULL, '', 'Y', 'N', 'N', 'N', 'M', 'Y', '', 'xy_setting', 3, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '系统管理目录', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10310, 10300, '通知公告', 'notice', 'system/system/notice/index', '', 'Y', 'N', 'N', 'N', 'C', 'Y',
        'system:notice:list', 'xy_message', 3, '0', 0, '2022-03-06 21:36:38', NULL, NULL, '通知公告菜单', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10311, 10310, '公告查询', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:notice:query', '#', 1, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10312, 10310, '公告新增', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:notice:add', '#', 2, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10313, 10310, '公告修改', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:notice:edit', '#', 3, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10314, 10310, '公告删除', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:notice:remove', '#', 4, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10320, 10300, '日志管理', 'log', '', '', 'Y', 'N', 'N', 'N', 'M', 'Y', '', 'xy_log', 4, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '日志管理菜单', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10321, 10320, '操作日志', 'operlog', 'system/system/journal/operlog/index', '', 'Y', 'N', 'N', 'N', 'C', 'Y',
        'system:operlog:list', 'xy_log_operation', 1, '0', 0, '2022-03-06 21:36:38', NULL, NULL, '操作日志菜单', 0, 0,
        0);
INSERT INTO `sys_menu`
VALUES (10322, 10321, '操作查询', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:operlog:query', '#', 1, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10323, 10321, '操作删除', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:operlog:remove', '#', 2, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10324, 10321, '日志导出', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:operlog:export', '#', 3, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10325, 10320, '登录日志', 'loginInfo', 'system/system/journal/loginInfo/index', '', 'Y', 'N', 'N', 'N', 'C',
        'Y', 'system:loginInfo:list', 'xy_log_loginInfo', 2, '0', 0, '2022-03-06 21:36:38', NULL, NULL, '登录日志菜单',
        0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10326, 10325, '登录查询', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:loginInfo:query', '#', 1, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10327, 10325, '登录删除', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:loginInfo:remove', '#', 2, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10328, 10325, '日志导出', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:loginInfo:export', '#', 3, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10400, 0, '权限管理', 'authority', NULL, '', 'Y', 'N', 'N', 'N', 'M', 'Y', '', 'xy_authority', 3, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '权限管理目录', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10410, 10400, '角色管理', 'role', 'system/authority/role/index', '', 'Y', 'N', 'N', 'N', 'C', 'Y',
        'system:role:list', 'xy_role', 1, '0', 0, '2022-03-06 21:36:38', NULL, NULL, '角色管理菜单', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10411, 10410, '角色查询', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:role:query', '#', 1, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10412, 10410, '角色授权', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:role:set', '#', 2, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10413, 10410, '角色新增', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:role:add', '#', 3, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10414, 10410, '角色修改', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:role:edit', '#', 4, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10415, 10410, '角色删除', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:role:remove', '#', 5, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10416, 10410, '角色导出', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:role:export', '#', 6, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10420, 10400, '菜单管理', 'menu', 'system/authority/menu/index', '', 'Y', 'N', 'N', 'N', 'C', 'Y',
        'system:menu:list', 'xy_menu', 2, '0', 0, '2022-03-06 21:36:38', NULL, NULL, '菜单管理菜单', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10421, 10420, '菜单查询', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:menu:query', '#', 1, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10422, 10420, '菜单新增', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:menu:add', '#', 2, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10423, 10420, '菜单修改', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:menu:edit', '#', 3, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10424, 10420, '菜单删除', '', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:menu:remove', '#', 4, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10430, 10400, '模块管理', 'system', 'system/authority/system/index', '', 'Y', 'N', 'N', 'N', 'C', 'Y',
        'system:system:list', 'xy_system', 3, '0', 0, '2022-03-06 21:36:38', NULL, NULL, '模块管理菜单', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10431, 10430, '模块查询', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:system:query', '#', 1, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10432, 10430, '模块新增', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:system:add', '#', 2, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10433, 10430, '模块修改', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:system:edit', '#', 3, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10434, 10430, '模块删除', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:system:remove', '#', 4, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10500, 0, '系统监控', 'monitor', NULL, '', 'Y', 'N', 'N', 'N', 'M', 'Y', '', 'xy_monitor', 4, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '系统监控目录', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10510, 10500, '在线用户', 'online', 'system/monitor/online/index', '', 'Y', 'N', 'N', 'N', 'C', 'Y',
        'monitor:online:list', 'xy_online', 1, '0', 0, '2022-03-06 21:36:38', NULL, NULL, '在线用户菜单', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10511, 10510, '在线查询', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'monitor:online:query', '#', 1, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10512, 10510, '批量强退', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'monitor:online:batchLogout', '#', 2, '0',
        0, '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10513, 10510, '单条强退', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'monitor:online:forceLogout', '#', 3, '0',
        0, '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10520, 10500, '定时任务', 'job', 'system/monitor/job/index', '', 'Y', 'N', 'N', 'N', 'C', 'Y',
        'monitor:job:list', 'xy_job', 2, '0', 0, '2022-03-06 21:36:38', NULL, NULL, '定时任务菜单', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10521, 10520, '任务查询', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'monitor:job:query', '#', 1, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10522, 10520, '任务新增', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'monitor:job:add', '#', 2, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10523, 10520, '任务修改', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'monitor:job:edit', '#', 3, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10524, 10520, '任务删除', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'monitor:job:remove', '#', 4, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10525, 10520, '状态修改', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'monitor:job:changeStatus', '#', 5, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10526, 10520, '任务导出', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'monitor:job:export', '#', 6, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10600, 0, '素材管理', NULL, NULL, '', 'Y', 'N', 'N', 'N', 'M', 'N', '', 'xy_tool', 9, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '素材管理目录', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10601, 10600, '素材查询', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:material:query', '#', 1, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10602, 10600, '素材新增', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:material:add', '#', 2, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10603, 10600, '素材编辑', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:material:edit', '#', 3, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (10604, 10600, '素材删除', '#', '', '', 'Y', 'N', 'N', 'N', 'F', 'N', 'system:material:remove', '#', 4, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 0, 0);
INSERT INTO `sys_menu`
VALUES (20000, 0, '租户管理', 'tenant', NULL, '', 'N', 'N', 'N', 'N', 'M', 'Y', '', 'xy_tenant', 6, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '租户管理目录', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20010, 20000, '租户管理', 'tenant', 'tenant/tenant/index', '', 'N', 'N', 'N', 'N', 'C', 'Y',
        'tenant:tenant:list', 'xy_tenant', 1, '0', 0, '2022-03-06 21:36:38', NULL, NULL, '租户管理菜单', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20011, 20010, '租户查询', '#', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'tenant:tenant:query', '#', 1, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20012, 20010, '租户新增', '#', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'tenant:tenant:add', '#', 2, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20013, 20010, '租户修改', '#', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'tenant:tenant:edit', '#', 3, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20014, 20010, '菜单配置', '#', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'tenant:tenant:role', '#', 4, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20015, 20010, '租户删除', '#', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'tenant:tenant:remove', '#', 5, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20020, 20000, '数据源管理', 'source', 'tenant/source/index', '', 'N', 'N', 'N', 'N', 'C', 'Y',
        'tenant:source:list', 'xy_source', 1, '0', 0, '2022-03-06 21:36:38', NULL, NULL, '数据源菜单', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20021, 20020, '数据源查询', '', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'tenant:source:query', '#', 1, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20022, 20020, '数据源新增', '', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'tenant:source:add', '#', 2, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20023, 20020, '数据源修改', '', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'tenant:source:edit', '#', 3, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20024, 20020, '数据源配置', '', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'tenant:separation:edit', '#', 4, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20025, 20020, '数据源删除', '', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'tenant:source:remove', '#', 5, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20050, 20000, '策略管理', 'strategy', 'tenant/strategy/index', '', 'N', 'N', 'N', 'N', 'C', 'Y',
        'tenant:strategy:list', 'xy_strategy', 1, '0', 0, '2022-03-06 21:36:38', NULL, NULL, '数据源策略菜单', 0, 2,
        -1);
INSERT INTO `sys_menu`
VALUES (20051, 20050, '策略查询', '', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'tenant:strategy:query', '#', 1, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20052, 20050, '策略新增', '', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'tenant:strategy:add', '#', 2, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20053, 20050, '策略修改', '', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'tenant:strategy:edit', '#', 3, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20054, 20050, '策略删除', '', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'tenant:strategy:remove', '#', 4, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20055, 20050, '策略导出', '', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'tenant:strategy:export', '#', 5, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20100, 0, '系统管理', 'system', NULL, '', 'N', 'N', 'N', 'N', 'M', 'Y', '', 'xy_setting', 3, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '系统管理目录', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20110, 20100, '字典管理', 'dict', 'system/system/dict/index', '', 'N', 'N', 'N', 'N', 'C', 'Y',
        'system:dict:list', 'xy_dict', 1, '0', 0, '2022-03-06 21:36:38', NULL, NULL, '字典管理菜单', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20111, 20110, '字典查询', '#', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'system:dict:query', '#', 1, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20112, 20110, '字典新增', '#', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'system:dict:add', '#', 2, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20113, 20110, '字典修改', '#', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'system:dict:edit', '#', 3, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20114, 20110, '字典删除', '#', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'system:dict:remove', '#', 4, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20115, 20110, '字典导出', '#', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'system:dict:export', '#', 5, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20120, 20100, '参数管理', 'config', 'system/system/config/index', '', 'N', 'N', 'N', 'N', 'C', 'Y',
        'system:config:list', 'xy_config', 2, '0', 0, '2022-03-06 21:36:38', NULL, NULL, '参数管理菜单', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20121, 20120, '参数查询', '#', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'system:config:query', '#', 1, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20122, 20120, '参数新增', '#', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'system:config:add', '#', 2, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20123, 20120, '参数修改', '#', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'system:config:edit', '#', 3, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20124, 20120, '参数删除', '#', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'system:config:remove', '#', 4, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20125, 20120, '参数导出', '#', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'system:config:export', '#', 5, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20200, 0, '系统监控', 'monitor', NULL, '', 'N', 'N', 'N', 'N', 'M', 'Y', '', 'xy_monitor', 4, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '系统监控目录', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20210, 20200, 'Sentinel控制台', 'http://westChinaBackend:8718', '', '', 'N', 'N', 'Y', 'N', 'C', 'Y',
        'monitor:sentinel:list', 'xy_sentinel', 1, '0', 0, '2022-03-06 21:36:38', NULL, NULL, '流量控制菜单', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20220, 20200, 'Nacos控制台', 'http://westChinaBackend:8848/nacos', '', '', 'N', 'N', 'Y', 'N', 'C', 'Y',
        'monitor:nacos:list', 'xy_nacos', 2, '0', 0, '2022-03-06 21:36:38', NULL, NULL, '服务治理菜单', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20230, 20200, 'Admin控制台', 'http://westChinaUI:9100/login', '', '', 'N', 'N', 'Y', 'N', 'C', 'Y',
        'monitor:server:list', 'xy_server', 3, '0', 0, '2022-03-06 21:36:38', NULL, NULL, '服务监控菜单', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20240, 20200, 'rabbit控制台', 'http://westChinaBackend:15672/#/', '', '', 'N', 'N', 'Y', 'N', 'C', 'Y',
        'monitor:rabbitmq:list', 'xy_rabbit', 4, '0', 0, '2022-03-06 21:36:38', NULL, NULL, '消息队列菜单', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20300, 0, '系统工具', 'tool', NULL, '', 'N', 'N', 'N', 'N', 'M', 'Y', '', 'xy_tool', 5, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '系统工具目录', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20310, 20300, '表单构建', 'build', 'tool/build/index', '', 'N', 'N', 'N', 'N', 'C', 'Y', 'tool:build:list',
        'xy_build', 1, '0', 0, '2022-03-06 21:36:38', NULL, NULL, '表单构建菜单', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20320, 20300, '代码生成', 'gen', 'tool/gen/index', '', 'N', 'N', 'N', 'N', 'C', 'Y', 'tool:gen:list', 'xy_code',
        2, '0', 0, '2022-03-06 21:36:38', NULL, NULL, '代码生成菜单', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20321, 20320, '生成查询', '#', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'tool:gen:query', '#', 1, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20322, 20320, '生成修改', '#', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'tool:gen:edit', '#', 2, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20323, 20320, '生成删除', '#', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'tool:gen:remove', '#', 3, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20324, 20320, '导入代码', '#', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'tool:gen:import', '#', 4, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20325, 20320, '预览代码', '#', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'tool:gen:preview', '#', 5, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20326, 20320, '生成代码', '#', '', '', 'N', 'N', 'N', 'N', 'F', 'N', 'tool:gen:code', '#', 6, '0', 0,
        '2022-03-06 21:36:38', NULL, NULL, '', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (20330, 20300, '系统接口', 'http://westChinaUI:8080/swagger-ui/index.html', '', '', 'N', 'N', 'Y', 'N', 'C', 'Y',
        'tool:swagger:list', 'xy_swagger', 3, '0', 0, '2022-03-06 21:36:38', NULL, NULL, '系统接口菜单', 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (1628293334747533312, 20000, '对象存储管理', 'bucket', 'tenant/bucket/index', NULL, 'N', 'N', 'N', 'N', 'C', 'Y',
        'tenant:bucket:list', 'example', 2, '0', -2, '2023-02-22 07:19:17', -2, '2023-02-22 08:11:41', NULL, 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (1628296473714249728, 20200, 'minio控制台', 'http://westChinaBackend:9001', NULL, NULL, 'N', 'N', 'Y', 'N', 'C',
        'Y', NULL, 'xy_source', 1, '0', -2, '2023-02-22 07:31:46', NULL, NULL, NULL, 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (1628303911859474432, 1628293334747533312, '对象存储空间查询', '', NULL, NULL, 'N', 'N', 'N', 'Y', 'F', 'Y',
        'tenant:bucket:query', '#', 1, '0', -2, '2023-02-22 08:01:19', NULL, NULL, NULL, 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (1628304092340359168, 1628293334747533312, '对象存储空间新增', '', NULL, NULL, 'N', 'N', 'N', 'Y', 'F', 'Y',
        'tenant:bucket:add', '#', 2, '0', -2, '2023-02-22 08:02:02', NULL, NULL, NULL, 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (1628304264768192512, 1628293334747533312, '对象存储空间修改', '', NULL, NULL, 'N', 'N', 'N', 'Y', 'F', 'Y',
        'tenant:bucket:edit', '#', 3, '0', -2, '2023-02-22 08:02:43', NULL, NULL, NULL, 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (1628304455491575808, 1628293334747533312, '对象存储空间删除', '', NULL, NULL, 'N', 'N', 'N', 'Y', 'F', 'Y',
        'tenant:bucket:remove', '#', 4, '0', -2, '2023-02-22 08:03:29', NULL, NULL, NULL, 0, 2, -1);
INSERT INTO `sys_menu`
VALUES (1628304597242298368, 1628293334747533312, '对象存储空间导出', '', NULL, NULL, 'N', 'N', 'N', 'Y', 'F', 'Y',
        'tenant:bucket:export', '#', 5, '0', -2, '2023-02-22 08:04:03', NULL, NULL, NULL, 0, 2, -1);

-- ----------------------------
-- Table structure for sys_notice
-- ----------------------------
DROP TABLE IF EXISTS `sys_notice`;
CREATE TABLE `sys_notice`
(
    `notice_id`      bigint                                                         NOT NULL COMMENT '公告Id',
    `notice_title`   varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '公告标题',
    `notice_type`    char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL COMMENT '公告类型（1通知 2公告）',
    `notice_content` longblob                                                       NULL COMMENT '公告内容',
    `status`         char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NULL     DEFAULT '0' COMMENT '公告状态（0未发送 1已发送）',
    `create_by`      bigint                                                         NULL     DEFAULT NULL COMMENT '创建者',
    `create_time`    datetime                                                       NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`      bigint                                                         NULL     DEFAULT NULL COMMENT '更新者',
    `update_time`    datetime                                                       NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `remark`         varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    `del_flag`       tinyint                                                        NOT NULL DEFAULT 0 COMMENT '删除标志(0正常 1删除)',
    `tenant_id`      bigint                                                         NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`notice_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '通知公告表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of sys_notice
-- ----------------------------

-- ----------------------------
-- Table structure for sys_notice_log
-- ----------------------------
DROP TABLE IF EXISTS `sys_notice_log`;
CREATE TABLE `sys_notice_log`
(
    `notice_id`      bigint                                                         NOT NULL COMMENT '公告Id',
    `user_id`        bigint                                                         NOT NULL COMMENT '用户Id',
    `receive_status` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL COMMENT '发送状态（0成功 1失败）',
    `status`         char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NULL     DEFAULT '0' COMMENT '阅读状态（0未读 1已读）',
    `create_by`      bigint                                                         NULL     DEFAULT NULL COMMENT '创建者',
    `create_time`    datetime                                                       NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`      bigint                                                         NULL     DEFAULT NULL COMMENT '更新者',
    `update_time`    datetime                                                       NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `remark`         varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    `del_flag`       tinyint                                                        NOT NULL DEFAULT 0 COMMENT '删除标志(0正常 1删除)',
    `tenant_id`      bigint                                                         NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`notice_id`, `user_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '通知公告记录表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of sys_notice_log
-- ----------------------------

-- ----------------------------
-- Table structure for sys_oper_log
-- ----------------------------
DROP TABLE IF EXISTS `sys_oper_log`;
CREATE TABLE `sys_oper_log`
(
    `oper_id`        bigint                                                         NOT NULL AUTO_INCREMENT COMMENT '日志主键',
    `title`          varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL     DEFAULT '' COMMENT '模块标题',
    `business_type`  int                                                            NULL     DEFAULT 0 COMMENT '业务类型（0其它 1新增 2修改 3删除）',
    `method`         varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT '方法名称',
    `request_method` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL     DEFAULT '' COMMENT '请求方式',
    `operator_type`  int                                                            NULL     DEFAULT 0 COMMENT '操作类别（0其它 1后台用户 2手机端用户）',
    `user_id`        bigint                                                         NOT NULL COMMENT '操作人员',
    `oper_url`       varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT '请求URL',
    `oper_ip`        varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT '主机地址',
    `oper_location`  varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT '操作地点',
    `oper_param`     varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT '' COMMENT '请求参数',
    `json_result`    varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT '' COMMENT '返回参数',
    `status`         int                                                            NULL     DEFAULT 0 COMMENT '操作状态（0正常 1异常）',
    `error_msg`      varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT '' COMMENT '错误消息',
    `oper_time`      datetime                                                       NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    `del_time`       datetime                                                       NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '删除时间',
    `del_flag`       tinyint                                                        NOT NULL DEFAULT 0 COMMENT '删除标志(0正常 1删除)',
    `tenant_id`      bigint                                                         NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`oper_id`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 138
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '操作日志记录'
  ROW_FORMAT = DYNAMIC;


-- ----------------------------
-- Table structure for sys_organize_role
-- ----------------------------
DROP TABLE IF EXISTS `sys_organize_role`;
CREATE TABLE `sys_organize_role`
(
    `id`                   bigint  NOT NULL AUTO_INCREMENT COMMENT 'id',
    `dept_id`              bigint  NULL     DEFAULT NULL COMMENT '部门id',
    `post_id`              bigint  NULL     DEFAULT NULL COMMENT '岗位id',
    `user_id`              bigint  NULL     DEFAULT NULL COMMENT '用户id',
    `derive_dept_id`       bigint  NULL     DEFAULT NULL COMMENT '部门衍生id',
    `derive_post_id`       bigint  NULL     DEFAULT NULL COMMENT '岗位衍生id',
    `derive_user_id`       bigint  NULL     DEFAULT NULL COMMENT '用户衍生id',
    `derive_enterprise_id` bigint  NULL     DEFAULT NULL COMMENT '企业衍生id',
    `derive_tenant_id`     bigint  NULL     DEFAULT NULL COMMENT '租户衍生id',
    `role_id`              bigint  NOT NULL COMMENT '角色Id',
    `del_flag`             tinyint NOT NULL DEFAULT 0 COMMENT '删除标志（0正常 1删除）',
    `tenant_id`            bigint  NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`id`) USING BTREE,
    UNIQUE INDEX `dept_id` (`dept_id` ASC, `post_id` ASC, `user_id` ASC, `derive_dept_id` ASC, `derive_post_id` ASC,
                            `derive_user_id` ASC, `derive_enterprise_id` ASC, `derive_tenant_id` ASC, `role_id`
                            ASC) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 24
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '组织和角色关联表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of sys_organize_role
-- ----------------------------
INSERT INTO `sys_organize_role`
VALUES (1, NULL, NULL, NULL, NULL, NULL, NULL, NULL, -1, -1, 0, -1);
INSERT INTO `sys_organize_role`
VALUES (3, NULL, NULL, NULL, NULL, NULL, NULL, -1, NULL, -2, 0, -1);
INSERT INTO `sys_organize_role`
VALUES (5, NULL, NULL, NULL, NULL, NULL, -2, NULL, NULL, -3, 0, -1);
INSERT INTO `sys_organize_role`
VALUES (8, NULL, NULL, NULL, NULL, -3, NULL, NULL, NULL, -4, 0, -1);
INSERT INTO `sys_organize_role`
VALUES (13, NULL, NULL, NULL, -4, NULL, NULL, NULL, NULL, -5, 0, -1);

-- ----------------------------
-- Table structure for sys_post
-- ----------------------------
DROP TABLE IF EXISTS `sys_post`;
CREATE TABLE `sys_post`
(
    `post_id`     bigint                                                         NOT NULL COMMENT '岗位Id',
    `dept_id`     bigint                                                         NOT NULL COMMENT '部门Id',
    `post_code`   varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL     DEFAULT NULL COMMENT '岗位编码',
    `post_name`   varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '岗位名称',
    `sort`        int UNSIGNED                                                   NOT NULL DEFAULT 0 COMMENT '显示顺序',
    `status`      char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
    `is_change`   char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT 'N' COMMENT '系统岗位（Y是 N否）',
    `create_by`   bigint                                                         NULL     DEFAULT NULL COMMENT '创建者',
    `create_time` datetime                                                       NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`   bigint                                                         NULL     DEFAULT NULL COMMENT '更新者',
    `update_time` datetime                                                       NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `remark`      varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    `del_flag`    tinyint                                                        NOT NULL DEFAULT 0 COMMENT '删除标志(0正常 1删除)',
    `tenant_id`   bigint                                                         NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`post_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '岗位信息表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of sys_post
-- ----------------------------
INSERT INTO `sys_post`
VALUES (-3, -4, 'ceo', '超级管理员', 0, '0', 'N', NULL, '2022-03-06 16:24:07', NULL, NULL, NULL, 0, -1);

-- ----------------------------
-- Table structure for sys_role
-- ----------------------------
DROP TABLE IF EXISTS `sys_role`;
CREATE TABLE `sys_role`
(
    `role_id`     bigint                                                         NOT NULL COMMENT '角色Id',
    `role_code`   varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL     DEFAULT NULL COMMENT '角色编码',
    `name`        varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '角色名称',
    `role_key`    varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT NULL COMMENT '角色权限字符串',
    `data_scope`  char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NULL     DEFAULT '1' COMMENT '数据范围（1全部数据权限 2自定数据权限 3本部门数据权限 4本部门及以下数据权限 5本岗位数据权限  6仅本人数据权限）',
    `type`        char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT '0' COMMENT '角色类型（0常规 1租户衍生 2企业衍生 3部门衍生 4岗位衍生 5用户衍生）',
    `derive_id`   bigint                                                         NULL     DEFAULT NULL COMMENT '衍生Id',
    `sort`        int UNSIGNED                                                   NOT NULL DEFAULT 0 COMMENT '显示顺序',
    `status`      char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
    `is_change`   char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT 'N' COMMENT '系统角色（Y是 N否）',
    `create_by`   bigint                                                         NULL     DEFAULT NULL COMMENT '创建者',
    `create_time` datetime                                                       NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`   bigint                                                         NULL     DEFAULT NULL COMMENT '更新者',
    `update_time` datetime                                                       NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `remark`      varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    `del_flag`    tinyint                                                        NOT NULL DEFAULT 0 COMMENT '删除标志（0正常 1删除）',
    `tenant_id`   bigint                                                         NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`role_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '角色信息表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of sys_role
-- ----------------------------
INSERT INTO `sys_role`
VALUES (-5, NULL, '部门衍生-1', NULL, '1', '3', -4, 0, '0', 'N', NULL, '2022-03-06 16:24:09', NULL, NULL, NULL, 0, -1);
INSERT INTO `sys_role`
VALUES (-4, NULL, '岗位衍生-1', NULL, '1', '4', -3, 0, '0', 'N', NULL, '2022-03-06 16:24:09', NULL, NULL, NULL, 0, -1);
INSERT INTO `sys_role`
VALUES (-3, NULL, '用户衍生-1', NULL, '1', '5', -2, 0, '0', 'N', NULL, '2022-03-06 16:24:09', NULL, NULL, NULL, 0, -1);
INSERT INTO `sys_role`
VALUES (-2, NULL, '企业衍生-1', NULL, '1', '2', -1, 0, '0', 'N', NULL, '2022-03-06 16:24:09', NULL, NULL, NULL, 0, -1);
INSERT INTO `sys_role`
VALUES (-1, NULL, '租户衍生-1', NULL, '1', '1', -1, 0, '0', 'N', NULL, '2022-03-06 16:24:09', NULL, NULL, NULL, 0, -1);

-- ----------------------------
-- Table structure for sys_role_dept_post
-- ----------------------------
DROP TABLE IF EXISTS `sys_role_dept_post`;
CREATE TABLE `sys_role_dept_post`
(
    `role_id`      bigint                                                   NOT NULL COMMENT '角色Id',
    `dept_post_id` bigint                                                   NOT NULL COMMENT '部门-岗位Id',
    `type`         char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '0' COMMENT '角色类型（0常规 1衍生）',
    `del_flag`     tinyint                                                  NOT NULL DEFAULT 0 COMMENT '删除标志（0正常 1删除）',
    `tenant_id`    bigint                                                   NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`role_id`, `dept_post_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '角色和部门-岗位关联表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of sys_role_dept_post
-- ----------------------------

-- ----------------------------
-- Table structure for sys_role_system_menu
-- ----------------------------
DROP TABLE IF EXISTS `sys_role_system_menu`;
CREATE TABLE `sys_role_system_menu`
(
    `role_id`        bigint                                                   NOT NULL COMMENT '角色Id',
    `system_menu_id` bigint                                                   NOT NULL COMMENT '系统-菜单Id',
    `data_scope`     char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '1' COMMENT '数据范围（1全部数据权限 2自定数据权限 3本部门数据权限 4本部门及以下数据权限 5本岗位数据权限  6仅本人数据权限）',
    `checked`        char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '0' COMMENT '选中类型（0全选 1半选）',
    `del_flag`       tinyint                                                  NOT NULL DEFAULT 0 COMMENT '删除标志（0正常 1删除）',
    `tenant_id`      bigint                                                   NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`role_id`, `system_menu_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '角色和系统-菜单关联表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of sys_role_system_menu
-- ----------------------------

-- ----------------------------
-- Table structure for sys_user
-- ----------------------------
DROP TABLE IF EXISTS `sys_user`;
CREATE TABLE `sys_user`
(
    `user_id`     bigint                                                         NOT NULL COMMENT '用户Id',
    `dept_id`     bigint                                                         NOT NULL COMMENT '部门Id',
    `post_id`     bigint                                                         NOT NULL COMMENT '职位Id',
    `user_code`   varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL     DEFAULT NULL COMMENT '用户编码',
    `user_name`   varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '用户账号',
    `nick_name`   varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '用户昵称',
    `user_type`   varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci    NULL     DEFAULT '01' COMMENT '用户类型（00超管用户 01普通用户）',
    `phone`       varchar(11) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL     DEFAULT '' COMMENT '手机号码',
    `email`       varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL     DEFAULT '' COMMENT '用户邮箱',
    `sex`         char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NULL     DEFAULT '2' COMMENT '用户性别（0男 1女 2保密）',
    `avatar`      varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT '头像地址',
    `profile`     varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '这个人很懒，暂未留下什么' COMMENT '个人简介',
    `password`    varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT '密码',
    `login_ip`    varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT '最后登录IP',
    `login_date`  datetime                                                       NULL     DEFAULT NULL COMMENT '最后登录时间',
    `sort`        int UNSIGNED                                                   NOT NULL DEFAULT 0 COMMENT '显示顺序',
    `status`      char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
    `is_change`   char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT 'N' COMMENT '系统用户（Y是 N否）',
    `create_by`   bigint                                                         NULL     DEFAULT NULL COMMENT '创建者',
    `create_time` datetime                                                       NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`   bigint                                                         NULL     DEFAULT NULL COMMENT '更新者',
    `update_time` datetime                                                       NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `remark`      varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    `del_flag`    tinyint                                                        NOT NULL DEFAULT 0 COMMENT '删除标志(0正常 1删除)',
    `tenant_id`   bigint                                                         NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`user_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '用户信息表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of sys_user
-- ----------------------------
INSERT INTO `sys_user`
VALUES (-2, -4, -3, '001', 'superadmin', 'superadmin', '00', '', '', '2',
        'https://images.gitee.com/uploads/images/2021/1101/141155_f3dfce1d_7382127.jpeg', '这个人很懒，暂未留下什么',
        '$2a$10$hc/Gia308.YMZgTadB90Se8cGpIL78Her8NK/GwjmH0nvQ.UeSt4G', '', NULL, 0, '0', 'N', NULL,
        '2022-03-06 16:24:08', -2, '2022-03-06 20:44:51', '超级管理员', 0, -1);

-- ----------------------------
-- Table structure for xy_material
-- ----------------------------
DROP TABLE IF EXISTS `xy_material`;
CREATE TABLE `xy_material`
(
    `material_id`            bigint                                                        NOT NULL COMMENT '素材Id',
    `folder_id`              bigint                                                        NOT NULL DEFAULT 0 COMMENT '分类Id',
    `material_nick`          varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '素材昵称',
    `material_name`          varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '素材名称',
    `material_original_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '原图名称',
    `material_url`           varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '素材地址',
    `material_original_url`  varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '原图地址',
    `material_size`          decimal(8, 4)                                                 NOT NULL COMMENT '素材大小',
    `type`                   char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci      NOT NULL DEFAULT '0' COMMENT '素材类型（0默认素材 1系统素材）',
    `sort`                   int UNSIGNED                                                  NOT NULL DEFAULT 0 COMMENT '显示顺序',
    `status`                 char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci      NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
    `create_by`              bigint                                                        NULL     DEFAULT NULL COMMENT '创建者',
    `create_time`            datetime                                                      NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`              bigint                                                        NULL     DEFAULT NULL COMMENT '更新者',
    `update_time`            datetime                                                      NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `del_flag`               tinyint                                                       NOT NULL DEFAULT 0 COMMENT '删除标志（0正常 1删除）',
    `tenant_id`              bigint                                                        NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`material_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '素材信息表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of xy_material
-- ----------------------------

-- ----------------------------
-- Table structure for xy_material_folder
-- ----------------------------
DROP TABLE IF EXISTS `xy_material_folder`;
CREATE TABLE `xy_material_folder`
(
    `folder_id`   bigint                                                        NOT NULL COMMENT '分类Id',
    `parent_id`   bigint                                                        NOT NULL DEFAULT 0 COMMENT '父类Id',
    `folder_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '分类名称',
    `ancestors`   varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT '' COMMENT '祖级列表',
    `type`        char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci      NOT NULL DEFAULT '0' COMMENT '分类类型（0默认文件夹 1系统文件夹）',
    `sort`        int UNSIGNED                                                  NOT NULL DEFAULT 0 COMMENT '显示顺序',
    `status`      char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci      NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
    `create_by`   bigint                                                        NULL     DEFAULT NULL COMMENT '创建者',
    `create_time` datetime                                                      NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`   bigint                                                        NULL     DEFAULT NULL COMMENT '更新者',
    `update_time` datetime                                                      NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `del_flag`    tinyint                                                       NOT NULL DEFAULT 0 COMMENT '删除标志（0正常 1删除）',
    `tenant_id`   bigint                                                        NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`folder_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '素材分类表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of xy_material_folder
-- ----------------------------

-- ----------------------------
-- Table structure for xy_system
-- ----------------------------
DROP TABLE IF EXISTS `xy_system`;
CREATE TABLE `xy_system`
(
    `system_id`   bigint                                                         NOT NULL COMMENT '模块Id',
    `name`        varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '模块名称',
    `image_url`   varchar(5000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '图片地址',
    `route`       varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NOT NULL COMMENT '跳转路由|链接',
    `is_common`   char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT 'N' COMMENT '公共模块（Y是 N否）',
    `is_change`   char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT 'N' COMMENT '系统模块（Y是 N否）',
    `type`        char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT '1' COMMENT '跳转类型（0内部跳转 1外部跳转）',
    `is_new`      char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT 'Y' COMMENT '跳转新页（Y是 N否）',
    `visible`     char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT 'Y' COMMENT '页面展示（Y是 N否）',
    `sort`        int UNSIGNED                                                   NOT NULL DEFAULT 0 COMMENT '显示顺序',
    `status`      char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
    `create_by`   bigint                                                         NULL     DEFAULT NULL COMMENT '创建者',
    `create_time` datetime                                                       NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`   bigint                                                         NULL     DEFAULT NULL COMMENT '更新者',
    `update_time` datetime                                                       NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `remark`      varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    `del_flag`    tinyint                                                        NOT NULL DEFAULT 0 COMMENT '删除标志（0正常 1删除）',
    `tenant_id`   bigint                                                         NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`system_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '模块信息表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of xy_system
-- ----------------------------
# INSERT INTO `xy_system`
# VALUES (0, '默认系统',
#         '{\"materialId\":\"1\",\"materialNick\":\"1.jpg\",\"materialUrl\":\"https://images.gitee.com/uploads/images/2021/1101/141155_f3dfce1d_7382127.jpeg\",\"materialOriginalUrl\":\"https://images.gitee.com/uploads/images/2021/1101/141155_f3dfce1d_7382127.jpeg\",\"hiddenVisible\":false}',
#         '', 'Y', 'Y', '1', 'Y', 'N', 0, '0', NULL, '2022-03-06 13:19:52', NULL, NULL, '默认系统', 0, 0);
# INSERT INTO `xy_system`
# VALUES (1, 'CT系统',
#         '{\"materialId\":\"1\",\"materialNick\":\"1.jpg\",\"materialUrl\":\"https://images.gitee.com/uploads/images/2021/1101/141155_f3dfce1d_7382127.jpeg\",\"materialOriginalUrl\":\"https://images.gitee.com/uploads/images/2021/1101/141155_f3dfce1d_7382127.jpeg\",\"hiddenVisible\":false}',
#         'http://westChinaUI:83', 'Y', 'N', '1', 'Y', 'Y', 0, '0', NULL, '2022-03-06 13:19:52', NULL,
#         '2022-03-06 19:44:06', 'ct阅片系统', 0, 0);
# INSERT INTO `xy_system`
# VALUES (2, '租户管理系统',
#         '{\"materialId\":\"1\",\"materialNick\":\"1.jpg\",\"materialUrl\":\"https://images.gitee.com/uploads/images/2021/1101/141601_d68e92a4_7382127.jpeg\",\"materialOriginalUrl\":\"https://images.gitee.com/uploads/images/2021/1101/141601_d68e92a4_7382127.jpeg\",\"hiddenVisible\":false}',
#         'http://westChinaUI:81', 'N', 'Y', '1', 'Y', 'Y', 0, '0', NULL, '2022-03-06 13:19:52', NULL, NULL,
#         '租户管理系统', 0, -1);

INSERT INTO `xy_system`
VALUES (0, '默认系统',
        '{\"materialId\":\"1\",\"materialNick\":\"1.jpg\",\"materialUrl\":\"https://images.gitee.com/uploads/images/2021/1101/141155_f3dfce1d_7382127.jpeg\",\"materialOriginalUrl\":\"https://images.gitee.com/uploads/images/2021/1101/141155_f3dfce1d_7382127.jpeg\",\"hiddenVisible\":false}',
        '', 'Y', 'Y', '1', 'Y', 'N', 0, '0', NULL, '2022-03-06 13:19:52', NULL, NULL, '默认系统', 0, 0);
INSERT INTO `xy_system`
VALUES (1, 'CT系统',
        '{\"materialId\":\"1\",\"materialNick\":\"1.jpg\",\"materialUrl\":\"https://images.gitee.com/uploads/images/2021/1101/141155_f3dfce1d_7382127.jpeg\",\"materialOriginalUrl\":\"https://images.gitee.com/uploads/images/2021/1101/141155_f3dfce1d_7382127.jpeg\",\"hiddenVisible\":false}',
        'http://westChinaUI:5000/ct', 'Y', 'N', '1', 'Y', 'Y', 0, '0', NULL, '2022-03-06 13:19:52', NULL,
        '2022-03-06 19:44:06', 'ct阅片系统', 0, 0);
INSERT INTO `xy_system`
VALUES (2, '租户管理系统',
        '{\"materialId\":\"1\",\"materialNick\":\"1.jpg\",\"materialUrl\":\"https://images.gitee.com/uploads/images/2021/1101/141601_d68e92a4_7382127.jpeg\",\"materialOriginalUrl\":\"https://images.gitee.com/uploads/images/2021/1101/141601_d68e92a4_7382127.jpeg\",\"hiddenVisible\":false}',
        'http://westChinaUI:5000/administrator', 'N', 'Y', '1', 'Y', 'Y', 0, '0', NULL, '2022-03-06 13:19:52', NULL, NULL,
        '租户管理系统', 0, -1);




























-- ----------------------------
-- Table structure for xy_tenant
-- ----------------------------
DROP TABLE IF EXISTS `xy_tenant`;
CREATE TABLE `xy_tenant`
(
    `tenant_id`             bigint                                                         NOT NULL COMMENT '租户Id',
    `strategy_id`           bigint                                                         NOT NULL COMMENT '策略Id',
    `tenant_name`           varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '租户账号',
    `tenant_system_name`    varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '系统名称',
    `tenant_nick`           varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '租户名称',
    `tenant_logo`           varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT '' COMMENT '租户logo',
    `tenant_name_frequency` tinyint                                                        NULL     DEFAULT 0 COMMENT '租户账号修改次数',
    `is_lessor`             char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT 'N' COMMENT '超管租户（Y是 N否）',
    `is_change`             char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT 'N' COMMENT '系统租户（Y是 N否）',
    `sort`                  int UNSIGNED                                                   NOT NULL DEFAULT 0 COMMENT '显示顺序',
    `status`                char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
    `create_by`             bigint                                                         NULL     DEFAULT NULL COMMENT '创建者',
    `create_time`           datetime                                                       NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`             bigint                                                         NULL     DEFAULT NULL COMMENT '更新者',
    `update_time`           datetime                                                       NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `remark`                varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    `del_flag`              tinyint                                                        NOT NULL DEFAULT 0 COMMENT '删除标志（0正常 1删除）',
    PRIMARY KEY (`tenant_id`) USING BTREE,
    UNIQUE INDEX `tenant_name` (`tenant_name` ASC) USING BTREE,
    UNIQUE INDEX `tenant_name_2` (`tenant_name` ASC) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '租户信息表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of xy_tenant
-- ----------------------------
INSERT INTO `xy_tenant`
VALUES (-1, 1, 'superadmin', '华西运维', 'superadmin',
        'https://images.gitee.com/uploads/images/2021/1101/141601_d68e92a4_7382127.jpeg', 1, 'Y', 'Y', 0, '0', NULL,
        '2022-03-06 13:19:50', -2, '2022-03-06 20:43:30', NULL, 0);

-- ----------------------------
-- Table structure for xy_tenant_bucket
-- ----------------------------
DROP TABLE IF EXISTS `xy_tenant_bucket`;
CREATE TABLE `xy_tenant_bucket`
(
    `bucket_id`          bigint                                                        NOT NULL COMMENT '桶Id',
    `bucket_name`        varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '桶名',
    `bucket_tenant_id`   bigint                                                        NOT NULL COMMENT '桶所属的租户',
    `bucket_tenant_name` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '桶所属的租户名',
    `sort`               int UNSIGNED                                                  NOT NULL DEFAULT 0 COMMENT '显示顺序',
    `status`             char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci      NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
    `create_by`          bigint                                                        NULL     DEFAULT NULL COMMENT '创建者',
    `create_time`        datetime                                                      NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`          bigint                                                        NULL     DEFAULT NULL COMMENT '更新者',
    `update_time`        datetime                                                      NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `del_flag`           tinyint                                                       NOT NULL DEFAULT 0 COMMENT '删除标志（0正常 1删除）',
    PRIMARY KEY (`bucket_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '对象存储表，存储租户的桶信息'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of xy_tenant_bucket
-- ----------------------------
INSERT INTO `xy_tenant_bucket`
VALUES (1628304805795631104, 'common', -1, 'superadmin', 0, '0', -2, '2023-02-22 08:04:52', NULL, NULL, 0);

-- ----------------------------
-- Table structure for xy_tenant_separation
-- ----------------------------
DROP TABLE IF EXISTS `xy_tenant_separation`;
CREATE TABLE `xy_tenant_separation`
(
    `write_id`    bigint                                                       NOT NULL COMMENT '写源Id',
    `write_slave` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '写源编码',
    `read_id`     bigint                                                       NOT NULL COMMENT '读源Id',
    `read_slave`  varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '读源编码',
    `del_flag`    tinyint                                                      NOT NULL DEFAULT 0 COMMENT '删除标志（0正常 1删除）',
    PRIMARY KEY (`read_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '主从库关联表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of xy_tenant_separation
-- ----------------------------
INSERT INTO `xy_tenant_separation`
VALUES (1, 'slave', 1, 'slave', 0);

-- ----------------------------
-- Table structure for xy_tenant_source
-- ----------------------------
DROP TABLE IF EXISTS `xy_tenant_source`;
CREATE TABLE `xy_tenant_source`
(
    `source_id`         bigint                                                        NOT NULL COMMENT '数据源Id',
    `name`              varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NOT NULL COMMENT '数据源名称',
    `database_type`     char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci      NOT NULL DEFAULT '0' COMMENT '数据源类型（0子数据源 1主数据源）',
    `is_change`         char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci      NOT NULL DEFAULT 'N' COMMENT '系统主源（Y是 N否）',
    `slave`             varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '数据源编码',
    `driver_class_name` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '驱动',
    `url_prepend`       varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '连接地址',
    `url_append`        varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '连接参数',
    `username`          varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '用户名',
    `password`          varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '密码',
    `type`              char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci      NOT NULL DEFAULT '0' COMMENT '读写类型（0读&写 1只读 2只写）',
    `sort`              int UNSIGNED                                                  NOT NULL DEFAULT 0 COMMENT '显示顺序',
    `status`            char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci      NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
    `create_by`         bigint                                                        NULL     DEFAULT NULL COMMENT '创建者',
    `create_time`       datetime                                                      NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`         bigint                                                        NULL     DEFAULT NULL COMMENT '更新者',
    `update_time`       datetime                                                      NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `del_flag`          tinyint                                                       NOT NULL DEFAULT 0 COMMENT '删除标志（0正常 1删除）',
    PRIMARY KEY (`source_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '数据源表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of xy_tenant_source
-- ----------------------------
INSERT INTO `xy_tenant_source`
VALUES (1, '华西运维数据源', '0', 'Y', 'slave', 'com.mysql.cj.jdbc.Driver',
        'jdbc:mysql://westChinaBackend:3306/xy-cloud',
        '?useUnicode=true&characterEncoding=utf8&zeroDateTimeBehavior=convertToNull&useSSL=true&serverTimezone=GMT%2B8',
        'root', '123456', '0', 0, '0', NULL, '2022-03-06 13:19:50', NULL, '2022-03-06 13:29:47', 0);

-- ----------------------------
-- Table structure for xy_tenant_strategy
-- ----------------------------
DROP TABLE IF EXISTS `xy_tenant_strategy`;
CREATE TABLE `xy_tenant_strategy`
(
    `strategy_id`   bigint                                                        NOT NULL COMMENT '策略Id',
    `name`          varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '策略名称',
    `tenant_amount` int UNSIGNED                                                  NOT NULL DEFAULT 0 COMMENT '租户数量',
    `source_amount` int UNSIGNED                                                  NOT NULL DEFAULT 0 COMMENT '数据源数量',
    `is_change`     char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci      NOT NULL DEFAULT 'N' COMMENT '系统策略（Y是 N否）',
    `sort`          int UNSIGNED                                                  NOT NULL DEFAULT 0 COMMENT '显示顺序',
    `status`        char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci      NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
    `create_by`     bigint                                                        NULL     DEFAULT NULL COMMENT '创建者',
    `create_time`   datetime                                                      NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`     bigint                                                        NULL     DEFAULT NULL COMMENT '更新者',
    `update_time`   datetime                                                      NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `del_flag`      tinyint                                                       NOT NULL DEFAULT 0 COMMENT '删除标志（0正常 1删除）',
    PRIMARY KEY (`strategy_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '数据源策略表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of xy_tenant_strategy
-- ----------------------------
INSERT INTO `xy_tenant_strategy`
VALUES (1, '华西运维数据源策略', 2, 1, 'Y', 1, '0', NULL, '2022-03-06 13:19:50', NULL, NULL, 0);

-- ----------------------------
-- Table structure for xy_tenant_strategy_source
-- ----------------------------
DROP TABLE IF EXISTS `xy_tenant_strategy_source`;
CREATE TABLE `xy_tenant_strategy_source`
(
    `strategy_id` bigint                                                   NOT NULL COMMENT '策略Id',
    `source_id`   bigint                                                   NOT NULL COMMENT '数据源Id',
    `is_main`     char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'N' COMMENT '主数据源（Y是 N否）',
    `del_flag`    tinyint                                                  NOT NULL DEFAULT 0 COMMENT '删除标志（0正常 1删除）',
    PRIMARY KEY (`strategy_id`, `source_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '策略-数据源关联表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of xy_tenant_strategy_source
-- ----------------------------
INSERT INTO `xy_tenant_strategy_source`
VALUES (1, 1, 'Y', 0);

SET
    FOREIGN_KEY_CHECKS = 1;
