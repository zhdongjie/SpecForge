package org.eu.originalkeen.system.dictionary.data.domain.vo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.Date;

/**
 * 字典数据分页视图对象
 * 用于分页展示字典数据列表
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class DictionaryDataPageVo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 4340370560276841146L;

    /**
     * 字典数据ID
     * 字典数据的唯一标识
     */
    private Long id;

    /**
     * 字典类型代码
     * 关联的字典类型代码
     */
    private String dictionaryTypeCode;

    /**
     * 字典值
     * 字典数据的值
     */
    private String value;

    /**
     * 字典标签
     * 字典数据在当前语言下的显示标签
     */
    private String label;

    /**
     * 排序值
     * 字典数据的显示顺序，值越小越靠前
     */
    private Integer sort;

    /**
     * 备注信息
     * 字典数据的备注说明
     */
    private String remark;

    /**
     * 创建时间
     * 记录创建的时间
     */
    private Date createdTime;

} 
