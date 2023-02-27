/*
 Navicat Premium Data Transfer

 Source Server         : huaxi
 Source Server Type    : MySQL
 Source Server Version : 50735
 Source Host           : localhost:3306
 Source Schema         : xy-cloud1

 Target Server Type    : MySQL
 Target Server Version : 50735
 File Encoding         : 65001

 Date: 06/03/2022 21:45:17
*/

DROP
    DATABASE IF EXISTS `xy-cloud1`;

CREATE
    DATABASE `xy-cloud1` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

SET NAMES utf8mb4;
SET
    FOREIGN_KEY_CHECKS = 0;

USE
    `xy-cloud1`;

DROP TABLE IF EXISTS `ct_dicom`;
CREATE TABLE `ct_dicom`
(
    `dicom_id`              bigint                                                         NOT NULL COMMENT 'id',
    `pat_card_id`           varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '身份证号',
    `dicom_ct_time`         varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL     DEFAULT NULL COMMENT 'ct拍摄时间',
    `dicom_ct_study_uid`    varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT NULL COMMENT '研究UId',
    `dicom_ct_series_uid`   varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT NULL COMMENT '序列UId',
    `dicom_ct_body`         varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT NULL COMMENT '检查的身体部位',
    `dicom_ct_path`         varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '序列第一张的存储地址',
    `dicom_ct_count`        int                                                            NULL     DEFAULT NULL COMMENT '一个序列的dicom数量',
    `dicom_ct_description` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    `sort`                  int UNSIGNED                                                   NOT NULL DEFAULT 0 COMMENT '显示顺序',
    `create_by`             bigint                                                         NULL     DEFAULT NULL COMMENT '创建者',
    `create_time`           datetime                                                       NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`             bigint                                                         NULL     DEFAULT NULL COMMENT '更新者',
    `update_time`           datetime                                                       NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `remark`                varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    `del_flag`              tinyint                                                        NOT NULL DEFAULT 0 COMMENT '删除标志（0正常 1删除）',
    `tenant_id`             bigint                                                         NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`dicom_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '病人dicom存储记录表'
  ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for ct_patients
-- ----------------------------
DROP TABLE IF EXISTS `ct_patients`;
CREATE TABLE `ct_patients`
(
    `pat_id`      bigint(20)                                                     NOT NULL COMMENT '唯一id，标识病人',
    `pat_card_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '身份证号',
    `pat_name`    varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL     DEFAULT NULL COMMENT '病人姓名',
    `pat_phone`   varchar(11) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL     DEFAULT NULL COMMENT '病人手机号码',
    `sort`        int(10) UNSIGNED                                               NOT NULL DEFAULT 0 COMMENT '显示顺序',
    `create_by`   bigint(20)                                                     NULL     DEFAULT NULL COMMENT '创建者',
    `create_time` datetime(0)                                                    NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`   bigint(20)                                                     NULL     DEFAULT NULL COMMENT '更新者',
    `update_time` datetime(0)                                                    NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '更新时间',
    `remark`      varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    `del_flag`    tinyint(4)                                                     NOT NULL DEFAULT 0 COMMENT '删除标志（0正常 1删除）',
    `tenant_id`   bigint(20)                                                     NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`pat_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '病人信息表'
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for sys_dept
-- ----------------------------
DROP TABLE IF EXISTS `sys_dept`;
CREATE TABLE `sys_dept`
(
    `dept_id`     bigint(20)                                                      NOT NULL COMMENT '部门id',
    `parent_id`   bigint(20)                                                      NULL     DEFAULT 0 COMMENT '父部门id',
    `dept_code`   varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci    NULL     DEFAULT NULL COMMENT '部门编码',
    `dept_name`   varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci    NULL     DEFAULT '' COMMENT '部门名称',
    `ancestors`   varchar(10000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT '' COMMENT '祖级列表',
    `leader`      varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci    NULL     DEFAULT '' COMMENT '负责人',
    `phone`       varchar(11) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci    NULL     DEFAULT '' COMMENT '联系电话',
    `email`       varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci    NULL     DEFAULT '' COMMENT '邮箱',
    `sort`        int(10) UNSIGNED                                                NOT NULL DEFAULT 0 COMMENT '显示顺序',
    `status`      char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci        NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
    `is_change`   char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci        NOT NULL DEFAULT 'N' COMMENT '系统部门（Y是 N否）',
    `create_by`   bigint(20)                                                      NULL     DEFAULT NULL COMMENT '创建者',
    `create_time` datetime(0)                                                     NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`   bigint(20)                                                      NULL     DEFAULT NULL COMMENT '更新者',
    `update_time` datetime(0)                                                     NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '更新时间',
    `remark`      varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT NULL COMMENT '备注',
    `del_flag`    tinyint(4)                                                      NOT NULL DEFAULT 0 COMMENT '删除标志(0正常 1删除)',
    `tenant_id`   bigint(20)                                                      NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`dept_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '部门表'
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for sys_logininfor
-- ----------------------------
DROP TABLE IF EXISTS `sys_logininfor`;
CREATE TABLE `sys_logininfor`
(
    `info_id`         bigint(20)                                                    NOT NULL AUTO_INCREMENT COMMENT '访问Id',
    `enterprise_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT '企业账号',
    `user_name`       varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT '用户账号',
    `user_id`         bigint(20)                                                    NULL     DEFAULT NULL COMMENT '用户Id',
    `ipaddr`          varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT '' COMMENT '登录IP地址',
    `status`          char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci      NULL     DEFAULT '0' COMMENT '登录状态（0成功 1失败）',
    `msg`             varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT '' COMMENT '提示信息',
    `access_time`     datetime(0)                                                   NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '访问时间',
    `del_time`        datetime(0)                                                   NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '删除时间',
    `del_flag`        tinyint(4)                                                    NOT NULL DEFAULT 0 COMMENT '删除标志(0正常 1删除)',
    `tenant_id`       bigint(20)                                                    NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`info_id`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 100
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '系统访问记录'
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for sys_notice
-- ----------------------------
DROP TABLE IF EXISTS `sys_notice`;
CREATE TABLE `sys_notice`
(
    `notice_id`      bigint(20)                                                     NOT NULL COMMENT '公告Id',
    `notice_title`   varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '公告标题',
    `notice_type`    char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL COMMENT '公告类型（1通知 2公告）',
    `notice_content` longblob                                                       NULL COMMENT '公告内容',
    `status`         char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NULL     DEFAULT '0' COMMENT '公告状态（0未发送 1已发送）',
    `create_by`      bigint(20)                                                     NULL     DEFAULT NULL COMMENT '创建者',
    `create_time`    datetime(0)                                                    NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`      bigint(20)                                                     NULL     DEFAULT NULL COMMENT '更新者',
    `update_time`    datetime(0)                                                    NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '更新时间',
    `remark`         varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    `del_flag`       tinyint(4)                                                     NOT NULL DEFAULT 0 COMMENT '删除标志(0正常 1删除)',
    `tenant_id`      bigint(20)                                                     NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`notice_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '通知公告表'
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for sys_notice_log
-- ----------------------------
DROP TABLE IF EXISTS `sys_notice_log`;
CREATE TABLE `sys_notice_log`
(
    `notice_id`      bigint(20)                                                     NOT NULL COMMENT '公告Id',
    `user_id`        bigint(20)                                                     NOT NULL COMMENT '用户Id',
    `receive_status` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL COMMENT '发送状态（0成功 1失败）',
    `status`         char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NULL     DEFAULT '0' COMMENT '阅读状态（0未读 1已读）',
    `create_by`      bigint(20)                                                     NULL     DEFAULT NULL COMMENT '创建者',
    `create_time`    datetime(0)                                                    NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`      bigint(20)                                                     NULL     DEFAULT NULL COMMENT '更新者',
    `update_time`    datetime(0)                                                    NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '更新时间',
    `remark`         varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    `del_flag`       tinyint(4)                                                     NOT NULL DEFAULT 0 COMMENT '删除标志(0正常 1删除)',
    `tenant_id`      bigint(20)                                                     NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`notice_id`, `user_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '通知公告记录表'
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for sys_oper_log
-- ----------------------------
DROP TABLE IF EXISTS `sys_oper_log`;
CREATE TABLE `sys_oper_log`
(
    `oper_id`        bigint(20)                                                     NOT NULL AUTO_INCREMENT COMMENT '日志主键',
    `title`          varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL     DEFAULT '' COMMENT '模块标题',
    `business_type`  int(2)                                                         NULL     DEFAULT 0 COMMENT '业务类型（0其它 1新增 2修改 3删除）',
    `method`         varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT '方法名称',
    `request_method` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL     DEFAULT '' COMMENT '请求方式',
    `operator_type`  int(1)                                                         NULL     DEFAULT 0 COMMENT '操作类别（0其它 1后台用户 2手机端用户）',
    `user_id`        bigint(20)                                                     NOT NULL COMMENT '操作人员',
    `oper_url`       varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT '请求URL',
    `oper_ip`        varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT '主机地址',
    `oper_location`  varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT '' COMMENT '操作地点',
    `oper_param`     varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT '' COMMENT '请求参数',
    `json_result`    varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT '' COMMENT '返回参数',
    `status`         int(1)                                                         NULL     DEFAULT 0 COMMENT '操作状态（0正常 1异常）',
    `error_msg`      varchar(2000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT '' COMMENT '错误消息',
    `oper_time`      datetime(0)                                                    NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    `del_time`       datetime(0)                                                    NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '删除时间',
    `del_flag`       tinyint(4)                                                     NOT NULL DEFAULT 0 COMMENT '删除标志(0正常 1删除)',
    `tenant_id`      bigint(20)                                                     NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`oper_id`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 100
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '操作日志记录'
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for sys_organize_role
-- ----------------------------
DROP TABLE IF EXISTS `sys_organize_role`;
CREATE TABLE `sys_organize_role`
(
    `id`                   bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'id',
    `dept_id`              bigint(20) NULL     DEFAULT NULL COMMENT '部门id',
    `post_id`              bigint(20) NULL     DEFAULT NULL COMMENT '岗位id',
    `user_id`              bigint(20) NULL     DEFAULT NULL COMMENT '用户id',
    `derive_dept_id`       bigint(20) NULL     DEFAULT NULL COMMENT '部门衍生id',
    `derive_post_id`       bigint(20) NULL     DEFAULT NULL COMMENT '岗位衍生id',
    `derive_user_id`       bigint(20) NULL     DEFAULT NULL COMMENT '用户衍生id',
    `derive_enterprise_id` bigint(20) NULL     DEFAULT NULL COMMENT '企业衍生id',
    `derive_tenant_id`     bigint(20) NULL     DEFAULT NULL COMMENT '租户衍生id',
    `role_id`              bigint(20) NOT NULL COMMENT '角色Id',
    `del_flag`             tinyint(4) NOT NULL DEFAULT 0 COMMENT '删除标志（0正常 1删除）',
    `tenant_id`            bigint(20) NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`id`) USING BTREE,
    UNIQUE INDEX `dept_id` (`dept_id`, `post_id`, `user_id`, `derive_dept_id`, `derive_post_id`, `derive_user_id`,
                            `derive_enterprise_id`, `derive_tenant_id`, `role_id`) USING BTREE
) ENGINE = InnoDB
  AUTO_INCREMENT = 1
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '组织和角色关联表'
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for sys_post
-- ----------------------------
DROP TABLE IF EXISTS `sys_post`;
CREATE TABLE `sys_post`
(
    `post_id`     bigint(20)                                                     NOT NULL COMMENT '岗位Id',
    `dept_id`     bigint(20)                                                     NOT NULL COMMENT '部门Id',
    `post_code`   varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL     DEFAULT NULL COMMENT '岗位编码',
    `post_name`   varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '岗位名称',
    `sort`        int(10) UNSIGNED                                               NOT NULL DEFAULT 0 COMMENT '显示顺序',
    `status`      char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
    `is_change`   char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT 'N' COMMENT '系统岗位（Y是 N否）',
    `create_by`   bigint(20)                                                     NULL     DEFAULT NULL COMMENT '创建者',
    `create_time` datetime(0)                                                    NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`   bigint(20)                                                     NULL     DEFAULT NULL COMMENT '更新者',
    `update_time` datetime(0)                                                    NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '更新时间',
    `remark`      varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    `del_flag`    tinyint(4)                                                     NOT NULL DEFAULT 0 COMMENT '删除标志(0正常 1删除)',
    `tenant_id`   bigint(20)                                                     NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`post_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '岗位信息表'
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for sys_role
-- ----------------------------
DROP TABLE IF EXISTS `sys_role`;
CREATE TABLE `sys_role`
(
    `role_id`     bigint(20)                                                     NOT NULL COMMENT '角色Id',
    `role_code`   varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NULL     DEFAULT NULL COMMENT '角色编码',
    `name`        varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '角色名称',
    `role_key`    varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NULL     DEFAULT NULL COMMENT '角色权限字符串',
    `data_scope`  char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NULL     DEFAULT '1' COMMENT '数据范围（1全部数据权限 2自定数据权限 3本部门数据权限 4本部门及以下数据权限 5本岗位数据权限  6仅本人数据权限）',
    `type`        char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT '0' COMMENT '角色类型（0常规 1租户衍生 2企业衍生 3部门衍生 4岗位衍生 5用户衍生）',
    `derive_id`   bigint(20)                                                     NULL     DEFAULT NULL COMMENT '衍生Id',
    `sort`        int(10) UNSIGNED                                               NOT NULL DEFAULT 0 COMMENT '显示顺序',
    `status`      char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
    `is_change`   char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT 'N' COMMENT '系统角色（Y是 N否）',
    `create_by`   bigint(20)                                                     NULL     DEFAULT NULL COMMENT '创建者',
    `create_time` datetime(0)                                                    NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`   bigint(20)                                                     NULL     DEFAULT NULL COMMENT '更新者',
    `update_time` datetime(0)                                                    NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '更新时间',
    `remark`      varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    `del_flag`    tinyint(4)                                                     NOT NULL DEFAULT 0 COMMENT '删除标志（0正常 1删除）',
    `tenant_id`   bigint(20)                                                     NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`role_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '角色信息表'
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for sys_role_dept_post
-- ----------------------------
DROP TABLE IF EXISTS `sys_role_dept_post`;
CREATE TABLE `sys_role_dept_post`
(
    `role_id`      bigint(20)                                               NOT NULL COMMENT '角色Id',
    `dept_post_id` bigint(20)                                               NOT NULL COMMENT '部门-岗位Id',
    `type`         char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '0' COMMENT '角色类型（0常规 1衍生）',
    `del_flag`     tinyint(4)                                               NOT NULL DEFAULT 0 COMMENT '删除标志（0正常 1删除）',
    `tenant_id`    bigint(20)                                               NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`role_id`, `dept_post_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '角色和部门-岗位关联表'
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for sys_role_system_menu
-- ----------------------------
DROP TABLE IF EXISTS `sys_role_system_menu`;
CREATE TABLE `sys_role_system_menu`
(
    `role_id`        bigint(20)                                               NOT NULL COMMENT '角色Id',
    `system_menu_id` bigint(20)                                               NOT NULL COMMENT '系统-菜单Id',
    `data_scope`     char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '1' COMMENT '数据范围（1全部数据权限 2自定数据权限 3本部门数据权限 4本部门及以下数据权限 5本岗位数据权限  6仅本人数据权限）',
    `checked`        char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL DEFAULT '0' COMMENT '选中类型（0全选 1半选）',
    `del_flag`       tinyint(4)                                               NOT NULL DEFAULT 0 COMMENT '删除标志（0正常 1删除）',
    `tenant_id`      bigint(20)                                               NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`role_id`, `system_menu_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '角色和系统-菜单关联表'
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for sys_user
-- ----------------------------
DROP TABLE IF EXISTS `sys_user`;
CREATE TABLE `sys_user`
(
    `user_id`     bigint(20)                                                     NOT NULL COMMENT '用户Id',
    `dept_id`     bigint(20)                                                     NOT NULL COMMENT '部门Id',
    `post_id`     bigint(20)                                                     NOT NULL COMMENT '职位Id',
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
    `login_date`  datetime(0)                                                    NULL     DEFAULT NULL COMMENT '最后登录时间',
    `sort`        int(10) UNSIGNED                                               NOT NULL DEFAULT 0 COMMENT '显示顺序',
    `status`      char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
    `is_change`   char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci       NOT NULL DEFAULT 'N' COMMENT '系统用户（Y是 N否）',
    `create_by`   bigint(20)                                                     NULL     DEFAULT NULL COMMENT '创建者',
    `create_time` datetime(0)                                                    NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`   bigint(20)                                                     NULL     DEFAULT NULL COMMENT '更新者',
    `update_time` datetime(0)                                                    NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '更新时间',
    `remark`      varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT NULL COMMENT '备注',
    `del_flag`    tinyint(4)                                                     NOT NULL DEFAULT 0 COMMENT '删除标志(0正常 1删除)',
    `tenant_id`   bigint(20)                                                     NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`user_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '用户信息表'
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for xy_material
-- ----------------------------
DROP TABLE IF EXISTS `xy_material`;
CREATE TABLE `xy_material`
(
    `material_id`            bigint(20)                                                    NOT NULL COMMENT '素材Id',
    `folder_id`              bigint(20)                                                    NOT NULL DEFAULT 0 COMMENT '分类Id',
    `material_nick`          varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '素材昵称',
    `material_name`          varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '素材名称',
    `material_original_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '原图名称',
    `material_url`           varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '素材地址',
    `material_original_url`  varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '原图地址',
    `material_size`          decimal(8, 4)                                                 NOT NULL COMMENT '素材大小',
    `type`                   char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci      NOT NULL DEFAULT '0' COMMENT '素材类型（0默认素材 1系统素材）',
    `sort`                   int(10) UNSIGNED                                              NOT NULL DEFAULT 0 COMMENT '显示顺序',
    `status`                 char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci      NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
    `create_by`              bigint(20)                                                    NULL     DEFAULT NULL COMMENT '创建者',
    `create_time`            datetime(0)                                                   NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`              bigint(20)                                                    NULL     DEFAULT NULL COMMENT '更新者',
    `update_time`            datetime(0)                                                   NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '更新时间',
    `del_flag`               tinyint(4)                                                    NOT NULL DEFAULT 0 COMMENT '删除标志（0正常 1删除）',
    `tenant_id`              bigint(20)                                                    NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`material_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '素材信息表'
  ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for xy_material_folder
-- ----------------------------
DROP TABLE IF EXISTS `xy_material_folder`;
CREATE TABLE `xy_material_folder`
(
    `folder_id`   bigint(20)                                                    NOT NULL COMMENT '分类Id',
    `parent_id`   bigint(20)                                                    NOT NULL DEFAULT 0 COMMENT '父类Id',
    `folder_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '分类名称',
    `ancestors`   varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL     DEFAULT '' COMMENT '祖级列表',
    `type`        char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci      NOT NULL DEFAULT '0' COMMENT '分类类型（0默认文件夹 1系统文件夹）',
    `sort`        int(10) UNSIGNED                                              NOT NULL DEFAULT 0 COMMENT '显示顺序',
    `status`      char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci      NOT NULL DEFAULT '0' COMMENT '状态（0正常 1停用）',
    `create_by`   bigint(20)                                                    NULL     DEFAULT NULL COMMENT '创建者',
    `create_time` datetime(0)                                                   NULL     DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_by`   bigint(20)                                                    NULL     DEFAULT NULL COMMENT '更新者',
    `update_time` datetime(0)                                                   NULL     DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP(0) COMMENT '更新时间',
    `del_flag`    tinyint(4)                                                    NOT NULL DEFAULT 0 COMMENT '删除标志（0正常 1删除）',
    `tenant_id`   bigint(20)                                                    NOT NULL COMMENT '租户Id',
    PRIMARY KEY (`folder_id`) USING BTREE
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci COMMENT = '素材分类表'
  ROW_FORMAT = Dynamic;

SET
    FOREIGN_KEY_CHECKS = 1;
