package org.eu.originalkeen.system.dictionary.data.domain.vo;

import com.mybatisflex.annotation.RelationOneToMany;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.List;

/**
 * 字典数据详情视图对象
 * 用于展示字典数据详细信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class DictionaryDataDetailsVo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 2930121224785866610L;

    /**
     * 字典数据ID
     * 字典数据的唯一标识
     */
    private Long id;

    /**
     * 字典类型代码
     * 关联的字典类型代码
     */
    private String dictionaryTypeCode;

    /**
     * 字典值
     * 字典数据的值
     */
    private String value;

    /**
     * 排序值
     * 字典数据的显示顺序，值越小越靠前
     */
    private Integer sort;

    /**
     * 字典数据翻译列表
     * 字典数据的多语言翻译信息
     */
    @RelationOneToMany(
            selfField = "id",
            targetField = "dictionaryDataId",
            targetTable = "system_dictionary_data_translation",
            selectColumns = "language_code, label, remark"
    )
    private List<DictionaryDataTranslationVo> translations;

} 
