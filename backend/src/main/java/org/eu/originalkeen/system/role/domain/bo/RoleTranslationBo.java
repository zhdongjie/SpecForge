package org.eu.originalkeen.system.role.domain.bo;

import org.eu.originalkeen.system.role.domain.dto.RoleTranslationDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 角色翻译业务对象
 * 用于在业务层处理角色的翻译信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class RoleTranslationBo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 5918465885559732575L;

    /**
     * 语言代码
     * 翻译的语言代码，对应 system_language_code 字典数据
     */
    private String languageCode;

    /**
     * 角色名称
     * 角色在该语言下的名称
     */
    private String roleName;

    /**
     * 备注信息
     * 文件类型的备注说明
     */
    private String remark;

    /**
     * 从角色翻译DTO创建业务对象
     * 工厂方法，将DTO转换为业务对象
     *
     * @param roleTranslationDto 角色翻译DTO
     * @return 角色翻译业务对象
     */
    public static RoleTranslationBo of(RoleTranslationDto roleTranslationDto) {
        return new RoleTranslationBo(
                roleTranslationDto.getLanguageCode(),
                roleTranslationDto.getRoleName(),
                roleTranslationDto.getRemark()
        );
    }

}
