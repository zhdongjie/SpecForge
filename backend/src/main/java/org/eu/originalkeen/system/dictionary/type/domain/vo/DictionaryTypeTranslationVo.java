package org.eu.originalkeen.system.dictionary.type.domain.vo;

import com.fasterxml.jackson.annotation.JsonIgnore;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 字典类型翻译视图对象
 * 用于返回字典类型翻译信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class DictionaryTypeTranslationVo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -1770951710005677165L;

    /**
     * 字典类型表ID
     * 关联的字典类型主表ID
     */
    @JsonIgnore
    private Long dictionaryTypeId;

    /**
     * 语言代码
     * 翻译的语言代码，对应 system_language_code 字典数据
     */
    private String languageCode;

    /**
     * 字典类型名称
     * 字典类型在该语言下的名称
     */
    private String dictionaryTypeName;

    /**
     * 备注信息
     * 字典类型的备注说明
     */
    private String remark;

}
