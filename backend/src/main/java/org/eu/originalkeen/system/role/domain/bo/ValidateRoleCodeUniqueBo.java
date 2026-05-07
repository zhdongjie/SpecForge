package org.eu.originalkeen.system.role.domain.bo;

import org.eu.originalkeen.system.role.domain.dto.ValidateRoleCodeUniqueDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 校验角色代码唯一性业务对象
 * 用于在业务层校验角色代码的唯一性
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ValidateRoleCodeUniqueBo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -6906027032941098633L;

    /**
     * 角色ID
     * 角色的唯一标识，用于在校验唯一性时排除自身
     */
    private Long id;

    /**
     * 角色代码
     * 需要校验唯一性的角色代码
     */
    private String roleCode;

    /**
     * 从角色代码唯一性DTO创建业务对象
     * 工厂方法，将DTO转换为业务对象
     *
     * @param validateRoleCodeUniqueDto 角色代码唯一性DTO
     * @return 校验角色代码唯一性业务对象
     */
    public static ValidateRoleCodeUniqueBo of(ValidateRoleCodeUniqueDto validateRoleCodeUniqueDto) {
        return new ValidateRoleCodeUniqueBo(
                validateRoleCodeUniqueDto.getId(),
                validateRoleCodeUniqueDto.getRoleCode()
        );
    }

    /**
     * 从校验角色业务对象创建角色代码唯一性业务对象
     * 工厂方法，将校验角色业务对象转换为角色代码唯一性业务对象
     *
     * @param validateRoleBo 校验角色业务对象
     * @return 校验角色代码唯一性业务对象
     */
    public static ValidateRoleCodeUniqueBo of(ValidateRoleBo validateRoleBo) {
        return new ValidateRoleCodeUniqueBo(
                validateRoleBo.getId(),
                validateRoleBo.getRoleCode()
        );
    }

}
