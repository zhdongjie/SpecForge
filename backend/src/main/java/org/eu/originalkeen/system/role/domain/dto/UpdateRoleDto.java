package org.eu.originalkeen.system.role.domain.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.validator.constraints.Range;

import java.io.Serial;
import java.io.Serializable;
import java.util.List;
import java.util.Set;

/**
 * 更新角色数据传输对象
 * 用于接收和校验更新角色的请求数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UpdateRoleDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 6923658791640728136L;

    /**
     * 角色ID
     * 要更新的角色的唯一标识
     */
    @NotNull(message = "{form.common.idIsRequired}")
    private Long id;

    /**
     * 角色代码
     * 角色的唯一代码标识
     */
    @NotBlank(message = "{form.role.roleCodeIsRequired}")
    @Size(max = 64, message = "{form.role.invalidRoleCodeLength}")
    private String roleCode;

    /**
     * 排序值
     * 角色的显示顺序，范围1-999
     */
    @NotNull(message = "{form.common.sortIsRequired}")
    @Range(min = 1, max = 999, message = "{form.common.invalidSortSize}")
    private Integer sort;

    /**
     * 角色状态
     * 角色的状态，对应 system_role_status 字典数据
     */
    @NotBlank(message = "{form.role.roleStatusIsRequired}")
    private String roleStatus;

    /**
     * 角色翻译列表
     * 角色在不同语言下的翻译列表
     */
    @Valid
    @NotEmpty(message = "{form.role.roleTranslationsIsRequired}")
    private List<RoleTranslationDto> translations;

    /**
     * 权限ID列表
     * 角色关联的权限ID列表
     */
    @NotEmpty(message = "{form.role.permissionListIsRequired}")
    private Set<Long> permissionIds;

}
