package org.eu.originalkeen.core.utils;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.eu.originalkeen.core.exception.system.HttpRequestException;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.collections4.MapUtils;
import org.apache.commons.lang3.StringUtils;

import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.stream.Collectors;

/**
 * HTTP请求工具类
 * 提供发送HTTP GET和POST请求的工具方法，支持JSON和表单数据
 */
@Slf4j
public class HttpUtils {

    /**
     * HTTP客户端
     * 用于发送HTTP请求的客户端实例
     */
    private static final HttpClient httpClient = HttpClient.newHttpClient();

    /**
     * 发送GET请求
     * 发送简单的GET请求，无参数和自定义头
     *
     * @param url 请求URL
     * @return 响应内容字符串
     */
    public static String sendGet(String url) {
        return sendGet(url, null, null);
    }

    /**
     * 发送GET请求带参数
     * 发送带查询参数的GET请求
     *
     * @param url    请求URL
     * @param params 查询参数映射
     * @return 响应内容字符串
     */
    public static String sendGet(String url, Map<String, Object> params) {
        return sendGet(url, params, null);
    }

    /**
     * 发送GET请求带参数和头
     * 发送带查询参数和自定义头的GET请求
     *
     * @param url     请求URL
     * @param params  查询参数映射
     * @param headers 自定义头映射
     * @return 响应内容字符串
     * @throws HttpRequestException 如果请求发生错误则抛出异常
     */
    public static String sendGet(String url, Map<String, Object> params, Map<String, String> headers) {
        try {
            url = prepareUrlWithQueryParams(url, params);
            HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
                    .uri(URI.create(url))
                    .GET();

            setCustomHeader(headers, requestBuilder);

            HttpRequest request = requestBuilder.build();

            log.info("Sending GET request to: {}", url);

            CompletableFuture<HttpResponse<String>> response = httpClient.sendAsync(request, HttpResponse.BodyHandlers.ofString());
            return response.get().body();
        } catch (ExecutionException | InterruptedException exception) {
            log.error("Error sending GET request to: {}", url, exception);
            Thread.currentThread().interrupt();
            throw new HttpRequestException(exception.getMessage(), exception);
        }
    }

    /**
     * 发送POST JSON请求
     * 发送简单的POST请求，无数据和自定义头
     *
     * @param url 请求URL
     * @return 响应内容字符串
     */
    public static String sendPostJson(String url) {
        return sendPostJson(url, null, null);
    }

    /**
     * 发送POST JSON请求带数据
     * 发送带JSON数据的POST请求
     *
     * @param url  请求URL
     * @param data JSON数据映射
     * @return 响应内容字符串
     */
    public static String sendPostJson(String url, Map<String, Object> data) {
        return sendPostJson(url, data, null);
    }

