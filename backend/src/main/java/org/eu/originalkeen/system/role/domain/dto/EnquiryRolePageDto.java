package org.eu.originalkeen.system.role.domain.dto;

import org.eu.originalkeen.core.domain.dto.EnquiryPageDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 查询角色分页数据传输对象
 * 用于接收角色分页查询的条件参数
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode(callSuper = true)
public class EnquiryRolePageDto extends EnquiryPageDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -5961535282093386668L;

    /**
     * 角色名称
     * 按照角色名称进行模糊查询
     */
    private String roleName;

    /**
     * 角色状态
     * 按照角色状态进行查询，对应 system_role_status 字典数据
     */
    private String roleStatus;

}
