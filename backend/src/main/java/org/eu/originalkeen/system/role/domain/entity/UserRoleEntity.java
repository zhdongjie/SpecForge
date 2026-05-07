package org.eu.originalkeen.system.role.domain.entity;

import com.mybatisflex.annotation.Id;
import com.mybatisflex.annotation.Table;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 用户角色关系实体类
 * 对应数据库中system_user_role表，存储用户和角色的关联关系
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Table("system_user_role")
public class UserRoleEntity implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -4130660604058176171L;

    /**
     * 用户ID
     * 用户的唯一标识，为联合主键的一部分
     */
    @Id
    private Long userId;

    /**
     * 角色ID
     * 角色的唯一标识，为联合主键的一部分
     */
    @Id
    private Long roleId;

    /**
     * 创建UserRoleEntity实例
     * 工厂方法，用于创建用户角色关系实体
     *
     * @param userId 用户ID
     * @param roleId 角色ID
     * @return UserRoleEntity实例
     */
    public static UserRoleEntity of(Long userId, Long roleId) {
        return new UserRoleEntity(userId, roleId);
    }

}
