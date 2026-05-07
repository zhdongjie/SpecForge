/*
 Navicat Premium Data Transfer

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 80031 (8.0.31)
 Source Host           : localhost:3306
 Source Schema         : original

 Target Server Type    : MySQL
 Target Server Version : 80031 (8.0.31)
 File Encoding         : 65001

 Date: 25/06/2025 10:51:41
*/

SET NAMES utf8mb4;
SET
FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for system_access_log
-- ----------------------------
DROP TABLE IF EXISTS `system_access_log`;
CREATE TABLE `system_access_log`
(
    `id`               bigint                                                        NOT NULL COMMENT '主键ID',
    `username`         varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '访问的用户名',
    `access_ip`        varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '访问IP地址',
    `access_location`  varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '访问地理位置',
    `browser`          varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '浏览器类型',
    `operating_system` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '操作系统',
    `access_type`      varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NOT NULL COMMENT '访问类型（REGISTER:注册 LOGIN:登录 LOGOUT:登出）',
    `access_status`    varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NOT NULL COMMENT '访问状态（FAILED:失败 SUCCESS:成功）',
    `prompt_message`   varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '提示信息',
    `access_time`      timestamp                                                     NOT NULL COMMENT '访问时间',
    PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '系统访问日志表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of system_access_log
-- ----------------------------

-- ----------------------------
-- Table structure for system_dictionary_data
-- ----------------------------
DROP TABLE IF EXISTS `system_dictionary_data`;
CREATE TABLE `system_dictionary_data`
(
    `id`                     bigint                                                       NOT NULL COMMENT '主键ID',
    `dictionary_type_code`   varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '字典类型代码',
    `value`                  varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '字典值',
    `sort`                   int                                                          NOT NULL COMMENT '显示顺序',
    `dictionary_data_status` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '字典数据状态（ENABLED:正常 DISABLED:停用）',
    `created_time`           timestamp                                                    NOT NULL COMMENT '创建时间',
    `created_by`             bigint NULL DEFAULT NULL COMMENT '创建人ID',
    `last_modified_time`     timestamp                                                    NOT NULL COMMENT '最后修改时间',
    `last_modified_by`       bigint NULL DEFAULT NULL COMMENT '最后修改人ID',
    PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '系统字典数据表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of system_dictionary_data
-- ----------------------------
INSERT INTO `system_dictionary_data`
VALUES (20250000000000001, 'system_language_code', 'zh-CN', 1, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000002, 'system_language_code', 'en-US', 2, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000003, 'system_role_status', 'ENABLED', 1, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000004, 'system_role_status', 'DISABLED', 2, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000005, 'system_permission_type', 'SUBHEADER', 1, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000006, 'system_permission_type', 'GROUP', 2, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000007, 'system_permission_type', 'TEMPLATE', 3, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000008, 'system_permission_type', 'LINK', 4, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000009, 'system_permission_type', 'BUTTON', 5, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000010, 'system_permission_type', 'FUNCTION', 6, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000011, 'system_permission_link_target', '_blank', 1, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000012, 'system_permission_link_target', '_self', 2, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000013, 'system_permission_status', 'ENABLED', 1, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000014, 'system_permission_status', 'DISABLED', 2, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000015, 'system_file_type_size_unit', 'B', 1, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000016, 'system_file_type_size_unit', 'KB', 2, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000017, 'system_file_type_size_unit', 'MB', 3, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000018, 'system_file_type_size_unit', 'GB', 4, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000019, 'system_file_type_status', 'ENABLED', 1, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000020, 'system_file_type_status', 'DISABLED', 2, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000021, 'system_file_metadata_status', 'ENABLED', 1, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000022, 'system_file_metadata_status', 'DISABLED', 2, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000023, 'system_scheduled_task_group', 'DEFAULT', 1, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000024, 'system_scheduled_task_group', 'SYSTEM', 2, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000025, 'system_scheduled_misfire_policy', 'DEFAULT', 1, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000026, 'system_scheduled_misfire_policy', 'IGNORE_MISFIRES', 2, 'ENABLED', '2025-01-01 00:00:00',
        NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000027, 'system_scheduled_misfire_policy', 'FIRE_AND_PROCEED', 3, 'ENABLED', '2025-01-01 00:00:00',
        NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000028, 'system_scheduled_misfire_policy', 'DO_NOTHING', 4, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000029, 'system_scheduled_task_status', 'ENABLED', 1, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000030, 'system_scheduled_task_status', 'DISABLED', 2, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000031, 'system_dictionary_type_status', 'ENABLED', 1, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000032, 'system_dictionary_type_status', 'DISABLED', 2, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000033, 'system_dictionary_data_status', 'ENABLED', 1, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000034, 'system_dictionary_data_status', 'DISABLED', 2, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000035, 'system_user_gender', 'MALE', 1, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_data`
VALUES (20250000000000036, 'system_user_gender', 'FEMALE', 2, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);

-- ----------------------------
-- Table structure for system_dictionary_data_translation
-- ----------------------------
DROP TABLE IF EXISTS `system_dictionary_data_translation`;
CREATE TABLE `system_dictionary_data_translation`
(
    `id`                 bigint                                                       NOT NULL COMMENT '主键ID',
    `dictionary_data_id` bigint                                                       NOT NULL COMMENT '字典数据ID',
    `language_code`      varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '语言代码（zh-CN:简体中文 en-US:英文）',
    `label`              varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '字典显示标签',
    `remark`             varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '备注信息',
    PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '系统字典数据翻译表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of system_dictionary_data_translation
-- ----------------------------
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000001, 20250000000000001, 'zh-CN', '简体中文', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000002, 20250000000000001, 'en-US', 'Simplified Chinese', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000003, 20250000000000002, 'zh-CN', '英文', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000004, 20250000000000002, 'en-US', 'English', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000005, 20250000000000003, 'zh-CN', '启用', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000006, 20250000000000003, 'en-US', 'Enabled', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000007, 20250000000000004, 'zh-CN', '禁用', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000008, 20250000000000004, 'en-US', 'Disabled', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000009, 20250000000000005, 'zh-CN', '子标题', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000010, 20250000000000005, 'en-US', 'Subheader', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000011, 20250000000000006, 'zh-CN', '组', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000012, 20250000000000006, 'en-US', 'Group', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000013, 20250000000000007, 'zh-CN', '模版', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000014, 20250000000000007, 'en-US', 'Template', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000015, 20250000000000008, 'zh-CN', '链接', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000016, 20250000000000008, 'en-US', 'Link', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000017, 20250000000000009, 'zh-CN', '按钮', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000018, 20250000000000009, 'en-US', 'Button', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000019, 20250000000000010, 'zh-CN', '功能', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000020, 20250000000000010, 'en-US', 'Function', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000021, 20250000000000011, 'zh-CN', '_blank', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000022, 20250000000000011, 'en-US', '_blank', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000023, 20250000000000012, 'zh-CN', '_self', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000024, 20250000000000012, 'en-US', '_self', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000025, 20250000000000013, 'zh-CN', '启用', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000026, 20250000000000013, 'en-US', 'Enabled', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000027, 20250000000000014, 'zh-CN', '禁用', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000028, 20250000000000014, 'en-US', 'Disabled', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000029, 20250000000000015, 'zh-CN', 'B', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000030, 20250000000000015, 'en-US', 'B', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000031, 20250000000000016, 'zh-CN', 'KB', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000032, 20250000000000016, 'en-US', 'KB', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000033, 20250000000000017, 'zh-CN', 'MB', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000034, 20250000000000017, 'en-US', 'MB', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000035, 20250000000000018, 'zh-CN', 'GB', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000036, 20250000000000018, 'en-US', 'GB', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000037, 20250000000000019, 'zh-CN', '启用', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000038, 20250000000000019, 'en-US', 'Enabled', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000039, 20250000000000020, 'zh-CN', '禁用', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000040, 20250000000000020, 'en-US', 'Disabled', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000041, 20250000000000021, 'zh-CN', '启用', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000042, 20250000000000021, 'en-US', 'Enabled', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000043, 20250000000000022, 'zh-CN', '禁用', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000044, 20250000000000022, 'en-US', 'Disabled', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000045, 20250000000000023, 'zh-CN', '默认', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000046, 20250000000000023, 'en-US', 'Default', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000047, 20250000000000024, 'zh-CN', '系统', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000048, 20250000000000024, 'en-US', 'System', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000049, 20250000000000025, 'zh-CN', '默认', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000050, 20250000000000025, 'en-US', 'Default', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000051, 20250000000000026, 'zh-CN', '忽略失败', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000052, 20250000000000026, 'en-US', 'Ignore Misfires', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000053, 20250000000000027, 'zh-CN', '触发并继续', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000054, 20250000000000027, 'en-US', 'Fire and Proceed', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000055, 20250000000000028, 'zh-CN', '不做任何处理', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000056, 20250000000000028, 'en-US', 'Do Nothing', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000057, 20250000000000029, 'zh-CN', '启用', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000058, 20250000000000029, 'en-US', 'Enabled', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000059, 20250000000000030, 'zh-CN', '禁用', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000060, 20250000000000030, 'en-US', 'Disabled', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000061, 20250000000000031, 'zh-CN', '启用', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000062, 20250000000000031, 'en-US', 'Enabled', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000063, 20250000000000032, 'zh-CN', '禁用', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000064, 20250000000000032, 'en-US', 'Disabled', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000065, 20250000000000033, 'zh-CN', '启用', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000066, 20250000000000033, 'en-US', 'Enabled', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000067, 20250000000000034, 'zh-CN', '禁用', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000068, 20250000000000034, 'en-US', 'Disabled', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000069, 20250000000000035, 'zh-CN', '男', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000070, 20250000000000035, 'en-US', 'Male', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000071, 20250000000000036, 'zh-CN', '女', NULL);
INSERT INTO `system_dictionary_data_translation`
VALUES (20250000000000072, 20250000000000036, 'en-US', 'Female', NULL);

-- ----------------------------
-- Table structure for system_dictionary_type
-- ----------------------------
DROP TABLE IF EXISTS `system_dictionary_type`;
CREATE TABLE `system_dictionary_type`
(
    `id`                     bigint                                                       NOT NULL COMMENT '主键ID',
    `dictionary_type_code`   varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '字典类型代码',
    `sort`                   int                                                          NOT NULL COMMENT '显示顺序（1-999）',
    `dictionary_type_status` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '字典类型状态（ENABLED:正常 DISABLED:停用）',
    `created_time`           timestamp                                                    NOT NULL COMMENT '创建时间',
    `created_by`             bigint NULL DEFAULT NULL COMMENT '创建人ID',
    `last_modified_time`     timestamp                                                    NOT NULL COMMENT '最后修改时间',
    `last_modified_by`       bigint NULL DEFAULT NULL COMMENT '最后修改人ID',
    PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '系统字典类型表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of system_dictionary_type
-- ----------------------------
INSERT INTO `system_dictionary_type`
VALUES (20250000000000001, 'system_language_code', 1, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00',
        NULL);
INSERT INTO `system_dictionary_type`
VALUES (20250000000000002, 'system_role_status', 2, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00',
        NULL);
INSERT INTO `system_dictionary_type`
VALUES (20250000000000003, 'system_permission_type', 3, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00',
        NULL);
INSERT INTO `system_dictionary_type`
VALUES (20250000000000004, 'system_permission_link_target', 4, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_type`
VALUES (20250000000000005, 'system_permission_status', 5, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00',
        NULL);
INSERT INTO `system_dictionary_type`
VALUES (20250000000000006, 'system_file_type_size_unit', 6, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_type`
VALUES (20250000000000007, 'system_file_type_status', 7, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00',
        NULL);
INSERT INTO `system_dictionary_type`
VALUES (20250000000000008, 'system_file_metadata_status', 8, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_type`
VALUES (20250000000000009, 'system_scheduled_task_group', 9, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_type`
VALUES (20250000000000010, 'system_scheduled_misfire_policy', 10, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_type`
VALUES (20250000000000011, 'system_scheduled_task_status', 11, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_type`
VALUES (20250000000000012, 'system_dictionary_type_status', 12, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_type`
VALUES (20250000000000013, 'system_dictionary_data_status', 13, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_dictionary_type`
VALUES (20250000000000014, 'system_user_gender', 14, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00',
        NULL);

-- ----------------------------
-- Table structure for system_dictionary_type_translation
-- ----------------------------
DROP TABLE IF EXISTS `system_dictionary_type_translation`;
CREATE TABLE `system_dictionary_type_translation`
(
    `id`                   bigint                                                       NOT NULL COMMENT '主键ID',
    `dictionary_type_id`   bigint                                                       NOT NULL COMMENT '字典类型ID',
    `language_code`        varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '语言代码（zh-CN:简体中文 en-US:英文）',
    `dictionary_type_name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '字典类型名称',
    `remark`               varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '备注信息',
    PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '系统字典类型翻译表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of system_dictionary_type_translation
-- ----------------------------
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000001, 20250000000000001, 'zh-CN', '系统语言代码',
        '用于定义系统支持的多语言语言代码，如 zh-CN、en-US。');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000002, 20250000000000001, 'en-US', 'System Language Code',
        'Defines language codes supported by the system, such as zh-CN, en-US.');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000003, 20250000000000002, 'zh-CN', '系统角色状态', '用于表示系统中角色的当前启用或禁用状态。');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000004, 20250000000000002, 'en-US', 'System Role Status',
        'Indicates the current enabled or disabled status of roles in the system.');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000005, 20250000000000003, 'zh-CN', '系统权限类型',
        '用于定义权限的类型，如菜单、按钮等，用于权限控制。');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000006, 20250000000000003, 'en-US', 'System Permission Type',
        'Defines types of permissions, such as menu or button, for access control.');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000007, 20250000000000004, 'zh-CN', '系统权限链接目标',
        '用于指定权限链接的跳转方式，例如当前页面或新窗口。');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000008, 20250000000000004, 'en-US', 'System Permission Link Target',
        'Specifies how permission links are opened, such as the current page or a new window.');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000009, 20250000000000005, 'zh-CN', '系统权限状态', '用于表示系统中权限的当前启用或禁用状态。');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000010, 20250000000000005, 'en-US', 'System Permission Status',
        'Indicates the current enabled or disabled status of permissions in the system.');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000011, 20250000000000006, 'zh-CN', '系统文件大小单位', '用于描述文件大小的单位，如 B、KB、MB、GB。');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000012, 20250000000000006, 'en-US', 'System File Type Size Unit',
        'Describes file size units, such as B, KB, MB, or GB.');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000013, 20250000000000007, 'zh-CN', '系统文件类型状态',
        '用于表示系统中文件类型的当前启用或禁用状态。');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000014, 20250000000000007, 'en-US', 'System File Type Status',
        'Indicates the current enabled or disabled status of file types in the system.');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000015, 20250000000000008, 'zh-CN', '系统文件元数据状态',
        '用于表示系统中文件元数据的当前启用或禁用状态。');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000016, 20250000000000008, 'en-US', 'System File Metadata Status',
        'Indicates the current enabled or disabled status of file metadata records in the system.');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000017, 20250000000000009, 'zh-CN', '系统定时任务组', '用于对定时任务进行分组管理，便于分类和调度。');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000018, 20250000000000009, 'en-US', 'System Scheduled Task Group',
        'Used to group scheduled tasks for easier categorization and scheduling.');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000019, 20250000000000010, 'zh-CN', '系统定时任务失败策略',
        '定义定时任务错过触发时的补偿策略，如立即执行、忽略。');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000020, 20250000000000010, 'en-US', 'System Scheduled Misfire Policy',
        'Defines how to handle misfired tasks, such as executing immediately or ignoring them.');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000021, 20250000000000011, 'zh-CN', '系统定时任务状态', '标识定时任务当前的运行状态，如正常、暂停。');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000022, 20250000000000011, 'en-US', 'System Scheduled Task Status',
        'Represents the current state of a scheduled task, such as normal or paused.');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000023, 20250000000000012, 'zh-CN', '系统字典类型状态',
        '用于表示系统中字典类型的当前启用或禁用状态。');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000024, 20250000000000012, 'en-US', 'System Dictionary Type Status',
        'Indicates the current enabled or disabled status of dictionary types in the system.');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000025, 20250000000000013, 'zh-CN', '系统字典数据状态',
        '用于表示系统中字典数据的当前启用或禁用状态。');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000026, 20250000000000013, 'en-US', 'System Dictionary Data Status',
        'Indicates the current enabled or disabled status of dictionary data records in the system.');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000027, 20250000000000014, 'zh-CN', '系统用户性别', '定义系统中用户的性别分类，如男、女。');
