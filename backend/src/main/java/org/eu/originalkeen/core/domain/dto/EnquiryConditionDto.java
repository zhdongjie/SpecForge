package org.eu.originalkeen.core.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;

import java.io.Serial;
import java.io.Serializable;
import java.util.Date;
import java.util.List;

/**
 * 查询条件数据传输对象
 * 用于查询的基础类，包含时间范围和排序等通用查询条件
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class EnquiryConditionDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 5740222121914403598L;

    /**
     * 创建时间起始值
     * 查询创建时间范围的起始时间
     */
    @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private Date createdTimeStart;

    /**
     * 创建时间结束值
     * 查询创建时间范围的结束时间
     */
    @DateTimeFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    private Date createdTimeEnd;

    /**
     * 排序条件列表
     * 查询结果的排序条件
     */
    private List<OrderDto> orders;

}
