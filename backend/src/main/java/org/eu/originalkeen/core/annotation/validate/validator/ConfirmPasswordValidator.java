package org.eu.originalkeen.core.annotation.validate.validator;

import org.eu.originalkeen.core.annotation.validate.ConfirmPasswordValidate;
import org.eu.originalkeen.core.utils.ReflectionUtils;
import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;

/**
 * 密码匹配校验器
 * 用于校验密码和确认密码是否一致
 */
@Slf4j
public class ConfirmPasswordValidator implements ConstraintValidator<ConfirmPasswordValidate, Object> {

    /**
     * 密码字段名
     * 指定包含密码的字段名
     */
    private String passwordField;

    /**
     * 确认密码字段名
     * 指定包含确认密码的字段名
     */
    private String confirmPasswordField;

    /**
     * 初始化方法
     * 从注解中获取密码字段和确认密码字段的名称
     *
     * @param constraintAnnotation 校验注解
     */
    @Override
    public void initialize(ConfirmPasswordValidate constraintAnnotation) {
        this.passwordField = constraintAnnotation.passwordField();
        this.confirmPasswordField = constraintAnnotation.confirmPasswordField();
    }

    /**
     * 校验方法
     * 校验密码和确认密码是否一致
     *
     * @param object  要校验的对象
     * @param context 校验器上下文
     * @return 如果密码和确认密码一致返回true，否则返回false
     */
    @Override
    public boolean isValid(Object object, ConstraintValidatorContext context) {
        context.buildConstraintViolationWithTemplate(context.getDefaultConstraintMessageTemplate())
                .addPropertyNode("confirmPassword")
                .addConstraintViolation();

        String password = (String) ReflectionUtils.getFieldValueSafely(object, passwordField);
        String confirmPassword = (String) ReflectionUtils.getFieldValueSafely(object, confirmPasswordField);

        if (StringUtils.isNotEmpty(password) && StringUtils.isNotEmpty(confirmPassword)) {
            return StringUtils.equals(password, confirmPassword);
        }

        return true;
    }

}
