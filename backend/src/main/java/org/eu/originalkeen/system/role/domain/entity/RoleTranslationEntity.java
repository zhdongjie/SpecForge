package org.eu.originalkeen.system.role.domain.entity;

import com.mybatisflex.annotation.Table;
import org.eu.originalkeen.core.domain.entity.PrimaryKeyEntity;
import org.eu.originalkeen.system.role.domain.dto.RoleTranslationDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 角色翻译实体类
 * 对应数据库中system_role_translation表，用于存储角色的多语言翻译
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Table(value = "system_role_translation")
@EqualsAndHashCode(callSuper = true)
public class RoleTranslationEntity extends PrimaryKeyEntity implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -3547991434914109785L;

    /**
     * 角色ID
     * 角色的唯一标识
     */
    private Long roleId;

    /**
     * 语言代码
     * 翻译的语言代码，对应 system_language_code 字典数据
     */
    private String languageCode;

    /**
     * 角色名称
     * 角色在不同语言下的名称
     */
    private String roleName;

    /**
     * 备注信息
     * 角色的备注说明
     */
    private String remark;

    /**
     * 从角色翻译DTO创建实体对象
     * 工厂方法，将DTO转换为实体对象
     *
     * @param roleId             角色ID
     * @param roleTranslationDto 角色翻译DTO
     * @return 角色翻译实体
     */
    public static RoleTranslationEntity of(Long roleId, RoleTranslationDto roleTranslationDto) {
        return new RoleTranslationEntity(
                roleId,
                roleTranslationDto.getLanguageCode(),
                roleTranslationDto.getRoleName(),
                roleTranslationDto.getRemark()
        );
    }

}
