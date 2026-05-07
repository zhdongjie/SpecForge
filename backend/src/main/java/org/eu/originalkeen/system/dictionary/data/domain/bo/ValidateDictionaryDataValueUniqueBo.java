package org.eu.originalkeen.system.dictionary.data.domain.bo;

import org.eu.originalkeen.system.dictionary.data.domain.dto.ValidateDictionaryDataValueUniqueDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 校验字典数据值唯一性业务对象
 * 用于在业务层校验字典数据值的唯一性
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ValidateDictionaryDataValueUniqueBo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -3850421418905481084L;

    /**
     * 字典数据ID
     * 字典数据的唯一标识，用于在校验唯一性时排除自身
     */
    private Long id;

    /**
     * 字典类型代码
     * 字典类型的唯一代码标识，用于确定字典数据所属的字典类型
     */
    private String dictionaryTypeCode;

    /**
     * 字典值
     * 需要校验唯一性的字典数据值
     */
    private String value;

    /**
     * 从字典数据值唯一性DTO创建业务对象
     * 工厂方法，将DTO转换为业务对象
     *
     * @param validateDictionaryDataValueUniqueDto 字典数据值唯一性DTO
     * @return 校验字典数据值唯一性业务对象
     */
    public static ValidateDictionaryDataValueUniqueBo of(ValidateDictionaryDataValueUniqueDto validateDictionaryDataValueUniqueDto) {
        return new ValidateDictionaryDataValueUniqueBo(
                validateDictionaryDataValueUniqueDto.getId(),
                validateDictionaryDataValueUniqueDto.getDictionaryTypeCode(),
                validateDictionaryDataValueUniqueDto.getValue()
        );
    }

    /**
     * 从校验字典数据业务对象创建字典数据值唯一性业务对象
     * 工厂方法，将校验字典数据业务对象转换为字典数据值唯一性业务对象
     *
     * @param validateDictionaryDataBo 校验字典数据业务对象
     * @return 校验字典数据值唯一性业务对象
     */
    public static ValidateDictionaryDataValueUniqueBo of(ValidateDictionaryDataBo validateDictionaryDataBo) {
        return new ValidateDictionaryDataValueUniqueBo(
                validateDictionaryDataBo.getId(),
                validateDictionaryDataBo.getDictionaryTypeCode(),
                validateDictionaryDataBo.getValue()
        );
    }

}