INSERT INTO `system_dictionary_type_translation`
VALUES (20250000000000028, 20250000000000014, 'en-US', 'System User Gender',
        'Defines gender classifications for users in the system, such as male, female.');

-- ----------------------------
-- Table structure for system_operate_log
-- ----------------------------
DROP TABLE IF EXISTS `system_operate_log`;
CREATE TABLE `system_operate_log`
(
    `id`                bigint                                                        NOT NULL COMMENT '主键ID',
    `title`             varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NOT NULL COMMENT '操作标题',
    `operate_type`      varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NOT NULL COMMENT '操作类型（INSERT:新增 DELETE:删除 UPDATE:更新 EXPORT:导出 IMPORT:导入 CLEAN:清空 TOGGLE_STATUS:切换状态 EXECUTE:执行）',
    `execute_method`    varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '执行方法',
    `request_method`    varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NOT NULL COMMENT '请求方法',
    `request_url`       varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '请求URL',
    `operate_ip`        varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '操作IP地址',
    `operate_location`  varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '操作地理位置',
    `request_param`     text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '请求参数',
    `response_result`   text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '响应结果',
    `error_message`     text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '错误信息',
    `response_duration` bigint                                                        NOT NULL COMMENT '响应时长（毫秒）',
    `operate_status`    varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '操作状态（FAILED:失败 SUCCESS:成功）',
    `operate_by`        bigint NULL DEFAULT NULL COMMENT '操作人ID',
    `operate_time`      timestamp                                                     NOT NULL COMMENT '操作时间',
    PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '系统操作日志表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of system_operate_log
-- ----------------------------

-- ----------------------------
-- Table structure for system_permission
-- ----------------------------
DROP TABLE IF EXISTS `system_permission`;
CREATE TABLE `system_permission`
(
    `id`                 bigint                                                        NOT NULL COMMENT '主键ID',
    `parent_id`          bigint                                                        NOT NULL COMMENT '父级ID',
    `authority`          varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '权限标识',
    `sort`               int                                                           NOT NULL COMMENT '显示顺序（1-99）',
    `permission_type`    varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NOT NULL COMMENT '权限类型（SUBHEADER:子标题 GROUP:分组 TEMPLATE:组件 LINK:链接 BUTTON:按钮 FUNCTION:功能）',
    `icon`               varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '图标',
    `link_address`       varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '链接地址',
    `link_target`        varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '链接打开方式（_self _blank）',
    `router_path`        varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '路由路径',
    `component_path`     varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '组件路径',
    `keep_alive`         tinyint NULL DEFAULT NULL COMMENT '是否缓存（1:是 0:否）',
    `visible`            tinyint                                                       NOT NULL COMMENT '是否可见（1:是 0:否）',
    `permission_status`  varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci  NOT NULL COMMENT '权限状态（DISABLED:停用 ENABLED:正常）',
    `created_time`       timestamp                                                     NOT NULL COMMENT '创建时间',
    `created_by`         bigint NULL DEFAULT NULL COMMENT '创建人ID',
    `last_modified_time` timestamp                                                     NOT NULL COMMENT '最后修改时间',
    `last_modified_by`   bigint NULL DEFAULT NULL COMMENT '最后修改人ID',
    PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '系统权限表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of system_permission
-- ----------------------------
INSERT INTO `system_permission`
VALUES (20250001000000001, 0, 'subheader:dashboard', 1, 'SUBHEADER', 'icon-layout-dashboard', NULL, NULL, NULL, NULL,
        NULL, 1, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250002000000001, 20250001000000001, 'dashboard:analytical', 1, 'TEMPLATE', 'icon-chart-pie', NULL, NULL,
        '/dashboard/analytical', '/dashboard/analytical/index.vue', 0, 1, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250002000000002, 20250001000000001, 'dashboard:ecommerce', 2, 'TEMPLATE', 'icon-shopping-cart', NULL, NULL,
        '/dashboard/ecommerce', '/dashboard/ecommerce/index.vue', 0, 1, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250002000000003, 20250001000000001, 'dashboard:modern', 3, 'TEMPLATE', 'icon-aperture', NULL, NULL,
        '/dashboard/modern', '/dashboard/modern/index.vue', 0, 1, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250101000000001, 0, 'subheader:system', 2, 'SUBHEADER', 'icon-settings', NULL, NULL, NULL, NULL, NULL, 1,
        'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250101000000002, 20250101000000001, 'system', 1, 'GROUP', 'icon-settings-cog', NULL, NULL, NULL, NULL, NULL,
        1, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250102000000001, 20250101000000002, 'system:user', 1, 'TEMPLATE', 'icon-users', NULL, NULL, '/system/user',
        '/system/user/index.vue', 0, 1, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250102000000002, 20250101000000002, 'system:role', 2, 'TEMPLATE', 'icon-user-square-rounded', NULL, NULL,
        '/system/role', '/system/role/index.vue', 0, 1, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00',
        NULL);
INSERT INTO `system_permission`
VALUES (20250102000000003, 20250101000000002, 'system:permission', 3, 'TEMPLATE', 'icon-list-details', NULL, NULL,
        '/system/permission', '/system/permission/index.vue', 0, 1, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250102000000004, 20250101000000002, 'system:file', 4, 'FUNCTION', NULL, NULL, NULL, NULL, NULL, NULL, 0,
        'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250102000000005, 20250101000000002, 'system:file-type', 5, 'TEMPLATE', 'icon-file-typography', NULL, NULL,
        '/system/file-type', '/system/file-type/index.vue', 0, 1, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250102000000006, 20250101000000002, 'system:file-metadata', 6, 'TEMPLATE', 'icon-file-database', NULL, NULL,
        '/system/file-metadata', '/system/file-metadata/index.vue', 0, 1, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250102000000007, 20250101000000002, 'system:task', 7, 'TEMPLATE', 'icon-calendar-time', NULL, NULL,
        '/system/task', '/system/task/index.vue', 0, 1, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00',
        NULL);
INSERT INTO `system_permission`
VALUES (20250102000000008, 20250101000000002, 'system:dictionary-type', 8, 'TEMPLATE', 'icon-book-2', NULL, NULL,
        '/system/dictionary-type', '/system/dictionary-type/index.vue', 0, 1, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250102000000009, 20250101000000002, 'system:dictionary-data', 9, 'TEMPLATE', 'icon-vocabulary', NULL, NULL,
        '/system/dictionary-data', '/system/dictionary-data/index.vue', 0, 1, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103010000001, 20250102000000001, 'system:user:create', 1, 'BUTTON', 'icon-system-user-create', NULL, NULL,
        NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103010000002, 20250102000000001, 'system:user:delete', 2, 'BUTTON', 'icon-system-user-delete', NULL, NULL,
        NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103010000003, 20250102000000001, 'system:user:update', 3, 'BUTTON', 'icon-system-user-update', NULL, NULL,
        NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103010000004, 20250102000000001, 'system:user:details', 4, 'FUNCTION', NULL, NULL, NULL, NULL, NULL, NULL,
        0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103010000005, 20250102000000001, 'system:user:validate-username', 5, 'FUNCTION', NULL, NULL, NULL, NULL,
        NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103010000006, 20250102000000001, 'system:user:page', 6, 'FUNCTION', NULL, NULL, NULL, NULL, NULL, NULL, 0,
        'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103010000007, 20250102000000001, 'system:user:export', 7, 'BUTTON', 'icon-system-user-export', NULL, NULL,
        NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103010000008, 20250102000000001, 'system:user:template', 8, 'BUTTON', 'icon-system-user-template', NULL,
        NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103010000009, 20250102000000001, 'system:user:import', 9, 'BUTTON', 'icon-system-user-import', NULL, NULL,
        NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103020000001, 20250102000000002, 'system:role:create', 1, 'BUTTON', 'icon-system-role-create', NULL, NULL,
        NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103020000002, 20250102000000002, 'system:role:delete', 2, 'BUTTON', 'icon-system-role-delete', NULL, NULL,
        NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103020000003, 20250102000000002, 'system:role:update', 3, 'BUTTON', 'icon-system-role-update', NULL, NULL,
        NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103020000004, 20250102000000002, 'system:role:details', 4, 'FUNCTION', NULL, NULL, NULL, NULL, NULL, NULL,
        0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103020000005, 20250102000000002, 'system:role:validate-role-name', 5, 'FUNCTION', NULL, NULL, NULL, NULL,
        NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103020000006, 20250102000000002, 'system:role:validate-role-code', 6, 'FUNCTION', NULL, NULL, NULL, NULL,
        NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103020000007, 20250102000000002, 'system:role:page', 7, 'FUNCTION', NULL, NULL, NULL, NULL, NULL, NULL, 0,
        'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103020000008, 20250102000000002, 'system:role:list', 8, 'FUNCTION', NULL, NULL, NULL, NULL, NULL, NULL, 0,
        'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103030000001, 20250102000000003, 'system:permission:create', 1, 'BUTTON', 'icon-system-permission-create',
        NULL, NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103030000002, 20250102000000003, 'system:permission:delete', 2, 'BUTTON', 'icon-system-permission-delete',
        NULL, NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103030000003, 20250102000000003, 'system:permission:update', 3, 'BUTTON', 'icon-system-permission-update',
        NULL, NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103030000004, 20250102000000003, 'system:permission:details', 4, 'FUNCTION', NULL, NULL, NULL, NULL, NULL,
        NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103030000005, 20250102000000003, 'system:permission:validate-permission-name', 5, 'FUNCTION', NULL, NULL,
        NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103030000006, 20250102000000003, 'system:permission:validate-authority', 6, 'FUNCTION', NULL, NULL, NULL,
        NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103030000007, 20250102000000003, 'system:permission:tree', 7, 'FUNCTION', NULL, NULL, NULL, NULL, NULL,
        NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103040000001, 20250102000000004, 'system:file:upload', 1, 'FUNCTION', NULL, NULL, NULL, NULL, NULL, NULL,
        0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103050000001, 20250102000000005, 'system:file-type:create', 1, 'BUTTON', 'icon-system-file-type-create',
        NULL, NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103050000002, 20250102000000005, 'system:file-type:delete', 2, 'BUTTON', 'icon-system-file-type-delete',
        NULL, NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103050000003, 20250102000000005, 'system:file-type:update', 3, 'BUTTON', 'icon-system-file-type-update',
        NULL, NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103050000004, 20250102000000005, 'system:file-type:details', 4, 'FUNCTION', NULL, NULL, NULL, NULL, NULL,
        NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103050000005, 20250102000000005, 'system:file-type:validate-file-type-name', 5, 'FUNCTION', NULL, NULL,
        NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103050000006, 20250102000000005, 'system:file-type:page', 6, 'FUNCTION', NULL, NULL, NULL, NULL, NULL,
        NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103050000007, 20250102000000005, 'system:file-type:list', 7, 'FUNCTION', NULL, NULL, NULL, NULL, NULL,
        NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103060000001, 20250102000000006, 'system:file-metadata:create', 1, 'BUTTON',
        'icon-system-file-metadata-create', NULL, NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103060000002, 20250102000000006, 'system:file-metadata:delete', 2, 'BUTTON',
        'icon-system-file-metadata-delete', NULL, NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103060000003, 20250102000000006, 'system:file-metadata:update', 3, 'BUTTON',
        'icon-system-file-metadata-update', NULL, NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103060000004, 20250102000000006, 'system:file-metadata:details', 4, 'FUNCTION', NULL, NULL, NULL, NULL,
        NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103060000005, 20250102000000006, 'system:file-metadata:validate-mime-type', 5, 'FUNCTION', NULL, NULL,
        NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103060000006, 20250102000000006, 'system:file-metadata:validate-extension', 6, 'FUNCTION', NULL, NULL,
        NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103060000007, 20250102000000006, 'system:file-metadata:page', 7, 'FUNCTION', NULL, NULL, NULL, NULL, NULL,
        NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103070000001, 20250102000000007, 'system:task:create', 1, 'BUTTON', 'icon-system-task-create', NULL, NULL,
        NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103070000002, 20250102000000007, 'system:task:delete', 2, 'BUTTON', 'icon-system-task-delete', NULL, NULL,
        NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103070000003, 20250102000000007, 'system:task:update', 3, 'BUTTON', 'icon-system-task-update', NULL, NULL,
        NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103070000004, 20250102000000007, 'system:task:details', 4, 'FUNCTION', NULL, NULL, NULL, NULL, NULL, NULL,
        0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103070000005, 20250102000000007, 'system:task:validate-task-name', 5, 'FUNCTION', NULL, NULL, NULL, NULL,
        NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103070000006, 20250102000000007, 'system:task:page', 6, 'FUNCTION', NULL, NULL, NULL, NULL, NULL, NULL, 0,
        'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103070000007, 20250102000000007, 'system:task:toggle-status', 7, 'BUTTON', 'icon-system-task-toggle', NULL,
        NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103070000008, 20250102000000007, 'system:task:execute', 8, 'BUTTON', 'icon-system-task-execute', NULL,
        NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103080000001, 20250102000000008, 'system:dictionary-type:create', 1, 'BUTTON',
        'icon-system-dictionary-type-create', NULL, NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103080000002, 20250102000000008, 'system:dictionary-type:delete', 2, 'BUTTON',
        'icon-system-dictionary-type-delete', NULL, NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103080000003, 20250102000000008, 'system:dictionary-type:update', 3, 'BUTTON',
        'icon-system-dictionary-type-update', NULL, NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103080000004, 20250102000000008, 'system:dictionary-type:details', 4, 'FUNCTION', NULL, NULL, NULL, NULL,
        NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103080000005, 20250102000000008, 'system:dictionary-type:validate-dictionary-type-name', 5, 'FUNCTION',
        NULL, NULL, NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103080000006, 20250102000000008, 'system:dictionary-type:validate-dictionary-type-code', 6, 'FUNCTION',
        NULL, NULL, NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103080000007, 20250102000000008, 'system:dictionary-type:page', 6, 'FUNCTION', NULL, NULL, NULL, NULL,
        NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103080000008, 20250102000000008, 'system:dictionary-type:list', 7, 'FUNCTION', NULL, NULL, NULL, NULL,
        NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103090000001, 20250102000000009, 'system:dictionary-data:create', 1, 'BUTTON',
        'icon-system-dictionary-data-create', NULL, NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103090000002, 20250102000000009, 'system:dictionary-data:delete', 2, 'BUTTON',
        'icon-system-dictionary-data-delete', NULL, NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103090000003, 20250102000000009, 'system:dictionary-data:update', 3, 'BUTTON',
        'icon-system-dictionary-data-update', NULL, NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103090000004, 20250102000000009, 'system:dictionary-data:details', 4, 'FUNCTION', NULL, NULL, NULL, NULL,
        NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103090000005, 20250102000000009, 'system:dictionary-data:validate-label', 5, 'FUNCTION', NULL, NULL, NULL,
        NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103090000006, 20250102000000009, 'system:dictionary-data:validate-value', 6, 'FUNCTION', NULL, NULL, NULL,
        NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103090000007, 20250102000000009, 'system:dictionary-data:page', 6, 'FUNCTION', NULL, NULL, NULL, NULL,
        NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250103090000008, 20250102000000009, 'system:dictionary-data:list', 7, 'FUNCTION', NULL, NULL, NULL, NULL,
        NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250201000000001, 0, 'business', 3, 'FUNCTION', NULL, NULL, NULL, NULL, NULL, NULL, 0, 'ENABLED',
        '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250202000000001, 20250201000000001, 'business:personal', 1, 'TEMPLATE', 'icon-business-personal', NULL, NULL,
        '/business/personal', '/business/personal/index.vue', 0, 0, 'ENABLED', '2025-01-01 00:00:00', NULL,
        '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250202000000002, 20250201000000001, 'business:file', 2, 'FUNCTION', NULL, NULL, NULL, NULL, NULL, NULL, 0,
        'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250203010000001, 20250202000000001, 'business:personal:me', 1, 'FUNCTION', NULL, NULL, NULL, NULL, NULL, NULL,
        0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250203010000002, 20250202000000001, 'business:personal:change-password', 2, 'BUTTON',
        'icon-business-personal-change-password', NULL, NULL, NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00',
        NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250203010000003, 20250202000000001, 'business:personal:validate-username', 3, 'FUNCTION', NULL, NULL, NULL,
        NULL, NULL, NULL, 0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_permission`
VALUES (20250203020000001, 20250202000000002, 'business:file:upload', 1, 'FUNCTION', NULL, NULL, NULL, NULL, NULL, NULL,
        0, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);

-- ----------------------------
-- Table structure for system_permission_translation
-- ----------------------------
DROP TABLE IF EXISTS `system_permission_translation`;
CREATE TABLE `system_permission_translation`
(
    `id`              bigint                                                       NOT NULL COMMENT '主键ID',
    `permission_id`   bigint                                                       NOT NULL COMMENT '权限ID',
    `language_code`   varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '语言代码（zh-CN:简体中文 en-US:英文）',
    `permission_name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '权限名称',
    PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '系统权限翻译表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of system_permission_translation
-- ----------------------------
INSERT INTO `system_permission_translation`
VALUES (20250000000000001, 20250001000000001, 'zh-CN', '仪表盘');
INSERT INTO `system_permission_translation`
VALUES (20250000000000002, 20250001000000001, 'en-US', 'Dashboard');
INSERT INTO `system_permission_translation`
VALUES (20250000000000003, 20250002000000001, 'zh-CN', '分析仪表盘');
INSERT INTO `system_permission_translation`
VALUES (20250000000000004, 20250002000000001, 'en-US', 'Analytical');
INSERT INTO `system_permission_translation`
VALUES (20250000000000005, 20250002000000002, 'zh-CN', '电子商务仪表盘');
INSERT INTO `system_permission_translation`
VALUES (20250000000000006, 20250002000000002, 'en-US', 'eCommerce');
INSERT INTO `system_permission_translation`
VALUES (20250000000000007, 20250002000000003, 'zh-CN', '现代版仪表盘');
INSERT INTO `system_permission_translation`
VALUES (20250000000000008, 20250002000000003, 'en-US', 'Modern');
INSERT INTO `system_permission_translation`
VALUES (20250000000000009, 20250101000000001, 'zh-CN', '系统');
INSERT INTO `system_permission_translation`
VALUES (20250000000000010, 20250101000000001, 'en-US', 'System');
INSERT INTO `system_permission_translation`
VALUES (20250000000000011, 20250101000000002, 'zh-CN', '系统管理');
INSERT INTO `system_permission_translation`
VALUES (20250000000000012, 20250101000000002, 'en-US', 'System Management');
INSERT INTO `system_permission_translation`
VALUES (20250000000000013, 20250102000000001, 'zh-CN', '用户管理');
INSERT INTO `system_permission_translation`
VALUES (20250000000000014, 20250102000000001, 'en-US', 'User Management');
INSERT INTO `system_permission_translation`
VALUES (20250000000000015, 20250102000000002, 'zh-CN', '角色管理');
INSERT INTO `system_permission_translation`
VALUES (20250000000000016, 20250102000000002, 'en-US', 'Role Management');
INSERT INTO `system_permission_translation`
VALUES (20250000000000017, 20250102000000003, 'zh-CN', '权限管理');
INSERT INTO `system_permission_translation`
VALUES (20250000000000018, 20250102000000003, 'en-US', 'Permission Management');
INSERT INTO `system_permission_translation`
VALUES (20250000000000019, 20250102000000004, 'zh-CN', '系统文件管理');
INSERT INTO `system_permission_translation`
VALUES (20250000000000020, 20250102000000004, 'en-US', 'System File Management');
INSERT INTO `system_permission_translation`
VALUES (20250000000000021, 20250102000000005, 'zh-CN', '文件类型管理');
INSERT INTO `system_permission_translation`
VALUES (20250000000000022, 20250102000000005, 'en-US', 'File Type Management');
INSERT INTO `system_permission_translation`
VALUES (20250000000000023, 20250102000000006, 'zh-CN', '文件元数据管理');
INSERT INTO `system_permission_translation`
VALUES (20250000000000024, 20250102000000006, 'en-US', 'File Metadata Management');
INSERT INTO `system_permission_translation`
VALUES (20250000000000025, 20250102000000007, 'zh-CN', '定时任务管理');
INSERT INTO `system_permission_translation`
VALUES (20250000000000026, 20250102000000007, 'en-US', 'Scheduled Task Management');
INSERT INTO `system_permission_translation`
VALUES (20250000000000027, 20250102000000008, 'zh-CN', '字典类型管理');
INSERT INTO `system_permission_translation`
VALUES (20250000000000028, 20250102000000008, 'en-US', 'Dictionary Type Management');
INSERT INTO `system_permission_translation`
VALUES (20250000000000029, 20250102000000009, 'zh-CN', '字典数据管理');
INSERT INTO `system_permission_translation`
VALUES (20250000000000030, 20250102000000009, 'en-US', 'Dictionary Data Management');
INSERT INTO `system_permission_translation`
VALUES (20250000000000031, 20250103010000001, 'zh-CN', '创建用户');
INSERT INTO `system_permission_translation`
VALUES (20250000000000032, 20250103010000001, 'en-US', 'Create User');
INSERT INTO `system_permission_translation`
VALUES (20250000000000033, 20250103010000002, 'zh-CN', '删除用户');
INSERT INTO `system_permission_translation`
VALUES (20250000000000034, 20250103010000002, 'en-US', 'Delete User');
INSERT INTO `system_permission_translation`
VALUES (20250000000000035, 20250103010000003, 'zh-CN', '更新用户');
INSERT INTO `system_permission_translation`
VALUES (20250000000000036, 20250103010000003, 'en-US', 'Update User');
INSERT INTO `system_permission_translation`
VALUES (20250000000000037, 20250103010000004, 'zh-CN', '查看用户详情');
INSERT INTO `system_permission_translation`
VALUES (20250000000000038, 20250103010000004, 'en-US', 'View User Details');
INSERT INTO `system_permission_translation`
VALUES (20250000000000039, 20250103010000005, 'zh-CN', '系统验证用户名唯一性');
INSERT INTO `system_permission_translation`
VALUES (20250000000000040, 20250103010000005, 'en-US', 'System Verify Username Uniqueness');
INSERT INTO `system_permission_translation`
VALUES (20250000000000041, 20250103010000006, 'zh-CN', '用户分页查询');
INSERT INTO `system_permission_translation`
VALUES (20250000000000042, 20250103010000006, 'en-US', 'Paginated User Query');
INSERT INTO `system_permission_translation`
VALUES (20250000000000043, 20250103010000007, 'zh-CN', '导出用户数据');
INSERT INTO `system_permission_translation`
VALUES (20250000000000044, 20250103010000007, 'en-US', 'Export User Data');
INSERT INTO `system_permission_translation`
VALUES (20250000000000045, 20250103010000008, 'zh-CN', '导出用户模板');
INSERT INTO `system_permission_translation`
VALUES (20250000000000046, 20250103010000008, 'en-US', 'Export User Template');
INSERT INTO `system_permission_translation`
VALUES (20250000000000047, 20250103010000009, 'zh-CN', '导入用户');
INSERT INTO `system_permission_translation`
VALUES (20250000000000048, 20250103010000009, 'en-US', 'Import User');
INSERT INTO `system_permission_translation`
VALUES (20250000000000049, 20250103020000001, 'zh-CN', '创建角色');
INSERT INTO `system_permission_translation`
VALUES (20250000000000050, 20250103020000001, 'en-US', 'Create Role');
INSERT INTO `system_permission_translation`
VALUES (20250000000000051, 20250103020000002, 'zh-CN', '删除角色');
INSERT INTO `system_permission_translation`
VALUES (20250000000000052, 20250103020000002, 'en-US', 'Delete Role');
INSERT INTO `system_permission_translation`
VALUES (20250000000000053, 20250103020000003, 'zh-CN', '更新角色');
INSERT INTO `system_permission_translation`
VALUES (20250000000000054, 20250103020000003, 'en-US', 'Update Role');
INSERT INTO `system_permission_translation`
VALUES (20250000000000055, 20250103020000004, 'zh-CN', '查看角色详情');
INSERT INTO `system_permission_translation`
VALUES (20250000000000056, 20250103020000004, 'en-US', 'View Role Details');
INSERT INTO `system_permission_translation`
VALUES (20250000000000057, 20250103020000005, 'zh-CN', '验证角色名称唯一性');
INSERT INTO `system_permission_translation`
VALUES (20250000000000058, 20250103020000005, 'en-US', 'Verify Role Name Uniqueness');
INSERT INTO `system_permission_translation`
VALUES (20250000000000059, 20250103020000006, 'zh-CN', '验证代码名称唯一性');
INSERT INTO `system_permission_translation`
VALUES (20250000000000060, 20250103020000006, 'en-US', 'Verify Role Code Uniqueness');
INSERT INTO `system_permission_translation`
VALUES (20250000000000061, 20250103020000007, 'zh-CN', '角色分页查询');
INSERT INTO `system_permission_translation`
VALUES (20250000000000062, 20250103020000007, 'en-US', 'Paginated Role Query');
INSERT INTO `system_permission_translation`
VALUES (20250000000000063, 20250103020000008, 'zh-CN', '角色列表');
INSERT INTO `system_permission_translation`
VALUES (20250000000000064, 20250103020000000, 'en-US', 'List Roles');
INSERT INTO `system_permission_translation`
VALUES (20250000000000065, 20250103030000001, 'zh-CN', '创建权限');
INSERT INTO `system_permission_translation`
VALUES (20250000000000066, 20250103030000001, 'en-US', 'Create Permission');
INSERT INTO `system_permission_translation`
VALUES (20250000000000067, 20250103030000002, 'zh-CN', '删除权限');
INSERT INTO `system_permission_translation`
VALUES (20250000000000068, 20250103030000002, 'en-US', 'Delete Permission');
INSERT INTO `system_permission_translation`
VALUES (20250000000000069, 20250103030000003, 'zh-CN', '更新权限');
INSERT INTO `system_permission_translation`
VALUES (20250000000000070, 20250103030000003, 'en-US', 'Update Permission');
INSERT INTO `system_permission_translation`
VALUES (20250000000000071, 20250103030000004, 'zh-CN', '查看权限详情');
INSERT INTO `system_permission_translation`
VALUES (20250000000000072, 20250103030000004, 'en-US', 'View Permission Details');
INSERT INTO `system_permission_translation`
VALUES (20250000000000073, 20250103030000005, 'zh-CN', '验证权限名称唯一性');
INSERT INTO `system_permission_translation`
VALUES (20250000000000074, 20250103030000005, 'en-US', 'Verify Permission Name Uniqueness');
INSERT INTO `system_permission_translation`
VALUES (20250000000000075, 20250103030000006, 'zh-CN', '验证权限标识唯一性');
INSERT INTO `system_permission_translation`
VALUES (20250000000000076, 20250103030000006, 'en-US', 'Verify Permission Authority Uniqueness');
INSERT INTO `system_permission_translation`
VALUES (20250000000000077, 20250103030000007, 'zh-CN', '查询权限树');
INSERT INTO `system_permission_translation`
VALUES (20250000000000078, 20250103030000007, 'en-US', 'Query Permission Tree');
INSERT INTO `system_permission_translation`
VALUES (20250000000000079, 20250103040000001, 'zh-CN', '系统上传文件');
INSERT INTO `system_permission_translation`
VALUES (20250000000000080, 20250103040000001, 'en-US', 'System Upload File');
INSERT INTO `system_permission_translation`
VALUES (20250000000000081, 20250103050000001, 'zh-CN', '创建文件类型');
INSERT INTO `system_permission_translation`
VALUES (20250000000000082, 20250103050000001, 'en-US', 'Create File Type');
INSERT INTO `system_permission_translation`
VALUES (20250000000000083, 20250103050000002, 'zh-CN', '删除文件类型');
INSERT INTO `system_permission_translation`
VALUES (20250000000000084, 20250103050000002, 'en-US', 'Delete File Type');
INSERT INTO `system_permission_translation`
VALUES (20250000000000085, 20250103050000003, 'zh-CN', '更新文件类型');
INSERT INTO `system_permission_translation`
VALUES (20250000000000086, 20250103050000003, 'en-US', 'Update File Type');
INSERT INTO `system_permission_translation`
VALUES (20250000000000087, 20250103050000004, 'zh-CN', '查看文件类型详情');
INSERT INTO `system_permission_translation`
VALUES (20250000000000088, 20250103050000004, 'en-US', 'View File Type Details');
INSERT INTO `system_permission_translation`
VALUES (20250000000000089, 20250103050000005, 'zh-CN', '验证文件类型名称唯一性');
INSERT INTO `system_permission_translation`
VALUES (20250000000000090, 20250103050000005, 'en-US', 'Verify File Type Name Uniqueness');
INSERT INTO `system_permission_translation`
VALUES (20250000000000091, 20250103050000006, 'zh-CN', '文件类型分页查询');
INSERT INTO `system_permission_translation`
VALUES (20250000000000092, 20250103050000006, 'en-US', 'Paginated File Type Query');
INSERT INTO `system_permission_translation`
VALUES (20250000000000093, 20250103050000007, 'zh-CN', '文件类型列表');
INSERT INTO `system_permission_translation`
VALUES (20250000000000094, 20250103050000007, 'en-US', 'List File Types');
INSERT INTO `system_permission_translation`
VALUES (20250000000000095, 20250103060000001, 'zh-CN', '创建文件元数据');
INSERT INTO `system_permission_translation`
VALUES (20250000000000096, 20250103060000001, 'en-US', 'Create File Metadata');
INSERT INTO `system_permission_translation`
VALUES (20250000000000097, 20250103060000002, 'zh-CN', '删除文件元数据');
INSERT INTO `system_permission_translation`
VALUES (20250000000000098, 20250103060000002, 'en-US', 'Delete File Metadata');
INSERT INTO `system_permission_translation`
VALUES (20250000000000099, 20250103060000003, 'zh-CN', '更新文件元数据');
INSERT INTO `system_permission_translation`
VALUES (20250000000000100, 20250103060000003, 'en-US', 'Update File Metadata');
INSERT INTO `system_permission_translation`
VALUES (20250000000000101, 20250103060000004, 'zh-CN', '查看文件元数据详情');
INSERT INTO `system_permission_translation`
VALUES (20250000000000102, 20250103060000004, 'en-US', 'View File Metadata Details');
INSERT INTO `system_permission_translation`
VALUES (20250000000000103, 20250103060000005, 'zh-CN', '验证MIME类型唯一性');
INSERT INTO `system_permission_translation`
VALUES (20250000000000104, 20250103060000005, 'en-US', 'Verify MIME Type Uniqueness');
INSERT INTO `system_permission_translation`
VALUES (20250000000000105, 20250103060000006, 'zh-CN', '验证扩展名唯一性');
INSERT INTO `system_permission_translation`
VALUES (20250000000000106, 20250103060000006, 'en-US', 'Verify Extension Uniqueness');
INSERT INTO `system_permission_translation`
VALUES (20250000000000107, 20250103060000007, 'zh-CN', '文件元数据分页查询');
INSERT INTO `system_permission_translation`
VALUES (20250000000000108, 20250103060000007, 'en-US', 'Paginated File Metadata Query');
INSERT INTO `system_permission_translation`
VALUES (20250000000000109, 20250103070000001, 'zh-CN', '创建定时任务');
INSERT INTO `system_permission_translation`
VALUES (20250000000000110, 20250103070000001, 'en-US', 'Create Scheduled Task');
INSERT INTO `system_permission_translation`
VALUES (20250000000000111, 20250103070000002, 'zh-CN', '删除定时任务');
INSERT INTO `system_permission_translation`
VALUES (20250000000000112, 20250103070000002, 'en-US', 'Delete Scheduled Task');
INSERT INTO `system_permission_translation`
VALUES (20250000000000113, 20250103070000003, 'zh-CN', '更新定时任务');
INSERT INTO `system_permission_translation`
VALUES (20250000000000114, 20250103070000003, 'en-US', 'Update Scheduled Task');
INSERT INTO `system_permission_translation`
VALUES (20250000000000115, 20250103070000004, 'zh-CN', '查看定时任务详情');
INSERT INTO `system_permission_translation`
VALUES (20250000000000116, 20250103070000004, 'en-US', 'View Scheduled Task Details');
INSERT INTO `system_permission_translation`
VALUES (20250000000000117, 20250103070000005, 'zh-CN', '验证任务名称唯一性');
INSERT INTO `system_permission_translation`
VALUES (20250000000000118, 20250103070000005, 'en-US', 'Verify Scheduled Task Name Uniqueness');
INSERT INTO `system_permission_translation`
VALUES (20250000000000119, 20250103070000006, 'zh-CN', '定时任务分页查询');
INSERT INTO `system_permission_translation`
VALUES (20250000000000120, 20250103070000006, 'en-US', 'Paginated Scheduled Task Query');
INSERT INTO `system_permission_translation`
VALUES (20250000000000121, 20250103070000007, 'zh-CN', '切换任务状态');
INSERT INTO `system_permission_translation`
VALUES (20250000000000122, 20250103070000007, 'en-US', 'Toggle Scheduled Task Status');
INSERT INTO `system_permission_translation`
VALUES (20250000000000123, 20250103070000008, 'zh-CN', '执行定时任务');
INSERT INTO `system_permission_translation`
VALUES (20250000000000124, 20250103070000008, 'en-US', 'Execute Scheduled Task');
INSERT INTO `system_permission_translation`
VALUES (20250000000000125, 20250103080000001, 'zh-CN', '创建字典类型');
INSERT INTO `system_permission_translation`
VALUES (20250000000000126, 20250103080000001, 'en-US', 'Create Dictionary Type');
INSERT INTO `system_permission_translation`
VALUES (20250000000000127, 20250103080000002, 'zh-CN', '删除字典类型');
INSERT INTO `system_permission_translation`
VALUES (20250000000000128, 20250103080000002, 'en-US', 'Delete Dictionary Type');
INSERT INTO `system_permission_translation`
VALUES (20250000000000129, 20250103080000003, 'zh-CN', '更新字典类型');
INSERT INTO `system_permission_translation`
VALUES (20250000000000130, 20250103080000003, 'en-US', 'Update Dictionary Type');
INSERT INTO `system_permission_translation`
VALUES (20250000000000131, 20250103080000004, 'zh-CN', '查看字典类型详情');
INSERT INTO `system_permission_translation`
VALUES (20250000000000132, 20250103080000004, 'en-US', 'View Dictionary Type Details');
INSERT INTO `system_permission_translation`
VALUES (20250000000000133, 20250103080000005, 'zh-CN', '验证字典类型名称唯一性');
INSERT INTO `system_permission_translation`
VALUES (20250000000000134, 20250103080000005, 'en-US', 'Verify Dictionary Type Name Uniqueness');
INSERT INTO `system_permission_translation`
VALUES (20250000000000135, 20250103080000006, 'zh-CN', '验证字典类型代码唯一性');
INSERT INTO `system_permission_translation`
VALUES (20250000000000136, 20250103080000006, 'en-US', 'Verify Dictionary Type Code Uniqueness');
INSERT INTO `system_permission_translation`
VALUES (20250000000000137, 20250103080000007, 'zh-CN', '字典类型分页查询');
INSERT INTO `system_permission_translation`
VALUES (20250000000000138, 20250103080000007, 'en-US', 'Paginated Dictionary Type Query');
INSERT INTO `system_permission_translation`
VALUES (20250000000000139, 20250103080000008, 'zh-CN', '字典类型列表');
INSERT INTO `system_permission_translation`
VALUES (20250000000000140, 20250103080000008, 'en-US', 'List Dictionary Types');
INSERT INTO `system_permission_translation`
VALUES (20250000000000141, 20250103090000001, 'zh-CN', '创建字典数据');
INSERT INTO `system_permission_translation`
VALUES (20250000000000142, 20250103090000001, 'en-US', 'Create Dictionary Data');
INSERT INTO `system_permission_translation`
VALUES (20250000000000143, 20250103090000002, 'zh-CN', '删除字典数据');
INSERT INTO `system_permission_translation`
VALUES (20250000000000144, 20250103090000002, 'en-US', 'Delete Dictionary Data');
INSERT INTO `system_permission_translation`
VALUES (20250000000000145, 20250103090000003, 'zh-CN', '更新字典数据');
INSERT INTO `system_permission_translation`
VALUES (20250000000000146, 20250103090000003, 'en-US', 'Update Dictionary Data');
INSERT INTO `system_permission_translation`
VALUES (20250000000000147, 20250103090000004, 'zh-CN', '查看字典数据详情');
INSERT INTO `system_permission_translation`
VALUES (20250000000000148, 20250103090000004, 'en-US', 'View Dictionary Data Details');
INSERT INTO `system_permission_translation`
VALUES (20250000000000149, 20250103090000005, 'zh-CN', '验证字典数据标签唯一性');
INSERT INTO `system_permission_translation`
VALUES (20250000000000150, 20250103090000005, 'en-US', 'Verify Dictionary Data Label Uniqueness');
INSERT INTO `system_permission_translation`
VALUES (20250000000000151, 20250103090000006, 'zh-CN', '验证字典数据值唯一性');
INSERT INTO `system_permission_translation`
VALUES (20250000000000152, 20250103090000006, 'en-US', 'Verify Dictionary Data Value Uniqueness');
INSERT INTO `system_permission_translation`
VALUES (20250000000000153, 20250103090000007, 'zh-CN', '字典数据分页查询');
INSERT INTO `system_permission_translation`
VALUES (20250000000000154, 20250103090000007, 'en-US', 'Paginated Dictionary Data Query');
INSERT INTO `system_permission_translation`
VALUES (20250000000000155, 20250103090000008, 'zh-CN', '字典数据列表');
INSERT INTO `system_permission_translation`
VALUES (20250000000000156, 20250103090000008, 'en-US', 'List Dictionary Datas');
INSERT INTO `system_permission_translation`
VALUES (20250000000000157, 20250201000000001, 'zh-CN', '业务管理');
INSERT INTO `system_permission_translation`
VALUES (20250000000000158, 20250201000000001, 'en-US', 'Business Management');
INSERT INTO `system_permission_translation`
VALUES (20250000000000159, 20250202000000001, 'zh-CN', '个人中心');
INSERT INTO `system_permission_translation`
VALUES (20250000000000160, 20250202000000001, 'en-US', 'Personal Center');
INSERT INTO `system_permission_translation`
VALUES (20250000000000161, 20250202000000002, 'zh-CN', '文件管理');
INSERT INTO `system_permission_translation`
VALUES (20250000000000162, 20250202000000002, 'en-US', 'File Management');
INSERT INTO `system_permission_translation`
VALUES (20250000000000163, 20250203010000001, 'zh-CN', '个人信息');
INSERT INTO `system_permission_translation`
VALUES (20250000000000164, 20250203010000001, 'en-US', 'Personal Information');
INSERT INTO `system_permission_translation`
VALUES (20250000000000165, 20250203010000002, 'zh-CN', '修改密码');
INSERT INTO `system_permission_translation`
VALUES (20250000000000166, 20250203010000002, 'en-US', 'Change Password');
INSERT INTO `system_permission_translation`
VALUES (20250000000000167, 20250203010000003, 'zh-CN', '验证用户名唯一性');
INSERT INTO `system_permission_translation`
VALUES (20250000000000168, 20250203010000003, 'en-US', 'Verify Username Uniqueness');
INSERT INTO `system_permission_translation`
VALUES (20250000000000169, 20250203020000001, 'zh-CN', '上传文件');
INSERT INTO `system_permission_translation`
VALUES (20250000000000170, 20250203020000001, 'en-US', 'Upload File');

-- ----------------------------
-- Table structure for system_role
-- ----------------------------
DROP TABLE IF EXISTS `system_role`;
CREATE TABLE `system_role`
(
    `id`                 bigint                                                       NOT NULL COMMENT '主键ID',
    `role_code`          varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '角色代码',
    `sort`               int                                                          NOT NULL COMMENT '显示排序（1-999）',
    `role_status`        varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '角色状态（ENABLE:正常 DISABLE:禁用）',
    `created_time`       timestamp                                                    NOT NULL COMMENT '创建时间',
    `created_by`         bigint NULL DEFAULT NULL COMMENT '创建人ID',
    `last_modified_time` timestamp                                                    NOT NULL COMMENT '最后修改时间',
    `last_modified_by`   bigint NULL DEFAULT NULL COMMENT '最后修改人ID',
    PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '系统角色表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of system_role
-- ----------------------------
INSERT INTO `system_role`
VALUES (20250000000000001, 'admin', 1, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_role`
VALUES (20250000000000002, 'normal', 2, 'ENABLED', '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);

-- ----------------------------
-- Table structure for system_role_permission
-- ----------------------------
DROP TABLE IF EXISTS `system_role_permission`;
CREATE TABLE `system_role_permission`
(
    `role_id`       bigint NOT NULL COMMENT '角色ID',
    `permission_id` bigint NOT NULL COMMENT '权限ID',
    PRIMARY KEY (`role_id`, `permission_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '系统角色权限关联表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of system_role_permission
-- ----------------------------
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250001000000001);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250002000000001);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250002000000002);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250002000000003);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250101000000001);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250101000000002);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250102000000001);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250102000000002);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250102000000003);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250102000000004);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250102000000005);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250102000000006);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250102000000007);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250102000000008);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250102000000009);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103010000001);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103010000002);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103010000003);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103010000004);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103010000005);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103010000006);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103010000007);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103010000008);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103010000009);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103020000001);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103020000002);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103020000003);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103020000004);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103020000005);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103020000006);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103020000007);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103020000008);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103030000001);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103030000002);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103030000003);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103030000004);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103030000005);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103030000006);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103030000007);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103040000001);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103050000001);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103050000002);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103050000003);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103050000004);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103050000005);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103050000006);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103050000007);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103060000001);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103060000002);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103060000003);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103060000004);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103060000005);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103060000006);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103060000007);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103070000001);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103070000002);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103070000003);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103070000004);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103070000005);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103070000006);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103070000007);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103070000008);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103080000001);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103080000002);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103080000003);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103080000004);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103080000005);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103080000006);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103080000007);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103080000008);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103090000001);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103090000002);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103090000003);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103090000004);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103090000005);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103090000006);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103090000007);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250103090000008);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250201000000001);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250202000000001);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250202000000002);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250203010000001);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250203010000002);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250203010000003);
INSERT INTO `system_role_permission`
VALUES (20250000000000001, 20250203020000001);
INSERT INTO `system_role_permission`
VALUES (20250000000000002, 20250201000000001);
INSERT INTO `system_role_permission`
VALUES (20250000000000002, 20250202000000001);
INSERT INTO `system_role_permission`
VALUES (20250000000000002, 20250202000000002);
INSERT INTO `system_role_permission`
VALUES (20250000000000002, 20250203010000001);
INSERT INTO `system_role_permission`
VALUES (20250000000000002, 20250203010000002);
INSERT INTO `system_role_permission`
VALUES (20250000000000002, 20250203010000003);
INSERT INTO `system_role_permission`
VALUES (20250000000000002, 20250203020000001);

