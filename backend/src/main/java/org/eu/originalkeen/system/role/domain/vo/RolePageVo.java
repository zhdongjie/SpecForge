package org.eu.originalkeen.system.role.domain.vo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.Date;

/**
 * 角色分页视图对象
 * 用于返回角色分页列表数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class RolePageVo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -2535103564122977571L;

    /**
     * 角色ID
     * 角色的唯一标识
     */
    private Long id;

    /**
     * 角色代码
     * 角色的唯一代码标识
     */
    private String roleCode;

    /**
     * 排序值
     * 角色的显示顺序，值越小越靠前
     */
    private Integer sort;

    /**
     * 角色状态
     * 角色的状态，对应 system_role_status 字典数据
     */
    private String roleStatus;

    /**
     * 角色名称
     * 角色的名称
     */
    private String roleName;

    /**
     * 备注信息
     * 角色的备注说明
     */
    private String remark;

    /**
     * 创建时间
     * 角色的创建时间
     */
    private Date createdTime;

}
