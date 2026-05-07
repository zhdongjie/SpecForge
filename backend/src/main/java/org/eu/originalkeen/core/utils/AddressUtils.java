package org.eu.originalkeen.core.utils;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;

import java.io.IOException;
import java.util.Map;

/**
 * 地址工具类
 * 提供根据IP地址获取真实地理位置的功能
 */
@Slf4j
public class AddressUtils {

    /**
     * IP地址查询服务URL
     * 用于查询IP地址对应的地理位置信息
     */
    public static final String IP_URL = "https://whois.pconline.com.cn/ipJson.jsp";

    /**
     * 根据IP地址获取真实地理位置
     * 通过调用外部API获取IP地址对应的地理位置信息
     *
     * @param ip IP地址字符串
     * @return 地理位置字符串，格式为"省份 城市"，如果无法获取则返回null
     */
    public static String getRealAddressByIP(String ip) {
        if (StringUtils.isEmpty(ip)) {
            return null;
        }

        if (IpUtils.isInternalIp(ip)) {
            return "Internal IP";
        }

        Map<String, Object> params = Map.of(
                "ip", ip,
                "json", true
        );
        String responseString;
        responseString = HttpUtils.sendGet(IP_URL, params);

        ObjectMapper objectMapper = new ObjectMapper();
        JsonNode jsonNode;
        try {
            jsonNode = objectMapper.readTree(responseString);
        } catch (IOException exception) {
            log.error("Error processing JSON response for IP: {}", ip, exception);
            return null;
        }
        String region = null;
        String city = null;
        if (jsonNode.hasNonNull("pro")) {
            region = jsonNode.get("pro").textValue();
        }
        if (jsonNode.hasNonNull("city")) {
            city = jsonNode.get("city").textValue();
        }

        if (StringUtils.isEmpty(region) || StringUtils.isEmpty(city)) {
            log.warn("Received empty real address for IP: {}", ip);
            return null;
        }

        return String.format("%s %s", region, city);
    }

    /**
     * 私有构造函数
     * 防止实例化工具类
     */
    private AddressUtils() {
    }

}
