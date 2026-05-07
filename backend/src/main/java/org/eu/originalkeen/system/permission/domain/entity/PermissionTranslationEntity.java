package org.eu.originalkeen.system.permission.domain.entity;

import com.mybatisflex.annotation.Table;
import org.eu.originalkeen.core.domain.entity.PrimaryKeyEntity;
import org.eu.originalkeen.system.permission.domain.dto.PermissionTranslationDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 权限翻译实体类
 * 对应数据库中system_permission_translation表，用于存储权限的多语言翻译
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Table(value = "system_permission_translation")
@EqualsAndHashCode(callSuper = true)
public class PermissionTranslationEntity extends PrimaryKeyEntity implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 6787101102165339914L;

    /**
     * 权限ID
     * 权限的唯一标识
     */
    private Long permissionId;

    /**
     * 语言代码
     * 翻译的语言代码，对应 system_language_code 字典数据
     */
    private String languageCode;

    /**
     * 权限名称
     * 权限在不同语言下的名称
     */
    private String permissionName;

    /**
     * 从权限翻译DTO创建实体对象
     * 工厂方法，将DTO转换为实体对象
     *
     * @param permissionId             权限ID
     * @param permissionTranslationDto 权限翻译DTO
     * @return 权限翻译实体
     */
    public static PermissionTranslationEntity of(Long permissionId, PermissionTranslationDto permissionTranslationDto) {
        return new PermissionTranslationEntity(
                permissionId,
                permissionTranslationDto.getLanguageCode(),
                permissionTranslationDto.getPermissionName()
        );
    }

}
