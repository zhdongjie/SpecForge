package org.eu.originalkeen.system.dictionary.type.domain.bo;

import org.eu.originalkeen.system.dictionary.type.domain.dto.ValidateDictionaryTypeNameUniqueDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.List;

/**
 * 校验字典类型名称唯一性业务对象
 * 用于在业务层校验字典类型名称的唯一性
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ValidateDictionaryTypeNameUniqueBo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -5519670520502739698L;

    /**
     * 字典类型ID
     * 字典类型的唯一标识，用于在校验唯一性时排除自身
     */
    private Long id;

    /**
     * 字典类型名称列表
     * 需要校验唯一性的字典类型名称列表
     */
    private List<String> dictionaryTypeNames;

    /**
     * 从字典类型名称唯一性DTO创建业务对象
     * 工厂方法，将DTO转换为业务对象
     *
     * @param validateDictionaryTypeNameUniqueDto 字典类型名称唯一性DTO
     * @return 校验字典类型名称唯一性业务对象
     */
    public static ValidateDictionaryTypeNameUniqueBo of(ValidateDictionaryTypeNameUniqueDto validateDictionaryTypeNameUniqueDto) {
        return new ValidateDictionaryTypeNameUniqueBo(
                validateDictionaryTypeNameUniqueDto.getId(),
                List.of(validateDictionaryTypeNameUniqueDto.getDictionaryTypeName())
        );
    }

    /**
     * 从校验字典类型业务对象创建字典类型名称唯一性业务对象
     * 工厂方法，将校验字典类型业务对象转换为字典类型名称唯一性业务对象
     *
     * @param validateDictionaryTypeBo 校验字典类型业务对象
     * @return 校验字典类型名称唯一性业务对象
     */
    public static ValidateDictionaryTypeNameUniqueBo of(ValidateDictionaryTypeBo validateDictionaryTypeBo) {
        List<String> dictionaryTypeNames = validateDictionaryTypeBo.getTranslations().stream()
                .map(DictionaryTypeTranslationBo::getDictionaryTypeName).toList();
        return new ValidateDictionaryTypeNameUniqueBo(
                validateDictionaryTypeBo.getId(),
                dictionaryTypeNames
        );
    }

}
