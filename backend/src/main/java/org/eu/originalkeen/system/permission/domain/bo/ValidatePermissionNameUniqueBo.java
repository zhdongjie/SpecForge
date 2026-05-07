package org.eu.originalkeen.system.permission.domain.bo;

import org.eu.originalkeen.system.permission.domain.dto.ValidatePermissionNameUniqueDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.List;

/**
 * 校验权限名称唯一性业务对象
 * 用于在业务层校验权限名称的唯一性
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ValidatePermissionNameUniqueBo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -7584188550410092520L;

    /**
     * 权限ID
     * 权限的唯一标识，用于在校验唯一性时排除自身
     */
    private Long id;

    /**
     * 权限名称列表
     * 要校验唯一性的权限名称列表
     */
    private List<String> permissionNames;

    /**
     * 从权限名称唯一性DTO创建业务对象
     * 工厂方法，将DTO转换为业务对象
     *
     * @param validatePermissionNameUniqueDto 权限名称唯一性DTO
     * @return 校验权限名称唯一性业务对象
     */
    public static ValidatePermissionNameUniqueBo of(ValidatePermissionNameUniqueDto validatePermissionNameUniqueDto) {
        return new ValidatePermissionNameUniqueBo(
                validatePermissionNameUniqueDto.getId(),
                List.of(validatePermissionNameUniqueDto.getPermissionName())
        );
    }

    /**
     * 从校验权限业务对象创建权限名称唯一性业务对象
     * 工厂方法，将校验权限业务对象转换为权限名称唯一性业务对象
     *
     * @param validatePermissionBo 校验权限业务对象
     * @return 校验权限名称唯一性业务对象
     */
    public static ValidatePermissionNameUniqueBo of(ValidatePermissionBo validatePermissionBo) {
        List<String> permissionNames = validatePermissionBo.getTranslations().stream()
                .map(PermissionTranslationBo::getPermissionName).toList();
        return new ValidatePermissionNameUniqueBo(
                validatePermissionBo.getId(),
                permissionNames
        );
    }

}
