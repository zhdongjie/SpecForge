package org.eu.originalkeen.system.dictionary.type.domain.bo;

import org.eu.originalkeen.system.dictionary.type.domain.dto.CreateDictionaryTypeDto;
import org.eu.originalkeen.system.dictionary.type.domain.dto.DictionaryTypeTranslationDto;
import org.eu.originalkeen.system.dictionary.type.domain.dto.UpdateDictionaryTypeDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.List;

/**
 * 校验字典类型业务对象
 * 用于在业务层校验字典类型的各项信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ValidateDictionaryTypeBo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -8606030448002867777L;

    /**
     * 字典类型ID
     * 字典类型的唯一标识，用于更新时排除自身
     */
    private Long id;

    /**
     * 字典类型代码
     * 字典类型的唯一代码标识
     */
    private String dictionaryTypeCode;

    /**
     * 字典类型状态
     * 字典类型的状态，对应 system_dictionary_type_status 字典数据
     */
    private String dictionaryTypeStatus;

    /**
     * 字典类型翻译列表
     * 字典类型在各语言下的翻译信息
     */
    private List<DictionaryTypeTranslationBo> translations;

    /**
     * 从创建字典类型DTO创建业务对象
     * 工厂方法，将创建DTO转换为业务对象
     *
     * @param createDictionaryTypeDto 创建字典类型DTO
     * @return 校验字典类型业务对象
     */
    public static ValidateDictionaryTypeBo of(CreateDictionaryTypeDto createDictionaryTypeDto) {
        return new ValidateDictionaryTypeBo(
                null,
                createDictionaryTypeDto.getDictionaryTypeCode(),
                createDictionaryTypeDto.getDictionaryTypeStatus(),
                convertTranslations(createDictionaryTypeDto.getTranslations())
        );
    }

    /**
     * 从更新字典类型DTO创建业务对象
     * 工厂方法，将更新DTO转换为业务对象
     *
     * @param updateDictionaryTypeDto 更新字典类型DTO
     * @return 校验字典类型业务对象
     */
    public static ValidateDictionaryTypeBo of(UpdateDictionaryTypeDto updateDictionaryTypeDto) {
        return new ValidateDictionaryTypeBo(
                updateDictionaryTypeDto.getId(),
                updateDictionaryTypeDto.getDictionaryTypeCode(),
                updateDictionaryTypeDto.getDictionaryTypeStatus(),
                convertTranslations(updateDictionaryTypeDto.getTranslations())
        );
    }

    /**
     * 将字典类型翻译DTO列表转换为业务对象列表
     * 工厂方法，将DTO列表转换为业务对象列表
     *
     * @param translationDtoList 字典类型翻译DTO列表
     * @return 字典类型翻译业务对象列表
     */
    private static List<DictionaryTypeTranslationBo> convertTranslations(List<DictionaryTypeTranslationDto> translationDtoList) {
        return translationDtoList.stream()
                .map(DictionaryTypeTranslationBo::of)
                .toList();
    }

} 
