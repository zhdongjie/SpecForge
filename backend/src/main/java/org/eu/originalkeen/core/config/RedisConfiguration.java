package org.eu.originalkeen.core.config;

import org.springframework.context.annotation.Bean;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.GenericJackson2JsonRedisSerializer;
import org.springframework.data.redis.serializer.RedisSerializer;
import org.springframework.stereotype.Component;

/**
 * Redis配置类
 * 配置Redis模板和序列化器，用于操作Redis缓存
 */
@Component
public class RedisConfiguration {

    /**
     * 获取Redis模板
     * 创建并配置RedisTemplate，使用JSON序列化器存储值，使用字符串序列化器存储键
     *
     * @param redisConnectionFactory Redis连接工厂
     * @param <K>                    键类型
     * @param <V>                    值类型
     * @return 配置好的RedisTemplate实例
     */
    @Bean
    public <K, V> RedisTemplate<K, V> getRedisTemplate(RedisConnectionFactory redisConnectionFactory) {
        RedisTemplate<K, V> redisTemplate = new RedisTemplate<>();
        redisTemplate.setConnectionFactory(redisConnectionFactory);

        GenericJackson2JsonRedisSerializer jsonRedisSerializer = new GenericJackson2JsonRedisSerializer();

        redisTemplate.setKeySerializer(RedisSerializer.string());
        redisTemplate.setHashKeySerializer(RedisSerializer.string());

        redisTemplate.setValueSerializer(jsonRedisSerializer);
        redisTemplate.setHashValueSerializer(jsonRedisSerializer);

        return redisTemplate;
    }

}
