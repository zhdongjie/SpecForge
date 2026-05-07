package org.eu.originalkeen.core.config;

import org.eu.originalkeen.core.utils.JwtUtils;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

/**
 * JWT配置类
 * 在应用启动时自动生成JWT所需的JWK密钥文件
 */
@Slf4j
@Component
public class JwtConfiguration implements ApplicationRunner {

    /**
     * 应用启动后运行
     * 在应用启动完成后自动生成JWT密钥文件
     *
     * @param args 应用参数
     */
    @Override
    public void run(ApplicationArguments args) {
        log.info("Generating JWK...");

        JwtUtils.generateJwk();

        log.info("JWK generation completed successfully");
    }

}
