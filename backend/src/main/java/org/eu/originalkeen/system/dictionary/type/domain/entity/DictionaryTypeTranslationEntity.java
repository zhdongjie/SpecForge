package org.eu.originalkeen.system.dictionary.type.domain.entity;

import com.mybatisflex.annotation.Table;
import org.eu.originalkeen.core.domain.entity.PrimaryKeyEntity;
import org.eu.originalkeen.system.dictionary.type.domain.dto.DictionaryTypeTranslationDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 字典类型翻译实体类
 * 对应数据库中的system_dictionary_type_translation表，存储字典类型多语言翻译信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Table("system_dictionary_type_translation")
@EqualsAndHashCode(callSuper = true)
public class DictionaryTypeTranslationEntity extends PrimaryKeyEntity implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 1292054632627112684L;

    /**
     * 字典类型表ID
     * 关联的字典类型主表ID
     */
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

    /**
     * 从字典类型翻译DTO创建字典类型翻译实体
     * 将字典类型翻译创建数据转换为实体对象
     *
     * @param dictionaryTypeId             字典类型ID
     * @param dictionaryTypeTranslationDto 字典类型翻译DTO
     * @return 字典类型翻译实体对象
     */
    public static DictionaryTypeTranslationEntity of(Long dictionaryTypeId, DictionaryTypeTranslationDto dictionaryTypeTranslationDto) {
        return new DictionaryTypeTranslationEntity(
                dictionaryTypeId,
                dictionaryTypeTranslationDto.getLanguageCode(),
                dictionaryTypeTranslationDto.getDictionaryTypeName(),
                dictionaryTypeTranslationDto.getRemark()
        );
    }

    /**
     * 从字典类型翻译DTO创建字典类型翻译实体
     * 将字典类型翻译更新数据转换为实体对象
     *
     * @param dictionaryTypeTranslationDto 字典类型翻译DTO
     * @return 字典类型翻译实体对象
     */
    public static DictionaryTypeTranslationEntity of(DictionaryTypeTranslationDto dictionaryTypeTranslationDto) {
        return new DictionaryTypeTranslationEntity(
                null,
                dictionaryTypeTranslationDto.getLanguageCode(),
                dictionaryTypeTranslationDto.getDictionaryTypeName(),
                dictionaryTypeTranslationDto.getRemark()
        );
    }

}
