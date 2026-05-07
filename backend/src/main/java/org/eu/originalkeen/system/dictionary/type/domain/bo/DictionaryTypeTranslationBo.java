package org.eu.originalkeen.system.dictionary.type.domain.bo;

import org.eu.originalkeen.system.dictionary.type.domain.dto.DictionaryTypeTranslationDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 字典类型翻译业务对象
 * 用于在业务层处理字典类型的翻译信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class DictionaryTypeTranslationBo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -4956077162844684097L;

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

    /**
     * 从字典类型翻译DTO创建业务对象
     * 工厂方法，将DTO转换为业务对象
     *
     * @param dictionaryTypeTranslationDto 字典类型翻译DTO
     * @return 字典类型翻译业务对象
     */
    public static DictionaryTypeTranslationBo of(DictionaryTypeTranslationDto dictionaryTypeTranslationDto) {
        return new DictionaryTypeTranslationBo(
                dictionaryTypeTranslationDto.getLanguageCode(),
                dictionaryTypeTranslationDto.getDictionaryTypeName(),
                dictionaryTypeTranslationDto.getRemark()
        );
    }

}
