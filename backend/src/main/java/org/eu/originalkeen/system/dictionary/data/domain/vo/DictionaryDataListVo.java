package org.eu.originalkeen.system.dictionary.data.domain.vo;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 字典数据选项视图对象
 * 用于展示字典数据选项列表
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class DictionaryDataListVo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -368545587336092756L;

    /**
     * 字典值
     * 字典数据的值
     */
    private String value;

    /**
     * 字典标签
     * 字典数据在当前语言下的显示标签
     */
    private String label;

    /**
     * 字典数据状态
     * 字典数据的状态，对应 system_dictionary_data_status 字典数据
     */
    private String status;

}
