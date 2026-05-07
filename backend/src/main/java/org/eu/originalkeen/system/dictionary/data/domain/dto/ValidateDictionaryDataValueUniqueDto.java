package org.eu.originalkeen.system.dictionary.data.domain.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 校验字典数据值唯一性数据传输对象
 * 用于校验字典数据值是否已被使用
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ValidateDictionaryDataValueUniqueDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -739752563988908976L;

    /**
     * 字典数据ID
     * 当前字典数据ID，更新时使用，新增时可为空
     */
    private Long id;

    /**
     * 字典类型代码
     * 字典类型的唯一代码标识
     */
    @NotBlank(message = "{form.dictionaryType.dictionaryTypeCodeIsRequired}")
    private String dictionaryTypeCode;

    /**
     * 字典值
     * 字典数据的值
     */
    @NotBlank(message = "{form.dictionaryData.valueIsRequired}")
    private String value;

} 
