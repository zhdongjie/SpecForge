package org.eu.originalkeen.system.dictionary.type.service;

import com.mybatisflex.core.service.IService;
import org.eu.originalkeen.core.domain.vo.PageVo;
import org.eu.originalkeen.system.dictionary.type.domain.bo.ValidateDictionaryTypeCodeUniqueBo;
import org.eu.originalkeen.system.dictionary.type.domain.dto.EnquiryDictionaryTypePageDto;
import org.eu.originalkeen.system.dictionary.type.domain.entity.DictionaryTypeEntity;
import org.eu.originalkeen.system.dictionary.type.domain.vo.DictionaryTypeDetailsVo;
import org.eu.originalkeen.system.dictionary.type.domain.vo.DictionaryTypeListVo;
import org.eu.originalkeen.system.dictionary.type.domain.vo.DictionaryTypePageVo;

import java.util.List;
import java.util.Set;

/**
 * 字典类型服务接口
 * 提供字典类型管理相关的业务逻辑方法
 */
public interface DictionaryTypeService extends IService<DictionaryTypeEntity> {
    /**
     * 查询字典类型分页
     * 分页查询字典类型列表
     *
     * @param enquiryDictionaryTypePageDto 查询字典类型分页数据传输对象
     * @return 字典类型分页数据响应对象
     */
    PageVo<DictionaryTypePageVo> enquiryPage(EnquiryDictionaryTypePageDto enquiryDictionaryTypePageDto);

    /**
     * 查询字典类型详情
     * 根据ID查询字典类型详细信息
     *
     * @param id 字典类型ID
     * @return 字典类型详情响应对象
     */
    DictionaryTypeDetailsVo enquiryDetails(Long id);

    /**
     * 查询字典类型列表
     * 查询所有字典类型的列表
     *
     * @return 字典类型列表响应对象
     */
    List<DictionaryTypeListVo> enquiryList();

    /**
     * 校验字典类型是否存在
     * 根据ID校验字典类型记录是否存在
     * <p>
     * 功能：
     * - 用于更新字典类型前的存在性校验
     * - 防止操作不存在的字典类型记录
     *
     * @param dictionaryTypeId 字典类型ID
     * @return 存在返回true，不存在返回false
     */
    boolean selectDictionaryTypeExists(Long dictionaryTypeId);

    /**
     * 校验字典类型代码是否存在
     * 根据代码校验是否已存在记录
     * <p>
     * 功能：
     * - 用于创建字典类型前的代码唯一性校验
     * - 用于更新字典类型前的代码唯一性校验
     * - 防止创建重复的字典类型代码
     *
     * @param validateDictionaryTypeCodeUniqueBo 字典类型代码唯一性校验业务对象，包含要校验的代码和排除的ID
     * @return 存在返回true，不存在返回false
     */
    boolean selectDictionaryTypeCodeExists(ValidateDictionaryTypeCodeUniqueBo validateDictionaryTypeCodeUniqueBo);

    /**
     * 查询被使用的字典类型代码
     * 根据字典类型ID列表查询被字典数据使用的字典类型代码
     * <p>
     * 功能：
     * - 用于删除字典类型前的使用情况校验
     * - 防止删除已被使用的字典类型
     * - 返回被使用的字典类型代码，用于提示用户
     *
     * @param dictionaryTypeIds 字典类型ID列表
     * @return 被使用的字典类型代码列表
     */
    Set<String> selectUsedDictionaryTypeCodes(Set<Long> dictionaryTypeIds);

    /**
     * 查询字典类型代码是否存在
     * 根据字典类型代码查询字典类型是否存在
     *
     * @param dictionaryTypeCode 字典类型代码
     * @return 如果字典类型存在返回true，否则返回false
     */
    boolean selectDictionaryTypeCodeExists(String dictionaryTypeCode);

}
