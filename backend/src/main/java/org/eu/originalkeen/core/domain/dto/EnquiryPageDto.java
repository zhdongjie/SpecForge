package org.eu.originalkeen.core.domain.dto;

import org.eu.originalkeen.core.constant.SystemConstant;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.Objects;

/**
 * 查询分页数据传输对象
 * 用于分页查询的基础类，包含当前页和每页大小等分页参数
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode(callSuper = true)
public class EnquiryPageDto extends EnquiryConditionDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -6397628192072846639L;

    /**
     * 当前页码
     * 要获取的数据页码，从1开始
     */
    private Long currentPage;

    /**
     * 每页大小
     * 每页显示的数据条数
     */
    private Long pageSize;

    /**
     * 获取当前页码
     * 如果当前页码为空或小于1，则返回默认值
     *
     * @return 当前页码，最小为1
     */
    public Long getCurrentPage() {
        return (Objects.isNull(currentPage) || currentPage < 1)
                ? SystemConstant.DEFAULT_CURRENT_PAGE
                : currentPage;
    }

    /**
     * 获取每页大小
     * 如果每页大小为空或小于1，则返回默认值
     *
     * @return 每页大小，最小为1
     */
    public Long getPageSize() {
        return (Objects.isNull(pageSize) || pageSize < 1)
                ? SystemConstant.DEFAULT_PAGE_SIZE
                : pageSize;
    }

}
