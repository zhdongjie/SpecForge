package org.eu.originalkeen.system.dictionary.data.domain.bo;

import org.eu.originalkeen.system.dictionary.data.domain.dto.DictionaryDataTranslationDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 字典数据翻译业务对象
 * 用于处理字典数据翻译相关的业务逻辑
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class DictionaryDataTranslationBo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -1606693769722395630L;

    /**
     * 语言代码
     * 翻译的语言代码，例如：zh-CN、en-US
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

    /**
     * 从DTO创建BO
     *
     * @param dictionaryDataTranslationDto 字典数据翻译DTO
     * @return 字典数据翻译BO
     */
    public static DictionaryDataTranslationBo of(DictionaryDataTranslationDto dictionaryDataTranslationDto) {
        return new DictionaryDataTranslationBo(
                dictionaryDataTranslationDto.getLanguageCode(),
                dictionaryDataTranslationDto.getLabel(),
                dictionaryDataTranslationDto.getRemark()
        );
    }

}
