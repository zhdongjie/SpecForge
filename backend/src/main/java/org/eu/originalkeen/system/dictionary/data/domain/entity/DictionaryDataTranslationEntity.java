package org.eu.originalkeen.system.dictionary.data.domain.entity;

import com.mybatisflex.annotation.Table;
import org.eu.originalkeen.core.domain.entity.PrimaryKeyEntity;
import org.eu.originalkeen.system.dictionary.data.domain.dto.DictionaryDataTranslationDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 字典数据翻译实体类
 * 对应数据库中的system_dictionary_data_translation表，存储字典数据多语言翻译信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Table("system_dictionary_data_translation")
@EqualsAndHashCode(callSuper = true)
public class DictionaryDataTranslationEntity extends PrimaryKeyEntity implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -7818108884590488278L;

    /**
     * 字典数据表ID
     * 关联的字典数据主表ID
     */
    private Long dictionaryDataId;

    /**
     * 语言代码
     * 翻译的语言代码，对应 system_language_code 字典数据
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
     * 从字典数据翻译DTO创建字典数据翻译实体
     * 将字典数据翻译创建数据转换为实体对象
     *
     * @param dictionaryDataId             字典数据ID
     * @param dictionaryDataTranslationDto 字典数据翻译DTO
     * @return 字典数据翻译实体对象
     */
    public static DictionaryDataTranslationEntity of(Long dictionaryDataId, DictionaryDataTranslationDto dictionaryDataTranslationDto) {
        return new DictionaryDataTranslationEntity(
                dictionaryDataId,
                dictionaryDataTranslationDto.getLanguageCode(),
                dictionaryDataTranslationDto.getLabel(),
                dictionaryDataTranslationDto.getRemark()
        );
    }

    /**
     * 从字典数据翻译DTO创建字典数据翻译实体
     * 将字典数据翻译更新数据转换为实体对象
     *
     * @param dictionaryDataTranslationDto 字典数据翻译DTO
     * @return 字典数据翻译实体对象
     */
    public static DictionaryDataTranslationEntity of(DictionaryDataTranslationDto dictionaryDataTranslationDto) {
        return new DictionaryDataTranslationEntity(
                null,
                dictionaryDataTranslationDto.getLanguageCode(),
                dictionaryDataTranslationDto.getLabel(),
                dictionaryDataTranslationDto.getRemark()
        );
    }

} 
