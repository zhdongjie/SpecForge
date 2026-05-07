package org.eu.originalkeen.system.dictionary.type.domain.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 校验字典类型名称唯一性数据传输对象
 * 用于接收校验字典类型名称唯一性的请求数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ValidateDictionaryTypeNameUniqueDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -5391830781353622453L;

    /**
     * 字典类型ID
     * 当前字典类型ID，用于更新时排除自身
     */
    private Long id;

    /**
     * 字典类型名称
     * 要校验的字典类型名称
     */
    @NotBlank(message = "{form.dictionaryType.dictionaryTypeNameIsRequired}")
    private String dictionaryTypeName;

} 
