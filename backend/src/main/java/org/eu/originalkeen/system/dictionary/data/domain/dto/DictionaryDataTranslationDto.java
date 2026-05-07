package org.eu.originalkeen.system.dictionary.data.domain.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 字典数据翻译数据传输对象
 * 用于创建和更新字典数据翻译信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class DictionaryDataTranslationDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 6219363827543301262L;

    /**
     * 语言代码
     * 翻译的语言代码，例如：zh-CN、en-US
     */
    @NotBlank(message = "{form.common.languageCodeIsRequired}")
    @Size(max = 16, message = "{form.common.invalidLanguageCode}")
    private String languageCode;

    /**
     * 字典标签
     * 字典数据在该语言下的显示标签
     */
    @NotBlank(message = "{form.dictionaryData.labelIsRequired}")
    @Size(max = 64, message = "{form.dictionaryData.invalidLabelLength}")
    private String label;

    /**
     * 备注信息
     * 字典数据的备注说明
     */
    @Size(max = 300, message = "{form.common.invalidRemarkLength}")
    private String remark;

} 
