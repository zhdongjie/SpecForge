package org.eu.originalkeen.system.dictionary.type.domain.bo;

import org.eu.originalkeen.system.dictionary.type.domain.dto.ValidateDictionaryTypeCodeUniqueDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 校验字典类型代码唯一性业务对象
 * 用于在业务层校验字典类型代码的唯一性
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ValidateDictionaryTypeCodeUniqueBo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -3401266406617187066L;

    /**
     * 字典类型ID
     * 字典类型的唯一标识，用于在校验唯一性时排除自身
     */
    private Long id;

    /**
     * 字典类型代码
     * 需要校验唯一性的字典类型代码
     */
    private String dictionaryTypeCode;

    /**
     * 从字典类型代码唯一性DTO创建业务对象
     * 工厂方法，将DTO转换为业务对象
     *
     * @param validateDictionaryTypeCodeUniqueDto 字典类型代码唯一性DTO
     * @return 校验字典类型代码唯一性业务对象
     */
    public static ValidateDictionaryTypeCodeUniqueBo of(ValidateDictionaryTypeCodeUniqueDto validateDictionaryTypeCodeUniqueDto) {
        return new ValidateDictionaryTypeCodeUniqueBo(
                validateDictionaryTypeCodeUniqueDto.getId(),
                validateDictionaryTypeCodeUniqueDto.getDictionaryTypeCode()
        );
    }

    /**
     * 从校验字典类型业务对象创建字典类型代码唯一性业务对象
     * 工厂方法，将校验字典类型业务对象转换为字典类型代码唯一性业务对象
     *
     * @param validateDictionaryTypeBo 校验字典类型业务对象
     * @return 校验字典类型代码唯一性业务对象
     */
    public static ValidateDictionaryTypeCodeUniqueBo of(ValidateDictionaryTypeBo validateDictionaryTypeBo) {
        return new ValidateDictionaryTypeCodeUniqueBo(
                validateDictionaryTypeBo.getId(),
                validateDictionaryTypeBo.getDictionaryTypeCode()
        );
    }

} 
