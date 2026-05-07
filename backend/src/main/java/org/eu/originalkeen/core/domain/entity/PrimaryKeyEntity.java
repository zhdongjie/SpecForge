package org.eu.originalkeen.core.domain.entity;

import com.mybatisflex.annotation.Id;
import com.mybatisflex.annotation.KeyType;
import com.mybatisflex.core.keygen.KeyGenerators;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 主键实体基类
 * 为实体类提供通用的主键字段，使用FlexID生成器生成唯一ID
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PrimaryKeyEntity implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 8748570551162539786L;

    /**
     * 主键字段
     * 使用FlexID生成器自动生成的唯一ID
     */
    @Id(keyType = KeyType.Generator, value = KeyGenerators.flexId)
    private Long id;

}
