package org.eu.originalkeen.system.role.domain.vo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 角色列表视图对象
 * 用于返回角色列表数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class RoleListVo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -3065816013668972104L;

    /**
     * 角色ID
     * 角色的唯一标识
     */
    private Long id;

    /**
     * 角色名称
     * 角色的名称
     */
    private String roleName;

    /**
     * 角色状态
     * 角色的状态，对应 system_role_status 字典数据
     */
    private String status;

}
