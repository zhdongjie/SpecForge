package org.eu.originalkeen.core.domain.vo;

import com.mybatisflex.core.paginate.Page;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 分页视图对象
 * 用于封装分页查询的结果，包含总数量和数据项列表
 *
 * @param <T> 数据项类型
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PageVo<T> {

    /**
     * 总数量
     * 符合查询条件的数据总条数
     */
    private Long total;

    /**
     * 数据项列表
     * 当前页的数据项列表
     */
    private List<T> items;

    /**
     * 从分页对象创建分页视图对象
     * 将MyBatisFlex的Page对象转换为PageVo对象
     *
     * @param page MyBatisFlex的分页对象
     * @param <T>  数据项类型
     * @return 分页视图对象
     */
    public static <T> PageVo<T> of(Page<T> page) {
        return new PageVo<>(page.getTotalRow(), page.getRecords());
    }

}
