package org.eu.originalkeen;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;

/**
 * 应用程序启动类
 * 使用@SpringBootApplication注解标记这是一个Spring Boot应用程序
 */
@SpringBootApplication
@ConfigurationPropertiesScan
public class BackendApplication {

    /**
     * 应用程序入口方法
     *
     * @param args 命令行参数
     */
    public static void main(String[] args) {
        SpringApplication.run(BackendApplication.class, args);
    }

}
