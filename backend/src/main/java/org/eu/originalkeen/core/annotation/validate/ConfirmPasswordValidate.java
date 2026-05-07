package org.eu.originalkeen.core.annotation.validate;

import org.eu.originalkeen.core.annotation.validate.validator.ConfirmPasswordValidator;
import jakarta.validation.Constraint;
import jakarta.validation.Payload;

import java.lang.annotation.*;

/**
 * 密码确认校验注解
 * 用于校验密码和确认密码是否一致，应用于实现PasswordMatches接口的类
 */
@Documented
@Constraint(validatedBy = ConfirmPasswordValidator.class)
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
public @interface ConfirmPasswordValidate {

    /**
     * 密码字段名
     * 指定包含密码的字段名，默认为"password"
     *
     * @return 密码字段名
     */
    String passwordField() default "password";

    /**
     * 确认密码字段名
     * 指定包含确认密码的字段名，默认为"confirmPassword"
     *
     * @return 确认密码字段名
     */
    String confirmPasswordField() default "confirmPassword";

    /**
     * 校验失败时的错误消息
     * 默认为国际化消息键"{authorize.register.enteredPasswordsDiffer}"
     *
     * @return 错误消息
     */
    String message() default "{authorize.register.enteredPasswordsDiffer}";

    /**
     * 校验分组
     * 用于指定校验应该应用的校验组
     *
     * @return 校验组数组
     */
    Class<?>[] groups() default {};

    /**
     * 校验负载
     * 用于携带校验时的元数据
     *
     * @return 负载数组
     */
    Class<? extends Payload>[] payload() default {};

}
