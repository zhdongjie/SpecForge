package org.eu.originalkeen.system.role.domain.bo;

import org.eu.originalkeen.system.role.domain.dto.CreateRoleDto;
import org.eu.originalkeen.system.role.domain.dto.RoleTranslationDto;
import org.eu.originalkeen.system.role.domain.dto.UpdateRoleDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.List;

/**
 * 校验角色业务对象
 * 用于在业务层校验角色的各种属性
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ValidateRoleBo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 3535927194335627013L;

    /**
     * 角色ID
     * 角色的唯一标识，更新时使用
     */
    private Long id;

    /**
     * 角色代码
     * 角色的唯一代码标识
     */
    private String roleCode;

    /**
     * 角色状态
     * 角色的状态，对应 system_role_status 字典数据
     */
    private String roleStatus;

    /**
     * 角色翻译列表
     * 角色的多语言翻译列表
     */
    private List<RoleTranslationBo> translations;

    /**
     * 从创建角色DTO创建校验角色业务对象
     * 将角色创建数据转换为校验对象
     *
     * @param createRoleDto 创建角色DTO
     * @return 校验角色业务对象
     */
    public static ValidateRoleBo of(CreateRoleDto createRoleDto) {
        return new ValidateRoleBo(
                null,
                createRoleDto.getRoleCode(),
                createRoleDto.getRoleStatus(),
                convertTranslations(createRoleDto.getTranslations())
        );
    }

    /**
     * 从更新角色DTO创建校验角色业务对象
     * 将角色更新数据转换为校验对象
     *
     * @param updateRoleDto 更新角色DTO
     * @return 校验角色业务对象
     */
    public static ValidateRoleBo of(UpdateRoleDto updateRoleDto) {
        return new ValidateRoleBo(
                updateRoleDto.getId(),
                updateRoleDto.getRoleCode(),
                updateRoleDto.getRoleStatus(),
                convertTranslations(updateRoleDto.getTranslations())
        );
    }

    /**
     * 将字典类型翻译DTO列表转换为业务对象列表
     * 工厂方法，将DTO列表转换为业务对象列表
     *
     * @param translationDtoList 字典类型翻译DTO列表
     * @return 字典类型翻译业务对象列表
     */
    private static List<RoleTranslationBo> convertTranslations(List<RoleTranslationDto> translationDtoList) {
        return translationDtoList.stream()
                .map(RoleTranslationBo::of)
                .toList();
    }

}
