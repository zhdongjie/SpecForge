package org.eu.originalkeen.system.dictionary.type.domain.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.validator.constraints.Length;

import java.io.Serial;
import java.io.Serializable;

/**
 * 字典类型翻译数据传输对象
 * 用于接收和校验字典类型翻译的请求数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class DictionaryTypeTranslationDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -2122769157106664191L;

    /**
     * 语言代码
     * 翻译的语言代码，对应 system_language_code 字典数据
     */
    @NotBlank(message = "{form.common.languageCodeIsRequired}")
    private String languageCode;

    /**
     * 字典类型名称
     * 字典类型在该语言下的名称
     */
    @NotBlank(message = "{form.dictionaryType.dictionaryTypeNameIsRequired}")
    @Length(max = 64, message = "{form.dictionaryType.invalidDictionaryTypeNameLength}")
    private String dictionaryTypeName;

    /**
     * 备注信息
     * 字典类型的备注说明
     */
    @Length(max = 300, message = "{form.common.invalidRemarkLength}")
    private String remark;

}
