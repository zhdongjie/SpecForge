package org.eu.originalkeen.system.permission.domain.bo;

import org.eu.originalkeen.system.permission.domain.dto.CreatePermissionDto;
import org.eu.originalkeen.system.permission.domain.dto.PermissionTranslationDto;
import org.eu.originalkeen.system.permission.domain.dto.UpdatePermissionDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.List;

/**
 * 校验权限业务对象
 * 用于在业务层校验权限的各种属性
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ValidatePermissionBo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 460504854609803864L;

    /**
     * 权限ID
     * 权限的唯一标识，更新时使用
     */
    private Long id;

    /**
     * 父级ID
     * 父级权限的ID，用于构建权限树结构
     */
    private Long parentId;

    /**
     * 权限标识
     * 权限的唯一标识字符串，用于授权校验
     */
    private String authority;

    /**
     * 权限类型
     * 权限的类型，对应 system_permission_type 字典数据
     */
    private String permissionType;

    /**
     * 链接目标
     * 外部链接的打开方式，对应 system_permission_link_target 字典数据
     */
    private String linkTarget;

    /**
     * 权限状态
     * 权限的状态，对应 system_permission_status 字典数据
     */
    private String permissionStatus;

    /**
     * 权限翻译列表
     * 权限的多语言翻译列表
     */
    private List<PermissionTranslationBo> translations;

    /**
     * 从创建权限DTO创建校验权限业务对象
     * 工厂方法，将创建权限DTO转换为校验权限业务对象
     *
     * @param createPermissionDto 创建权限DTO
     * @return 校验权限业务对象
     */
    public static ValidatePermissionBo of(CreatePermissionDto createPermissionDto) {
        return new ValidatePermissionBo(
                null,
                createPermissionDto.getParentId(),
                createPermissionDto.getAuthority(),
                createPermissionDto.getPermissionType(),
                createPermissionDto.getLinkTarget(),
                createPermissionDto.getPermissionStatus(),
                convertTranslations(createPermissionDto.getTranslations())
        );
    }

    /**
     * 从更新权限DTO创建校验权限业务对象
     * 工厂方法，将更新权限DTO转换为校验权限业务对象
     *
     * @param updatePermissionDto 更新权限DTO
     * @return 校验权限业务对象
     */
    public static ValidatePermissionBo of(UpdatePermissionDto updatePermissionDto) {
        return new ValidatePermissionBo(
                updatePermissionDto.getId(),
                updatePermissionDto.getParentId(),
                updatePermissionDto.getAuthority(),
                updatePermissionDto.getPermissionType(),
                updatePermissionDto.getLinkTarget(),
                updatePermissionDto.getPermissionStatus(),
                convertTranslations(updatePermissionDto.getTranslations())
        );
    }

    /**
     * 将权限翻译DTO列表转换为业务对象列表
     * 工厂方法，将DTO列表转换为业务对象列表
     *
     * @param translationDtoList 权限翻译DTO列表
     * @return 权限翻译业务对象列表
     */
    private static List<PermissionTranslationBo> convertTranslations(List<PermissionTranslationDto> translationDtoList) {
        return translationDtoList.stream()
                .map(PermissionTranslationBo::of)
                .toList();
    }

}
