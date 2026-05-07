package org.eu.originalkeen.system.dictionary.data.domain.bo;

import org.eu.originalkeen.system.dictionary.data.domain.dto.ValidateDictionaryDataLabelUniqueDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.List;

/**
 * 校验字典数据标签唯一性业务对象
 * 用于校验字典数据标签是否已被使用
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ValidateDictionaryDataLabelUniqueBo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -2912504178305704808L;

    /**
     * 字典数据ID
     * 当前字典数据ID，更新时使用，新增时可为空
     */
    private Long id;

    /**
     * 字典类型代码
     * 字典类型的唯一代码标识
     */
    private String dictionaryTypeCode;

    /**
     * 字典标签列表
     * 需要校验唯一性的字典标签列表
     */
    private List<String> labels;

    /**
     * 从DTO创建BO
     *
     * @param validateDictionaryDataLabelUniqueDto 校验字典数据标签唯一性DTO
     * @return 校验字典数据标签唯一性BO
     */
    public static ValidateDictionaryDataLabelUniqueBo of(ValidateDictionaryDataLabelUniqueDto validateDictionaryDataLabelUniqueDto) {
        return new ValidateDictionaryDataLabelUniqueBo(
                validateDictionaryDataLabelUniqueDto.getId(),
                validateDictionaryDataLabelUniqueDto.getDictionaryTypeCode(),
                List.of(validateDictionaryDataLabelUniqueDto.getLabel())
        );
    }

    /**
     * 从校验字典数据业务对象创建字典数据标签唯一性业务对象
     * 工厂方法，将校验字典数据业务对象转换为字典数据标签唯一性业务对象
     *
     * @param validateDictionaryDataBo 校验字典数据业务对象
     * @return 校验字典数据标签唯一性业务对象
     */
    public static ValidateDictionaryDataLabelUniqueBo of(ValidateDictionaryDataBo validateDictionaryDataBo) {
        List<String> labels = validateDictionaryDataBo.getTranslations().stream()
                .map(DictionaryDataTranslationBo::getLabel).toList();
        return new ValidateDictionaryDataLabelUniqueBo(
                validateDictionaryDataBo.getId(),
                validateDictionaryDataBo.getDictionaryTypeCode(),
                labels
        );
    }

}
