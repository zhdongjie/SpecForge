package org.eu.originalkeen.system.dictionary.type.domain.entity;

import com.mybatisflex.annotation.Table;
import org.eu.originalkeen.core.domain.Audit;
import org.eu.originalkeen.core.domain.entity.PrimaryKeyEntity;
import org.eu.originalkeen.system.dictionary.type.domain.dto.CreateDictionaryTypeDto;
import org.eu.originalkeen.system.dictionary.type.domain.dto.UpdateDictionaryTypeDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.Date;

/**
 * 字典类型实体类
 * 对应数据库中的system_dictionary_type表，存储字典类型基本信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Table("system_dictionary_type")
@EqualsAndHashCode(callSuper = true)
public class DictionaryTypeEntity extends PrimaryKeyEntity implements Serializable, Audit {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = 3228203700841074947L;

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
     * 创建时间
     * 记录创建的时间
     */
    private Date createdTime;

    /**
     * 创建人
     * 记录创建人的用户ID
     */
    private Long createdBy;

    /**
     * 最后修改时间
     * 记录最后一次修改的时间
     */
    private Date lastModifiedTime;

    /**
     * 最后修改人
     * 记录最后一次修改人的用户ID
     */
    private Long lastModifiedBy;

    /**
     * 从创建字典类型DTO创建字典类型实体
     * 将字典类型创建数据转换为实体对象
     *
     * @param createDictionaryTypeDto 创建字典类型DTO
     * @return 字典类型实体对象
     */
    public static DictionaryTypeEntity of(CreateDictionaryTypeDto createDictionaryTypeDto) {
        return new DictionaryTypeEntity(
                createDictionaryTypeDto.getDictionaryTypeCode(),
                createDictionaryTypeDto.getSort(),
                createDictionaryTypeDto.getDictionaryTypeStatus(),
                null,
                null,
                null,
                null
        );
    }

    /**
     * 从更新字典类型DTO创建字典类型实体
     * 将字典类型更新数据转换为实体对象
     *
     * @param updateDictionaryTypeDto 更新字典类型DTO
     * @return 字典类型实体对象
     */
    public static DictionaryTypeEntity of(UpdateDictionaryTypeDto updateDictionaryTypeDto) {
        return new DictionaryTypeEntity(
                updateDictionaryTypeDto.getDictionaryTypeCode(),
                updateDictionaryTypeDto.getSort(),
                updateDictionaryTypeDto.getDictionaryTypeStatus(),
                null,
                null,
                null,
                null
        );
    }

}
