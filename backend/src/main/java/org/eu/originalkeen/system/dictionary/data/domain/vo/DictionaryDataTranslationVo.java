package org.eu.originalkeen.system.dictionary.data.domain.vo;

import com.fasterxml.jackson.annotation.JsonIgnore;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 字典数据翻译视图对象
 * 用于展示字典数据的翻译信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class DictionaryDataTranslationVo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -7580476139473763558L;

    /**
     * 字典数据表ID
     * 关联的字典数据主表ID
     */
    @JsonIgnore
    private Long dictionaryDataId;

    /**
     * 语言代码
     * 翻译的语言代码
     */
    private String languageCode;

    /**
     * 字典标签
     * 字典数据在该语言下的显示标签
     */
    private String label;

    /**
     * 备注信息
     * 字典数据的备注说明
     */
    private String remark;

}