    /**
     * 发送POST JSON请求带数据和头
     * 发送带JSON数据和自定义头的POST请求
     *
     * @param url     请求URL
     * @param data    JSON数据映射
     * @param headers 自定义头映射
     * @return 响应内容字符串
     * @throws HttpRequestException 如果请求发生错误或JSON序列化失败则抛出异常
     */
    public static String sendPostJson(String url, Map<String, Object> data, Map<String, String> headers) {
        try {
            ObjectMapper objectMapper = new ObjectMapper();
            HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
                    .uri(URI.create(url))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(objectMapper.writeValueAsString(data), StandardCharsets.UTF_8));

            setCustomHeader(headers, requestBuilder);

            HttpRequest request = requestBuilder.build();

            log.info("Sending POST JSON request to: {} with data: {}", url, data);

            CompletableFuture<HttpResponse<String>> response = httpClient.sendAsync(request, HttpResponse.BodyHandlers.ofString());
            return response.get().body();
        } catch (ExecutionException | InterruptedException exception) {
            log.error("Error sending POST JSON request to: {}", url, exception);
            Thread.currentThread().interrupt();
            throw new HttpRequestException(exception.getMessage(), exception);
        } catch (JsonProcessingException exception) {
            log.error("Error serializing data to JSON: {}", data, exception);
            throw new HttpRequestException(exception.getMessage(), exception);
        }
    }

    /**
     * 发送POST表单请求
     * 发送简单的POST表单请求，无数据和自定义头
     *
     * @param url 请求URL
     * @return 响应内容字符串
     */
    public static String sendPostForm(String url) {
        return sendPostForm(url, null, null);
    }

    /**
     * 发送POST表单请求带数据
     * 发送带表单数据的POST请求
     *
     * @param url      请求URL
     * @param formData 表单数据映射
     * @return 响应内容字符串
     */
    public static String sendPostForm(String url, Map<String, Object> formData) {
        return sendPostForm(url, formData, null);
    }

    /**
     * 发送POST表单请求带数据和头
     * 发送带表单数据和自定义头的POST请求
     *
     * @param url      请求URL
     * @param formData 表单数据映射
     * @param headers  自定义头映射
     * @return 响应内容字符串
     * @throws HttpRequestException 如果请求发生错误则抛出异常
     */
    public static String sendPostForm(String url, Map<String, Object> formData, Map<String, String> headers) {
        try {
            String formDataString = StringUtils.EMPTY;
            if (MapUtils.isNotEmpty(formData)) {
                formDataString = formData.entrySet().stream()
                        .map(entry -> URLEncoder.encode(entry.getKey(), StandardCharsets.UTF_8) + "=" +
                                URLEncoder.encode(String.valueOf(entry.getValue()), StandardCharsets.UTF_8))
                        .collect(Collectors.joining("&"));
            }

            HttpRequest.Builder requestBuilder = HttpRequest.newBuilder()
                    .uri(URI.create(url))
                    .header("Content-Type", "application/x-www-form-urlencoded")
                    .POST(HttpRequest.BodyPublishers.ofString(formDataString));

            setCustomHeader(headers, requestBuilder);

            HttpRequest request = requestBuilder.build();

            log.info("Sending POST form request to: {} with data: {}", url, formData);

            CompletableFuture<HttpResponse<String>> response = httpClient.sendAsync(request, HttpResponse.BodyHandlers.ofString());
            return response.get().body();
        } catch (ExecutionException | InterruptedException exception) {
            log.error("Error sending POST form request to: {}", url, exception);
            Thread.currentThread().interrupt();
            throw new HttpRequestException(exception.getMessage(), exception);
        }
    }

    /**
     * 准备带查询参数的URL
     * 将查询参数添加到URL中
     *
     * @param url    原始URL
     * @param params 查询参数映射
     * @return 带查询参数的完整URL
     * @throws IllegalArgumentException 如果URL为空则抛出异常
     */
    public static String prepareUrlWithQueryParams(String url, Map<String, Object> params) {
        if (MapUtils.isEmpty(params)) {
            return url;
        }

        if (StringUtils.isEmpty(url)) {
            throw new IllegalArgumentException("URL cannot be blank or null");
        }

        String queryString = getParams(params);

        if (!url.contains("?")) {
            return url + "?" + queryString;
        }

        return String.join(url.endsWith("&") || url.endsWith("?") ? StringUtils.EMPTY : "&", url, queryString);
    }

    /**
     * 获取查询参数字符串
     * 将参数映射转换为查询字符串格式
     *
     * @param params 参数映射
     * @return 查询字符串，格式为"key1=value1&key2=value2"
     */
    public static String getParams(Map<String, Object> params) {
        return params.entrySet().stream()
                .map(entry -> URLEncoder.encode(entry.getKey(), StandardCharsets.UTF_8) + "=" +
                        URLEncoder.encode(String.valueOf(entry.getValue()), StandardCharsets.UTF_8))
                .collect(Collectors.joining("&"));
    }

    /**
     * 设置自定义请求头
     * 将自定义头添加到请求构建器中
     *
     * @param headers        自定义头映射
     * @param requestBuilder 请求构建器
     */
    private static void setCustomHeader(Map<String, String> headers, HttpRequest.Builder requestBuilder) {
        if (MapUtils.isNotEmpty(headers)) {
            headers.forEach(requestBuilder::header);
        }
    }

    /**
     * 私有构造函数
     * 防止实例化工具类
     */
    private HttpUtils() {
    }
}