-- ----------------------------
-- Table structure for system_role_translation
-- ----------------------------
DROP TABLE IF EXISTS `system_role_translation`;
CREATE TABLE `system_role_translation`
(
    `id`            bigint                                                       NOT NULL COMMENT '角色翻译表ID',
    `role_id`       bigint                                                       NOT NULL COMMENT '角色ID',
    `language_code` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '语言代码（zh-CN:简体中文 en-US:英文）',
    `role_name`     varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '角色名称',
    `remark`        varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '备注信息',
    PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '系统角色翻译表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of system_role_translation
-- ----------------------------
INSERT INTO `system_role_translation`
VALUES (20250000000000001, 20250000000000001, 'zh-CN', '管理员', '系统管理员角色');
INSERT INTO `system_role_translation`
VALUES (20250000000000002, 20250000000000001, 'en-US', 'Admin', 'System admin role');
INSERT INTO `system_role_translation`
VALUES (20250000000000003, 20250000000000002, 'zh-CN', '用户', '普通用户角色');
INSERT INTO `system_role_translation`
VALUES (20250000000000004, 20250000000000002, 'en-US', 'User', 'Normal user role');

-- ----------------------------
-- Table structure for system_user
-- ----------------------------
DROP TABLE IF EXISTS `system_user`;
CREATE TABLE `system_user`
(
    `id`                 bigint                                                        NOT NULL COMMENT '主键ID',
    `username`           varchar(8) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci   NOT NULL COMMENT '用户名',
    `email`              varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '电子邮箱',
    `phone_number`       varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '手机号码',
    `encoded_password`   varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '加密后的密码',
    `gender`             varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '性别（MALE:男 FEMALE:女）',
    `birthday`           timestamp NULL DEFAULT NULL COMMENT '出生日期',
    `created_time`       timestamp                                                     NOT NULL COMMENT '创建时间',
    `created_by`         bigint NULL DEFAULT NULL COMMENT '创建人ID',
    `last_modified_time` timestamp                                                     NOT NULL COMMENT '最后修改时间',
    `last_modified_by`   bigint NULL DEFAULT NULL COMMENT '最后修改人ID',
    PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '系统用户表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of system_user
-- ----------------------------
INSERT INTO `system_user`
VALUES (20250000000000001, 'Admin', NULL, NULL,
        '{pbkdf2}c63e28db5fd94e6dc0c0b3ffc709c4605fd29b1ec3fe3284081cb525cb9aae06503689dbbc236f4f58bb417d1ff834c1',
        NULL, NULL, '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);
INSERT INTO `system_user`
VALUES (20250000000000002, 'User', NULL, NULL,
        '{pbkdf2}fac170d8c23026b83580b708ce652f0c4dcd4a2e00ea55cd89e2342a370228100b0d309f822c27c9521368b4b2079271',
        NULL, NULL, '2025-01-01 00:00:00', NULL, '2025-01-01 00:00:00', NULL);

-- ----------------------------
-- Table structure for system_user_role
-- ----------------------------
DROP TABLE IF EXISTS `system_user_role`;
CREATE TABLE `system_user_role`
(
    `user_id` bigint NOT NULL COMMENT '用户ID',
    `role_id` bigint NOT NULL COMMENT '角色ID',
    PRIMARY KEY (`user_id`, `role_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '系统用户角色关联表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of system_user_role
-- ----------------------------
INSERT INTO `system_user_role`
VALUES (20250000000000001, 20250000000000001);
INSERT INTO `system_user_role`
VALUES (20250000000000002, 20250000000000002);

SET
FOREIGN_KEY_CHECKS = 1;
