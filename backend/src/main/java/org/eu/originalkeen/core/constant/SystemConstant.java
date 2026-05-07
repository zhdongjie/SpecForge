package org.eu.originalkeen.core.constant;

import java.util.Set;

/**
 * 系统常量类
 * 定义系统中使用的各种常量值
 */
public class SystemConstant {

    /**
     * 安全匿名用户标识
     * 用于标识未登录的匿名用户
     */
    public static final String SECURITY_ANONYMOUS_USER = "anonymousUser";

    /**
     * 角色权限前缀
     * 用于标识角色类型的权限
     */
    public static final String ROLE_AUTHORITY_PREFIX = "ROLE_";

    /**
     * Redis登录用户信息前缀
     * 用于在Redis中存储登录用户信息的键前缀
     */
    public static final String REDIS_PREFIX_LOGIN = "LOGIN:";

    /**
     * 默认当前页码
     * 分页查询时的默认当前页码
     */
    public static final Long DEFAULT_CURRENT_PAGE = 1L;

    /**
     * 默认每页大小
     * 分页查询时的默认每页记录数
     */
    public static final Long DEFAULT_PAGE_SIZE = 20L;

    /**
     * 默认角色列表
     * 新用户注册时默认分配的角色
     */
    public static final Set<String> DEFAULT_ROLE_CODES = Set.of(
            "normal"
    );

    /**
     * 权限根节点ID
     * 权限树结构的根节点标识
     */
    public static final Long PERMISSION_ROOT_NODE_ID = 0L;

    /**
     * 语言代码字典类型代码
     * 用于标识系统支持的语言代码的字典类型
     */
    public static final String DICTIONARY_CODE_LANGUAGE_CODE = "system_language_code";
    /**
     * 角色状态字典代码
     * 用于标识系统角色状态的字典类型代码
     */
    public static final String DICTIONARY_CODE_ROLE_STATUS = "system_role_status";
    /**
     * 权限类型字典代码
     * 用于标识系统权限类型的字典类型代码
     */
    public static final String DICTIONARY_CODE_PERMISSION_TYPE = "system_permission_type";
    /**
     * 权限链接目标字典代码
     * 用于标识系统权限链接目标的字典类型代码
     */
    public static final String DICTIONARY_CODE_PERMISSION_LINK_TARGET = "system_permission_link_target";
    /**
     * 权限状态字典代码
     * 用于标识系统权限状态的字典类型代码
     */
    public static final String DICTIONARY_CODE_PERMISSION_STATUS = "system_permission_status";
    /**
     * 字典类型状态字典代码
     * 用于标识字典类型状态的字典类型代码
     */
    public static final String DICTIONARY_CODE_DICTIONARY_TYPE_STATUS = "system_dictionary_type_status";
    /**
     * 字典数据状态字典代码
     * 用于标识字典数据状态的字典类型代码
     */
    public static final String DICTIONARY_CODE_DICTIONARY_DATA_STATUS = "system_dictionary_data_status";
    /**
     * 用户性别字典代码
     * 用于标识用户性别的字典类型代码
     */
    public static final String DICTIONARY_CODE_USER_GENDER = "system_user_gender";

    /**
     * 角色启用状态
     * 表示角色处于启用状态的值
     */
    public static final String ROLE_ENABLED_STATUS = "ENABLED";
    /**
     * 权限启用状态
     * 表示权限处于启用状态的值
     */
    public static final String PERMISSION_ENABLED_STATUS = "ENABLED";
    /**
     * 字典类型启用状态
     * 表示字典类型处于启用状态的值
     */
    public static final String DICTIONARY_TYPE_ENABLED_STATUS = "ENABLED";
    /**
     * 字典数据启用状态
     * 表示字典数据处于启用状态的值
     */
    public static final String DICTIONARY_DATA_ENABLED_STATUS = "ENABLED";
    /**
     * 权限类型-子标题
     * 表示权限类型为子标题的值
     */
    public static final String PERMISSION_TYPE_SUBHEADER = "SUBHEADER";
    /**
     * 权限类型-分组
     * 表示权限类型为分组的值
     */
    public static final String PERMISSION_TYPE_GROUP = "GROUP";
    /**
     * 权限类型-模板
     * 表示权限类型为模板的值
     */
    public static final String PERMISSION_TYPE_TEMPLATE = "TEMPLATE";
    /**
     * 权限类型-链接
     * 表示权限类型为链接的值
     */
    public static final String PERMISSION_TYPE_LINK = "LINK";
    /**
     * 权限类型-按钮
     * 表示权限类型为按钮的值
     */
    public static final String PERMISSION_TYPE_BUTTON = "BUTTON";
    /**
     * 权限类型-功能
     * 表示权限类型为功能的值
     */
    public static final String PERMISSION_TYPE_FUNCTION = "FUNCTION";

    /**
     * 私有构造函数
     * 防止实例化工具类
     */
    private SystemConstant() {
    }

}
