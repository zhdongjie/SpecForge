package org.eu.originalkeen.system.user.domain.dto;

import org.eu.originalkeen.core.domain.dto.EnquiryPageDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.Set;

/**
 * 查询用户分页数据传输对象
 * 用于接收用户分页查询的条件参数
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode(callSuper = true)
public class EnquiryUserPageDto extends EnquiryPageDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 459173451321562880L;

    /**
     * 用户名
     * 按照用户名进行模糊查询
     */
    private String username;

    /**
     * 角色ID列表
     * 按照角色列表进行查询
     */
    private Set<Long> roleIds;

}
