package org.eu.originalkeen.system.user.domain.vo;

import com.mybatisflex.annotation.RelationManyToMany;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.Date;
import java.util.List;

/**
 * 用户分页视图对象
 * 用于返回用户分页列表数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserPageVo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -2651746861575968883L;

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
     * 角色列表
     * 用户关联的角色名称列表
     */
    @RelationManyToMany(
            selfField = "id",
            targetTable = "system_role_translation",
            targetField = "roleId",
            valueField = "roleName",
            joinTable = "system_user_role",
            joinSelfColumn = "user_id",
            joinTargetColumn = "role_id",
            extraCondition = "language_code = :languageCode"
    )
    private List<String> roles;

    /**
     * 创建时间
     * 用户账号的创建时间
     */
    private Date createdTime;

}
