package org.eu.originalkeen.system.user.domain.vo;

import com.mybatisflex.annotation.RelationOneToMany;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.Set;

/**
 * 用户详情视图对象
 * 用于返回用户详细信息的数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserDetailsVo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 8041716895258297800L;

    /**
     * 用户ID
     * 用户的唯一标识
     */
    private Long id;

    /**
     * 用户名
     * 用户的登录账号
     */
    private String username;

    /**
     * 角色ID列表
     * 用户关联的角色ID列表
     */
    @RelationOneToMany(
            selfField = "id",
            targetTable = "system_user_role",
            targetField = "userId",
            valueField = "roleId"
    )
    private Set<Long> roleIds;

}
