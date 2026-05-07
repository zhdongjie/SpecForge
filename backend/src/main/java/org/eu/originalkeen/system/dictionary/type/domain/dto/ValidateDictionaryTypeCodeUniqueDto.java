package org.eu.originalkeen.system.dictionary.type.domain.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 校验字典类型代码唯一性数据传输对象
 * 用于接收校验字典类型代码唯一性的请求数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ValidateDictionaryTypeCodeUniqueDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -3366571693627389106L;

    /**
     * 字典类型ID
     * 当前字典类型ID，用于更新时排除自身
     */
    private Long id;

    /**
     * 字典类型代码
     * 要校验的字典类型代码
     */
    @NotBlank(message = "{form.dictionaryType.dictionaryTypeCodeIsRequired}")
    private String dictionaryTypeCode;

} 
