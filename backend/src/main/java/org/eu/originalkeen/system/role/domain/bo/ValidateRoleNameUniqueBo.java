package org.eu.originalkeen.system.role.domain.bo;

import org.eu.originalkeen.system.role.domain.dto.ValidateRoleNameUniqueDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.List;

/**
 * 校验角色名称唯一性业务对象
 * 用于在业务层校验角色名称的唯一性
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ValidateRoleNameUniqueBo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -5519670520502739697L;

    /**
     * 角色ID
     * 角色的唯一标识，用于在校验唯一性时排除自身
     */
    private Long id;

    /**
     * 角色名称列表
     * 需要校验唯一性的角色名称列表
     */
    private List<String> roleNames;

    /**
     * 从角色名称唯一性DTO创建业务对象
     * 工厂方法，将DTO转换为业务对象
     *
     * @param validateRoleNameUniqueDto 角色名称唯一性DTO
     * @return 校验角色名称唯一性业务对象
     */
    public static ValidateRoleNameUniqueBo of(ValidateRoleNameUniqueDto validateRoleNameUniqueDto) {
        return new ValidateRoleNameUniqueBo(
                validateRoleNameUniqueDto.getId(),
                List.of(validateRoleNameUniqueDto.getRoleName())
        );
    }

    /**
     * 从校验角色业务对象创建角色名称唯一性业务对象
     * 工厂方法，将校验角色业务对象转换为角色名称唯一性业务对象
     *
     * @param validateRoleBo 校验角色业务对象
     * @return 校验角色名称唯一性业务对象
     */
    public static ValidateRoleNameUniqueBo of(ValidateRoleBo validateRoleBo) {
        List<String> roleNames = validateRoleBo.getTranslations().stream()
                .map(RoleTranslationBo::getRoleName).toList();
        return new ValidateRoleNameUniqueBo(
                validateRoleBo.getId(),
                roleNames
        );
    }

}
