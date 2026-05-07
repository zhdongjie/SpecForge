package org.eu.originalkeen.system.dictionary.type.domain.dto;

import org.eu.originalkeen.core.domain.dto.EnquiryPageDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 查询字典类型分页数据传输对象
 * 用于接收和校验查询字典类型分页的请求数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode(callSuper = true)
public class EnquiryDictionaryTypePageDto extends EnquiryPageDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -1302024428921120292L;

    /**
     * 字典类型名称
     * 按照字典类型名称进行模糊查询
     */
    private String dictionaryTypeName;

    /**
     * 字典类型状态
     * 按照字典类型状态进行查询，对应 system_dictionary_type_status 字典数据
     */
    private String dictionaryTypeStatus;

} 
