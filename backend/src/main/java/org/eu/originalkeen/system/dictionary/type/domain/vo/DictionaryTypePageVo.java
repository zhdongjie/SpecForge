package org.eu.originalkeen.system.dictionary.type.domain.vo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 字典类型分页视图对象
 * 用于返回字典类型分页数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class DictionaryTypePageVo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 586029543156113663L;

    /**
     * 字典类型ID
     * 字典类型的唯一标识
     */
    private Long id;

    /**
     * 字典类型名称
     * 字典类型的名称
     */
    private String dictionaryTypeName;

    /**
     * 字典类型代码
     * 字典类型的唯一代码标识
     */
    private String dictionaryTypeCode;

    /**
     * 排序值
     * 字典类型的显示顺序，值越小越靠前
     */
    private Integer sort;

    /**
     * 字典类型状态
     * 字典类型的状态，对应 system_dictionary_type_status 字典数据
     */
    private String dictionaryTypeStatus;

    /**
     * 备注信息
     * 字典类型的备注说明
     */
    private String remark;

} 
