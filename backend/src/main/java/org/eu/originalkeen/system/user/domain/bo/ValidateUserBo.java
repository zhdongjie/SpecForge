package org.eu.originalkeen.system.user.domain.bo;

import org.eu.originalkeen.system.user.domain.dto.CreateUserDto;
import org.eu.originalkeen.system.user.domain.dto.UpdateUserDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 校验用户业务对象
 * 用于在业务层校验用户的各种属性
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ValidateUserBo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -1562361087830040394L;

    /**
     * 用户ID
     * 用户的唯一标识，更新时使用
     */
    private Long id;

    /**
     * 用户名
     * 用户的登录名，需要校验唯一性
     */
    private String username;

    /**
     * 从创建用户DTO创建校验用户业务对象
     * 工厂方法，将创建用户DTO转换为校验用户业务对象
     *
     * @param createUserDto 创建用户DTO
     * @return 校验用户业务对象
     */
    public static ValidateUserBo of(CreateUserDto createUserDto) {
        return new ValidateUserBo(
                null,
                createUserDto.getUsername()
        );
    }

    /**
     * 从更新用户DTO创建校验用户业务对象
     * 工厂方法，将更新用户DTO转换为校验用户业务对象
     *
     * @param updateUserDto 更新用户DTO
     * @return 校验用户业务对象
     */
    public static ValidateUserBo of(UpdateUserDto updateUserDto) {
        return new ValidateUserBo(
                updateUserDto.getId(),
                updateUserDto.getUsername()
        );
    }

}
