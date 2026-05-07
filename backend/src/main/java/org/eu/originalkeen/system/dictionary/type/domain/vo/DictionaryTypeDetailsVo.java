package org.eu.originalkeen.system.dictionary.type.domain.vo;

import com.mybatisflex.annotation.RelationOneToMany;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.List;

/**
 * 字典类型详情视图对象
 * 用于返回字典类型详细信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class DictionaryTypeDetailsVo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 3498175550821788290L;

    /**
     * 字典类型ID
     * 字典类型的唯一标识
     */
    private Long id;

    /**
     * 字典类型代码
     * 字典类型的唯一代码标识
     */
    private String dictionaryTypeCode;

    /**
     * 排序值
     * 字典类型的显示顺序，值越小越靠前
     */
    private Integer sort;

    /**
     * 字典类型状态
     * 字典类型的状态，对应 system_dictionary_type_status 字典数据
     */
    private String dictionaryTypeStatus;

    /**
     * 字典类型翻译列表
     * 字典类型的多语言翻译信息
     */
    @RelationOneToMany(
            selfField = "id",
            targetField = "dictionaryTypeId",
            targetTable = "system_dictionary_type_translation",
            selectColumns = "language_code, dictionary_type_name, remark"
    )
    private List<DictionaryTypeTranslationVo> translations;

}
