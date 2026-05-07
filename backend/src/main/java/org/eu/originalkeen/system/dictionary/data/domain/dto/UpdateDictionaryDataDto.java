package org.eu.originalkeen.system.dictionary.data.domain.dto;

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
 * 更新字典数据数据传输对象
 * 用于更新字典数据信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UpdateDictionaryDataDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 258879464386326905L;

    /**
     * 字典数据ID
     * 要更新的字典数据ID
     */
    @NotNull(message = "{form.common.idIsRequired}")
    private Long id;

    /**
     * 字典类型代码
     * 关联的字典类型代码
     */
    @NotBlank(message = "{form.dictionaryType.dictionaryTypeCodeIsRequired}")
    @Size(max = 64, message = "{form.dictionaryType.invalidDictionaryTypeCodeLength}")
    private String dictionaryTypeCode;

    /**
     * 字典值
     * 字典数据的值
     */
    @NotBlank(message = "{form.dictionaryData.valueIsRequired}")
    @Size(max = 32, message = "{form.dictionaryData.invalidValueLength}")
    private String value;

    /**
     * 排序值
     * 字典数据的显示顺序，值越小越靠前
     */
    @NotNull(message = "{form.common.sortIsRequired}")
    @Range(min = 1, max = 999, message = "{form.common.invalidSortSize}")
    private Integer sort;

    /**
     * 字典数据状态
     * 字典数据的状态，对应 system_dictionary_data_status 字典数据
     */
    @NotBlank(message = "{form.dictionaryData.dictionaryDataStatusIsRequired}")
    private String dictionaryDataStatus;

    /**
     * 字典数据翻译列表
     * 字典数据的多语言翻译信息
     */
    @NotEmpty(message = "{form.dictionaryData.dictionaryDataTranslationsIsRequired}")
    @Valid
    private List<DictionaryDataTranslationDto> translations;

} 
