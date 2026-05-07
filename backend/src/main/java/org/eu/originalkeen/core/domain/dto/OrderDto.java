package org.eu.originalkeen.core.domain.dto;

import jakarta.validation.constraints.Pattern;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.apache.commons.lang3.StringUtils;

import java.io.Serial;
import java.io.Serializable;

/**
 * 排序条件数据传输对象
 * 用于指定查询结果的排序字段和排序方式
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class OrderDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -7118691849379169862L;

    /**
     * 排序字段
     * 指定排序的字段名称
     */
    private String key;

    /**
     * 是否升序
     * 排序方式，asc表示升序，desc表示降序，默认为升序
     */
    @Pattern(regexp = "^(?i)(asc|desc)$", message = "{form.common.invalidSortOrder}")
    private String order = "asc";

    /**
     * 判断排序方式
     * 判断当前排序方向是否为升序（ASC）
     * <p>
     * 根据 order 字段值进行判断（不区分大小写）：
     * - 当值为 "asc" 时返回 true
     * - 其他情况（包括 "desc"）均返回 false
     * </p>
     *
     * @return true 表示升序排序，false 表示降序排序
     */
    public boolean isAsc() {
        return StringUtils.equalsIgnoreCase(order, "asc");
    }

}
