package org.eu.originalkeen.system.dictionary.type.domain.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.validator.constraints.Range;

import java.io.Serial;
import java.io.Serializable;
import java.util.List;

/**
 * 创建字典类型数据传输对象
 * 用于接收和校验创建字典类型的请求数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class CreateDictionaryTypeDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -3417616781581046931L;

    /**
     * 字典类型代码
     * 字典类型的唯一代码标识
     */
    @NotBlank(message = "{form.dictionaryType.dictionaryTypeCodeIsRequired}")
    @Size(max = 64, message = "{form.dictionaryType.invalidDictionaryTypeCodeLength}")
    private String dictionaryTypeCode;

    /**
     * 字典类型状态
     * 字典类型的状态，对应 system_dictionary_type_status 字典数据
     */
    @NotBlank(message = "{form.dictionaryType.dictionaryTypeStatusIsRequired}")
    private String dictionaryTypeStatus;

    /**
     * 排序值
     * 字典类型的显示顺序，范围1-999
     */
    @NotNull(message = "{form.common.sortIsRequired}")
    @Range(min = 1, max = 999, message = "{form.common.invalidSortSize}")
    private Integer sort;

    /**
     * 字典类型翻译列表
     * 字典类型的多语言翻译信息
     */
    @Valid
    @NotEmpty(message = "{form.dictionaryType.dictionaryTypeTranslationsIsRequired}")
    private List<DictionaryTypeTranslationDto> translations;

} 
