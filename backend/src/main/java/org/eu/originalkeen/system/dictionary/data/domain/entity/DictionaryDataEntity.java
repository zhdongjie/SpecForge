package org.eu.originalkeen.system.dictionary.data.domain.entity;

import com.mybatisflex.annotation.Table;
import org.eu.originalkeen.core.domain.Audit;
import org.eu.originalkeen.core.domain.entity.PrimaryKeyEntity;
import org.eu.originalkeen.system.dictionary.data.domain.dto.CreateDictionaryDataDto;
import org.eu.originalkeen.system.dictionary.data.domain.dto.UpdateDictionaryDataDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.Date;

/**
 * 字典数据实体类
 * 对应数据库中的system_dictionary_data表，存储字典数据基本信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Table("system_dictionary_data")
@EqualsAndHashCode(callSuper = true)
public class DictionaryDataEntity extends PrimaryKeyEntity implements Serializable, Audit {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -5709204479666113307L;

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
     * 字典数据状态
     * 字典数据的状态，对应 system_dictionary_data_status 字典数据
     */
    private String dictionaryDataStatus;

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
     * 从创建字典数据DTO创建字典数据实体
     * 将字典数据创建数据转换为实体对象
     *
     * @param createDictionaryDataDto 创建字典数据DTO
     * @return 字典数据实体对象
     */
    public static DictionaryDataEntity of(CreateDictionaryDataDto createDictionaryDataDto) {
        return new DictionaryDataEntity(
                createDictionaryDataDto.getDictionaryTypeCode(),
                createDictionaryDataDto.getValue(),
                createDictionaryDataDto.getSort(),
                createDictionaryDataDto.getDictionaryDataStatus(),
                null,
                null,
                null,
                null
        );
    }

    /**
     * 从更新字典数据DTO创建字典数据实体
     * 将字典数据更新数据转换为实体对象
     *
     * @param updateDictionaryDataDto 更新字典数据DTO
     * @return 字典数据实体对象
     */
    public static DictionaryDataEntity of(UpdateDictionaryDataDto updateDictionaryDataDto) {
        return new DictionaryDataEntity(
                updateDictionaryDataDto.getDictionaryTypeCode(),
                updateDictionaryDataDto.getValue(),
                updateDictionaryDataDto.getSort(),
                updateDictionaryDataDto.getDictionaryDataStatus(),
                null,
                null,
                null,
                null
        );
    }

}
