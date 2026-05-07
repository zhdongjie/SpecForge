package org.eu.originalkeen.core.utils;

import jakarta.servlet.http.HttpServletRequest;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;

import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.Objects;

/**
 * IP地址工具类
 * 提供提取客户端IP地址和判断内部IP的工具方法
 */
@Slf4j
public class IpUtils {

    /**
     * IP头候选列表
     * 包含可能包含客户端IP地址的HTTP请求头列表
     */
    private static final String[] IP_HEADER_CANDIDATES = {
            "X-Forwarded-For",
            "Proxy-Client-IP",
            "WL-Proxy-Client-IP",
            "X-Real-IP",
            "HTTP_CLIENT_IP",
            "HTTP_X_FORWARDED_FOR"
    };

    /**
     * 提取客户端IP地址
     * 从当前请求中提取客户端IP地址
     *
     * @return 客户端IP地址字符串，如果无法获取则返回null
     */
    public static String extractClientIp() {
        String ip = extractClientIp(ServletUtils.getRequest());
        if (StringUtils.isEmpty(ip)) {
            return "Unknown";
        }
        return ip;
    }

    /**
     * 判断是否为内部IP地址
     * 校验给定IP地址是否为内部网络地址（私有IP或本地环回IP）
     *
     * @param ip 要校验的IP地址字符串
     * @return 如果是内部IP地址则返回true，否则返回false
     * @throws IllegalArgumentException 如果IP地址无效则抛出异常
     */
    public static boolean isInternalIp(String ip) {
        if (StringUtils.isEmpty(ip) || !isValidIp(ip)) {
            throw new IllegalArgumentException("Invalid IP address: " + ip);
        }
        byte[] ipBytes = parseIpv4ToBytes(ip);
        return isPrivateIp(ipBytes) || StringUtils.equals("127.0.0.1", ip);
    }

    /**
     * 从请求中提取客户端IP地址
     * 从给定的HTTP请求中提取客户端IP地址，先校验各种代理头，然后再使用远程地址
     *
     * @param request HTTP请求对象
     * @return 客户端IP地址字符串，如果无法获取则返回null
     */
    private static String extractClientIp(HttpServletRequest request) {
        if (Objects.isNull(request)) {
            return null;
        }

        for (String header : IP_HEADER_CANDIDATES) {
            String ip = request.getHeader(header);
            if (isNonEmptyAndNotUnknown(ip)) {
                return normalizeIp(ip);
            }
        }

        String ip = request.getRemoteAddr();
        return StringUtils.equals("0:0:0:0:0:0:0:1", ip) ? "127.0.0.1" : normalizeIp(ip);
    }

    /**
     * 标准化IP地址
     * 处理可能包含多个IP地址的字符串，返回第一个有效的IP地址
     *
     * @param ip 原始IP地址字符串，可能包含多个IP地址（用逗号分隔）
     * @return 标准化后的IP地址字符串，如果无法获取则返回null
     */
    private static String normalizeIp(String ip) {
        if (StringUtils.isEmpty(ip)) {
            return null;
        }

        String[] ipParts = ip.trim().split(",");
        for (String part : ipParts) {
            String trimmedIp = part.trim();
            if (isNonEmptyAndNotUnknown(trimmedIp) && isValidIp(trimmedIp)) {
                return StringUtils.substring(trimmedIp, 0, 255);
            }
        }

        return null;
    }

    /**
     * 判断是否为私有IP地址
     * 校验给定的IP地址字节数组是否属于私有IP范围（A类、B类、C类私有地址）
     *
     * @param addr IP地址字节数组
     * @return 如果是私有IP地址则返回true，否则返回false
     */
    private static boolean isPrivateIp(byte[] addr) {
        if (addr.length != 4) {
            return false;
        }

        int b0 = Byte.toUnsignedInt(addr[0]);
        int b1 = Byte.toUnsignedInt(addr[1]);

        if (b0 == 10) {
            return true;
        }

        if (b0 == 172 && b1 >= 16 && b1 <= 31) {
            return true;
        }

        return b0 == 192 && b1 == 168;
    }

    /**
     * 将IPv4地址字符串解析为字节数组
     * 将形如"192.168.1.1"的IPv4地址字符串转换为对应的字节数组
     *
     * @param ipv4 IPv4地址字符串
     * @return 包含4个字节的数组，如果解析失败则返回空数组
     */
    private static byte[] parseIpv4ToBytes(String ipv4) {
        String[] segments = ipv4.split("\\.");
        if (segments.length != 4) {
            return new byte[0];
        }

        byte[] bytes = new byte[4];
        for (int i = 0; i < 4; i++) {
            bytes[i] = (byte) Integer.parseInt(segments[i]);
        }
        return bytes;
    }

    /**
     * 校验IP地址是否有效
     * 校验给定的字符串是否是有效的IP地址
     *
     * @param ip 要校验的IP地址字符串
     * @return 如果是有效的IP地址则返回true，否则返回false
     */
    public static boolean isValidIp(String ip) {
        if (StringUtils.isEmpty(ip)) {
            return false;
        }

        try {
            InetAddress inetAddress = InetAddress.getByName(ip);
            log.debug("Validated IP: {}, resolved as: {}", ip, inetAddress.getHostAddress());
            return true;
        } catch (UnknownHostException exception) {
            log.debug("Invalid IP: {}", ip, exception);
            return false;
        }
    }

    /**
     * 校验IP字符串是否非空且不是"unknown"
     * 用于过滤无效的IP地址字符串
     *
     * @param ip IP地址字符串
     * @return 如果字符串非空且不是"unknown"则返回true，否则返回false
     */
    private static boolean isNonEmptyAndNotUnknown(String ip) {
        return StringUtils.isNotEmpty(ip) && !StringUtils.equalsIgnoreCase("unknown", ip);
    }

    /**
     * 私有构造函数
     * 防止实例化工具类
     */
    private IpUtils() {
    }

}
