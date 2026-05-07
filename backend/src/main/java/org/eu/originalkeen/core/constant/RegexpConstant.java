package org.eu.originalkeen.core.constant;

/**
 * 正则表达式常量类
 * 定义系统中使用的各种正则表达式模式
 */
public class RegexpConstant {

    /**
     * 登录密码模式
     * 密码必须包含至少一个大写字母、一个小写字母和一个数字
     */
    public static final String LOGIN_PASSWORD_PATTERN = "^(?=.*[A-Z])(?=.*[a-z])(?=.*\\d)[A-Za-z\\d]*$";

    /**
     * 电子邮箱模式
     * 标准的电子邮箱格式校验模式
     */
    public static final String EMAIL_PATTERN = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$";

    /**
     * 手机号码模式
     * 中国大陆手机号码格式，1开头后跟3-9的数字，总长度11位
     */
    public static final String PHONE_NUMBER_PATTERN = "^1[3-9]\\d{9}$";

    /**
     * 路由路径正则表达式
     * 校验前端路由路径格式，支持动态参数和可选参数
     */
    public static final String ROUTER_PATH_REGEX = "^(\\/[A-Za-z0-9_-]+)?(?:\\/[A-Za-z0-9_-]+|\\/:[A-Za-z0-9_]+(?:\\([^)]*\\))?\\??)*\\/?$";

    /**
     * 组件路径正则表达式
     * 校验Vue组件路径格式，必须以.vue结尾
     */
    public static final String COMPONENT_PATH_REGEX = "^\\/(?:[A-Za-z0-9._-]+\\/)*[A-Za-z0-9._-]+\\.vue$";

    /**
     * 链接地址正则表达式
     * 校验URL地址格式，支持HTTP和HTTPS协议，支持域名、IP地址和IPv6地址
     */
    public static final String LINK_ADDRESS_REGEX = "^(https?://)(([a-zA-Z0-9-]+\\.)*([a-zA-Z0-9-]+\\.|xn--[a-zA-Z0-9-]+)+[a-zA-Z]{2,}|\\[([a-fA-F0-9:]+){2,}(::[a-fA-F0-9:]+)*\\]|((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))(:\\d+)?(/[^\\s?#]*)?(\\?[^#]*)?(#.*)?$";

    /**
     * 私有构造函数
     * 防止实例化工具类
     */
    private RegexpConstant() {
    }

}
