package org.eu.originalkeen.system.dictionary.data.domain.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 校验字典数据标签唯一性数据传输对象
 * 用于校验字典数据标签是否已被使用
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ValidateDictionaryDataLabelUniqueDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 7985231728596586214L;

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
     * 字典标签
     * 字典数据在该语言下的显示标签
     */
    @NotBlank(message = "{form.dictionaryData.labelIsRequired}")
    private String label;

} 
