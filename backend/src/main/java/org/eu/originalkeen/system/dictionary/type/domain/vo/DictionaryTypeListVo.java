package org.eu.originalkeen.system.dictionary.type.domain.vo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 字典类型列表视图对象
 * 用于返回字典类型列表数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class DictionaryTypeListVo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 987519653426030161L;

    /**
     * 字典类型ID
     * 字典类型的唯一标识
     */
    private Long id;

    /**
     * 字典类型名称
     * 字典类型的名称
     */
    private String dictionaryTypeName;

}
