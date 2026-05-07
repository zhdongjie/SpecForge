package org.eu.originalkeen.system.user.domain.bo;

import org.eu.originalkeen.system.user.domain.dto.ValidateUsernameUniqueDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.List;

/**
 * 校验用户名唯一性业务对象
 * 用于在业务层校验用户名的唯一性
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ValidateUsernameUniqueBo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -5223404473656418018L;

    /**
     * 用户ID
     * 用户的唯一标识，用于在校验唯一性时排除自身
     */
    private Long id;

    /**
     * 用户名
     * 需要校验唯一性的用户名
     */
    private List<String> usernames;

    /**
     * 从用户名唯一性DTO创建业务对象
     * 工厂方法，将DTO转换为业务对象
     *
     * @param validateUsernameUniqueDto 用户名唯一性DTO
     * @return 校验用户名唯一性业务对象
     */
    public static ValidateUsernameUniqueBo of(ValidateUsernameUniqueDto validateUsernameUniqueDto) {
        return new ValidateUsernameUniqueBo(
                validateUsernameUniqueDto.getId(),
                List.of(validateUsernameUniqueDto.getUsername())
        );
    }

    /**
     * 从校验用户业务对象创建用户名唯一性业务对象
     * 工厂方法，将校验用户业务对象转换为用户名唯一性业务对象
     *
     * @param validateUserBo 校验用户业务对象
     * @return 校验用户名唯一性业务对象
     */
    public static ValidateUsernameUniqueBo of(ValidateUserBo validateUserBo) {
        return new ValidateUsernameUniqueBo(
                validateUserBo.getId(),
                List.of(validateUserBo.getUsername())
        );
    }

    /**
     * 从用户名列表创建用户名唯一性业务对象
     * 工厂方法，基于用户名列表创建校验对象
     *
     * @param usernames 需要校验唯一性的用户名列表
     * @return 校验用户名唯一性业务对象
     */
    public static ValidateUsernameUniqueBo of(List<String> usernames) {
        return new ValidateUsernameUniqueBo(
                null,
                usernames
        );
    }

}
