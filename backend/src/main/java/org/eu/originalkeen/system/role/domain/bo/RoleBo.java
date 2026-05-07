package org.eu.originalkeen.system.role.domain.bo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 角色业务对象
 * 用于在业务逻辑层传递角色相关信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class RoleBo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -1857749636637624506L;

    /**
     * 角色编码
     * 唯一标识角色的编码，用于系统内部识别角色
     */
    private String roleCode;

    /**
     * 角色名称
     * 角色的显示名称，便于用户识别角色
     */
    private String roleName;

}
