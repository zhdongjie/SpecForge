package org.eu.originalkeen.system.permission.domain.bo;

import org.eu.originalkeen.system.permission.domain.dto.PermissionTranslationDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 权限翻译业务对象
 * 用于在业务层处理权限的翻译信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PermissionTranslationBo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 5526852652396751718L;

    /**
     * 语言代码
     * 翻译的语言代码，对应 system_language_code 字典数据
     */
    private String languageCode;

    /**
     * 权限名称
     * 权限在该语言下的名称
     */
    private String permissionName;

    /**
     * 从权限翻译DTO创建业务对象
     * 工厂方法，将DTO转换为业务对象
     *
     * @param permissionTranslationDto 权限翻译DTO
     * @return 权限翻译业务对象
     */
    public static PermissionTranslationBo of(PermissionTranslationDto permissionTranslationDto) {
        return new PermissionTranslationBo(
                permissionTranslationDto.getLanguageCode(),
                permissionTranslationDto.getPermissionName()
        );
    }

}
