package org.eu.originalkeen.system.user.domain.entity;

import com.mybatisflex.annotation.Table;
import org.eu.originalkeen.core.domain.Audit;
import org.eu.originalkeen.core.domain.entity.PrimaryKeyEntity;
import org.eu.originalkeen.system.user.domain.dto.CreateUserDto;
import org.eu.originalkeen.system.user.domain.dto.UpdateUserDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.Date;

/**
 * 用户实体类
 * 对应数据库中的system_user表，存储用户基本信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Table("system_user")
@EqualsAndHashCode(callSuper = true)
public class UserEntity extends PrimaryKeyEntity implements Serializable, Audit {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 7939803179768627048L;

    /**
     * 用户名
     * 用户的登录账号，必须唯一
     */
    private String username;

    /**
     * 加密密码
     * 用户的登录密码，已经过加密处理
     */
    private String encodedPassword;

    /**
     * 创建时间
     * 记录创建的时间
     */
    private Date createdTime;

    /**
     * 创建人
     * 记录创建人的用户ID
     */
    private Long createdBy;

    /**
     * 最后修改时间
     * 记录最后一次修改的时间
     */
    private Date lastModifiedTime;

    /**
     * 最后修改人
     * 记录最后一次修改人的用户ID
     */
    private Long lastModifiedBy;

    /**
     * 从创建用户DTO创建用户实体
     * 将用户创建数据转换为实体对象
     *
     * @param createUserDto   创建用户DTO
     * @param encodedPassword 已加密的密码
     * @return 用户实体对象
     */
    public static UserEntity of(CreateUserDto createUserDto, String encodedPassword) {
        return new UserEntity(
                createUserDto.getUsername(),
                encodedPassword,
                null,
                null,
                null,
                null
        );
    }

    /**
     * 从更新用户DTO创建用户实体
     * 将用户更新数据转换为实体对象
     *
     * @param updateUserDto 更新用户DTO
     * @return 用户实体对象
     */
    public static UserEntity of(UpdateUserDto updateUserDto) {
        return new UserEntity(
                updateUserDto.getUsername(),
                null,
                null,
                null,
                null,
                null
        );
    }

}
