package org.eu.originalkeen.system.user.domain.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 校验用户名唯一性数据传输对象
 * 用于接收校验用户名唯一性的请求数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ValidateUsernameUniqueDto implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -1031564570976654302L;

    /**
     * 用户ID
     * 当前用户ID，用于更新时排除自身
     */
    private Long id;

    /**
     * 用户名
     * 要校验的用户名
     */
    @NotBlank(message = "{form.user.usernameIsRequired}")
    private String username;

}
