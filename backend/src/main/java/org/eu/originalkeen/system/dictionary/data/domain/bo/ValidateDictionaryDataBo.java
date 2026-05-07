package org.eu.originalkeen.system.dictionary.data.domain.bo;

import org.eu.originalkeen.system.dictionary.data.domain.dto.CreateDictionaryDataDto;
import org.eu.originalkeen.system.dictionary.data.domain.dto.DictionaryDataTranslationDto;
import org.eu.originalkeen.system.dictionary.data.domain.dto.UpdateDictionaryDataDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.List;

/**
 * 校验字典数据业务对象
 * 用于校验字典数据信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ValidateDictionaryDataBo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 2816699075872435325L;

    /**
     * 字典数据ID
     * 当前字典数据ID，更新时使用，新增时为空
     */
    private Long id;

    /**
     * 字典类型代码
     * 关联的字典类型代码
     */
    private String dictionaryTypeCode;

    /**
     * 字典值
     * 字典数据的值
     */
    private String value;

    /**
     * 字典数据状态
     * 字典数据的状态，对应 system_dictionary_data_status 字典数据
     */
    private String dictionaryDataStatus;

    /**
     * 字典数据翻译列表
     * 字典数据在各语言下的翻译信息
     */
    private List<DictionaryDataTranslationBo> translations;

    /**
     * 从创建字典数据DTO创建校验字典数据BO
     *
     * @param createDictionaryDataDto 创建字典数据DTO
     * @return 校验字典数据BO
     */
    public static ValidateDictionaryDataBo of(CreateDictionaryDataDto createDictionaryDataDto) {
        return new ValidateDictionaryDataBo(
                null,
                createDictionaryDataDto.getDictionaryTypeCode(),
                createDictionaryDataDto.getValue(),
                createDictionaryDataDto.getDictionaryDataStatus(),
                convertTranslations(createDictionaryDataDto.getTranslations())
        );
    }

    /**
     * 从更新字典数据DTO创建校验字典数据BO
     *
     * @param updateDictionaryDataDto 更新字典数据DTO
     * @return 校验字典数据BO
     */
    public static ValidateDictionaryDataBo of(UpdateDictionaryDataDto updateDictionaryDataDto) {
        return new ValidateDictionaryDataBo(
                updateDictionaryDataDto.getId(),
                updateDictionaryDataDto.getDictionaryTypeCode(),
                updateDictionaryDataDto.getValue(),
                updateDictionaryDataDto.getDictionaryDataStatus(),
                convertTranslations(updateDictionaryDataDto.getTranslations())
        );
    }

    /**
     * 将字典数据翻译DTO列表转换为业务对象列表
     * 工厂方法，将DTO列表转换为业务对象列表
     *
     * @param translationDtoList 字典数据翻译DTO列表
     * @return 字典数据翻译业务对象列表
     */
    private static List<DictionaryDataTranslationBo> convertTranslations(List<DictionaryDataTranslationDto> translationDtoList) {
        return translationDtoList.stream()
                .map(DictionaryDataTranslationBo::of)
                .toList();
    }

} 
