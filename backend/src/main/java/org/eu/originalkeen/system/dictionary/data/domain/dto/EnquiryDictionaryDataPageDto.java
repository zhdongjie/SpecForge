package org.eu.originalkeen.system.dictionary.data.domain.dto;

import org.eu.originalkeen.core.domain.dto.EnquiryPageDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

import java.io.Serial;

/**
 * 查询字典数据分页数据传输对象
 * 用于分页查询字典数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode(callSuper = true)
public class EnquiryDictionaryDataPageDto extends EnquiryPageDto {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -8261648690369903951L;

    /**
     * 字典类型代码
     * 用于筛选特定字典类型的数据
     */
    private String dictionaryTypeCode;

    /**
     * 字典值
     * 用于筛选特定值的字典数据
     */
    private String value;

    /**
     * 字典标签
     * 用于筛选特定标签的字典数据
     */
    private String label;

} 
