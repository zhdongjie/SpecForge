package org.eu.originalkeen.core.utils;

import org.eu.originalkeen.core.enums.ContentType;
import jakarta.servlet.ServletRequest;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.web.context.request.RequestAttributes;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

import java.io.IOException;
import java.nio.charset.Charset;
import java.util.*;

/**
 * Servlet工具类
 * 提供处理HTTP请求和响应的工具方法
 */
public class ServletUtils {

    /**
     * 获取当前请求属性
     * 从当前线程上下文中获取请求属性
     *
     * @return 当前请求的ServletRequestAttributes对象
     * @throws IllegalStateException 如果当前线程不在Web请求上下文中则抛出异常
     */
    public static ServletRequestAttributes getRequestAttributes() {
        RequestAttributes attributes = RequestContextHolder.getRequestAttributes();
        if (Objects.isNull(attributes)) {
            throw new IllegalStateException("Request attributes are not available. Ensure that the request is being processed in a servlet context.");
        }
        return (ServletRequestAttributes) attributes;
    }

    /**
     * 获取当前响应对象
     * 从当前请求属性中获取响应对象
     *
     * @return 当前的HttpServletResponse对象
     * @throws IllegalStateException 如果当前线程不在Web请求上下文中则抛出异常
     */
    public static HttpServletResponse getResponse() {
        return getRequestAttributes().getResponse();
    }

    /**
     * 获取当前请求对象
     * 从当前请求属性中获取请求对象
     *
     * @return 当前的HttpServletRequest对象
     * @throws IllegalStateException 如果当前线程不在Web请求上下文中则抛出异常
     */
    public static HttpServletRequest getRequest() {
        return getRequestAttributes().getRequest();
    }

    /**
     * 获取请求参数映射
     * 将请求参数转换为Map<String, List<String>>格式
     *
     * @param request 请求对象
     * @return 参数名到参数值列表的映射
     */
    public static Map<String, List<String>> getParamMap(ServletRequest request) {
        Map<String, List<String>> params = new HashMap<>();
        for (Map.Entry<String, String[]> entry : getParams(request).entrySet()) {
            params.put(entry.getKey(), Arrays.asList(entry.getValue()));
        }
        return params;
    }

    /**
     * 获取请求参数
     * 获取请求的原始参数映射
     *
     * @param request 请求对象
     * @return 不可变的参数名到参数值数组的映射
     */
    public static Map<String, String[]> getParams(ServletRequest request) {
        Map<String, String[]> map = request.getParameterMap();
        return Collections.unmodifiableMap(map);
    }

    /**
     * 写入响应内容
     * 将结果字符串写入HTTP响应
     *
     * @param response    HTTP响应对象
     * @param result      要写入的结果字符串
     * @param contentType 内容类型，如JSON或HTML
     * @param charset     字符集
     * @throws IOException 如果写入过程中发生错误则抛出异常
     */
    public static void write(
            HttpServletResponse response,
            String result,
            ContentType contentType,
            Charset charset
    ) throws IOException {
        response.setCharacterEncoding(charset.name());
        response.setContentType(Objects.nonNull(contentType) ? contentType.getValue() : ContentType.JSON.getValue());
        response.getWriter().write(result);
    }

    /**
     * 私有构造函数
     * 防止实例化工具类
     */
    private ServletUtils() {
    }

}
