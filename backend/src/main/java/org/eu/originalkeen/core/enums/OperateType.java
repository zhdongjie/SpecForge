package org.eu.originalkeen.core.enums;

/**
 * 操作类型枚举
 * 用于标识不同的业务操作类型
 */
public enum OperateType {

    /**
     * 新增操作
     */
    INSERT,

    /**
     * 删除操作
     */
    DELETE,

    /**
     * 更新操作
     */
    UPDATE,

    /**
     * 导出操作
     */
    EXPORT,

    /**
     * 导入操作
     */
    IMPORT,

    /**
     * 清理操作
     */
    CLEAN,

    /**
     * 执行操作
     */
    EXECUTE,

    /**
     * 切换状态操作
     */
    TOGGLE_STATUS,

}
