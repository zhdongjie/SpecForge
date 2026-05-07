package org.eu.originalkeen.core.domain.vo;

import org.eu.originalkeen.core.enums.ResponseCode;
import org.eu.originalkeen.core.utils.MessageUtils;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * 统一响应对象
 * 用于封装API响应的标准格式，包含状态码、消息、数据等
 *
 * @param <T> 响应数据的类型
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ResponseVo<T> {

    /**
     * 状态码
     * 响应的状态码
     */
    private Integer code;

    /**
     * 响应消息
     * 响应的描述信息
     */
    private String message;

    /**
     * 错误列表
     * 当发生校验错误时，包含具体的字段错误信息
     */
    private List<FieldErrorVo> errors;

    /**
     * 响应数据
     * 响应的业务数据内容
     */
    private T data;

    /**
     * 时间戳
     * 响应生成的时间戳，毫秒级
     */
    private Long timestamp;

    /**
     * 创建成功响应（无数据）
     * 创建一个成功的响应对象，不包含数据
     *
     * @param <T> 响应数据类型
     * @return 成功响应对象
     */
    public static <T> ResponseVo<T> success() {
        return success(null);
    }

    /**
     * 创建成功响应（带数据）
     * 创建一个成功的响应对象，包含指定的数据
     *
     * @param data 响应数据
     * @param <T>  响应数据类型
     * @return 成功响应对象
     */
    public static <T> ResponseVo<T> success(T data) {
        return instance(ResponseCode.SUCCESS.getValue(), MessageUtils.message("common.operationSuccessfully"), null, data);
    }

    /**
     * 创建失败响应（字段错误）
     * 创建一个包含字段错误信息的失败响应
     *
     * @param fieldErrors 字段错误列表
     * @param <T>         响应数据类型
     * @return 失败响应对象
     */
    public static <T> ResponseVo<T> fail(List<FieldErrorVo> fieldErrors) {
        return instance(ResponseCode.BAD_REQUEST.getValue(), null, fieldErrors, null);
    }

    /**
     * 创建失败响应（自定义消息）
     * 创建一个包含自定义错误消息的失败响应
     *
     * @param message 错误消息
     * @param <T>     响应数据类型
     * @return 失败响应对象
     */
    public static <T> ResponseVo<T> fail(String message) {
        return instance(ResponseCode.BAD_REQUEST.getValue(), message, null, null);
    }

    /**
     * 创建未授权响应
     * 创建一个表示用户未登录或未授权的响应
     *
     * @param <T> 响应数据类型
     * @return 未授权响应对象
     */
    public static <T> ResponseVo<T> unauthorized() {
        return instance(ResponseCode.UNAUTHORIZED.getValue(), MessageUtils.message("common.unauthorized"), null, null);
    }

    /**
     * 创建禁止访问响应
     * 创建一个表示用户没有权限访问资源的响应
     *
     * @param <T> 响应数据类型
     * @return 禁止访问响应对象
     */
    public static <T> ResponseVo<T> forbidden() {
        return instance(ResponseCode.FORBIDDEN.getValue(), MessageUtils.message("common.forbidden"), null, null);
    }

    /**
     * 创建服务器错误响应
     * 创建一个表示服务器内部错误的响应
     *
     * @param <T> 响应数据类型
     * @return 服务器错误响应对象
     */
    public static <T> ResponseVo<T> error() {
        return instance(ResponseCode.SERVER_ERROR.getValue(), MessageUtils.message("common.serverInternalError"), null, null);
    }

    /**
     * 创建响应实例
     * 创建一个带有指定参数的响应对象
     *
     * @param code        状态码
     * @param message     响应消息
     * @param fieldErrors 字段错误列表
     * @param data        响应数据
     * @param <T>         响应数据类型
     * @return 响应对象
     */
    private static <T> ResponseVo<T> instance(Integer code, String message, List<FieldErrorVo> fieldErrors, T data) {
        return new ResponseVo<>(code, message, fieldErrors, data, System.currentTimeMillis());
    }

}
