package org.eu.originalkeen.system.permission.domain.bo;

import org.eu.originalkeen.system.permission.domain.dto.ValidateAuthorityUniqueDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 校验权限标识唯一性业务对象
 * 用于在业务层校验权限标识的唯一性
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ValidateAuthorityUniqueBo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 4568327571319780097L;

    /**
     * 权限ID
     * 权限的唯一标识，用于在校验唯一性时排除自身
     */
    private Long id;

    /**
     * 权限标识
     * 要校验唯一性的权限标识字符串
     */
    private String authority;

    /**
     * 从权限标识唯一性DTO创建业务对象
     * 工厂方法，将DTO转换为业务对象
     *
     * @param validateAuthorityUniqueDto 权限标识唯一性DTO
     * @return 校验权限标识唯一性业务对象
     */
    public static ValidateAuthorityUniqueBo of(ValidateAuthorityUniqueDto validateAuthorityUniqueDto) {
        return new ValidateAuthorityUniqueBo(
                validateAuthorityUniqueDto.getId(),
                validateAuthorityUniqueDto.getAuthority()
        );
    }

    /**
     * 从校验权限业务对象创建权限标识唯一性业务对象
     * 工厂方法，将校验权限业务对象转换为权限标识唯一性业务对象
     *
     * @param validatePermissionBo 校验权限业务对象
     * @return 校验权限标识唯一性业务对象
     */
    public static ValidateAuthorityUniqueBo of(ValidatePermissionBo validatePermissionBo) {
        return new ValidateAuthorityUniqueBo(
                validatePermissionBo.getId(),
                validatePermissionBo.getAuthority()
        );
    }

}
