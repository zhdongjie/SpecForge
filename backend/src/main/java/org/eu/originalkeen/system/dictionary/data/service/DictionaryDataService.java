package org.eu.originalkeen.system.dictionary.data.service;

import com.mybatisflex.core.service.IService;
import org.eu.originalkeen.core.domain.vo.PageVo;
import org.eu.originalkeen.core.exception.business.FieldValidationException;
import org.eu.originalkeen.system.dictionary.data.domain.bo.ValidateDictionaryDataValueUniqueBo;
import org.eu.originalkeen.system.dictionary.data.domain.dto.EnquiryDictionaryDataPageDto;
import org.eu.originalkeen.system.dictionary.data.domain.entity.DictionaryDataEntity;
import org.eu.originalkeen.system.dictionary.data.domain.vo.DictionaryDataDetailsVo;
import org.eu.originalkeen.system.dictionary.data.domain.vo.DictionaryDataListVo;
import org.eu.originalkeen.system.dictionary.data.domain.vo.DictionaryDataPageVo;

import java.util.List;
import java.util.Set;

/**
 * 字典数据服务接口
 * 提供字典数据管理相关的业务逻辑方法
 */
public interface DictionaryDataService extends IService<DictionaryDataEntity> {

    /**
     * 查询字典数据分页
     * 分页查询字典数据列表
     *
     * @param enquiryDictionaryDataPageDto 查询字典数据分页数据传输对象
     * @return 字典数据分页数据响应对象
     */
    PageVo<DictionaryDataPageVo> enquiryPage(EnquiryDictionaryDataPageDto enquiryDictionaryDataPageDto);

    /**
     * 查询字典数据详情
     * 根据ID查询字典数据详细信息
     *
     * @param id 字典数据ID
     * @return 字典数据详情响应对象
     */
    DictionaryDataDetailsVo enquiryDetails(Long id);

    /**
     * 查询字典数据选项列表
     * 根据字典类型代码查询字典数据选项列表
     *
     * @param dictionaryTypeCode 字典类型代码
     * @return 字典数据选项列表响应对象
     */
    List<DictionaryDataListVo> enquiryList(String dictionaryTypeCode);

    /**
     * 校验字典数据值是否有效
     * 校验指定字典类型下是否存在给定的值，如果不存在则抛出字段校验异常
     * 并在异常信息中包含该字典类型下所有可用的选项值
     *
     * @param dictionaryTypeCode 字典类型代码
     * @param value              需要校验的值
     * @param field              字段名称，用于异常信息
     * @param errorMessageCode   错误消息代码
     * @throws FieldValidationException 当值无效时抛出，包含所有可选值
     */
    void validateDictionaryDataValue(String dictionaryTypeCode, String value, String field, String errorMessageCode);

    /**
     * 查询指定字典类型下的所有可用选项值
     * 根据字典类型代码查询所有可用的字典数据值
     *
     * @param dictionaryTypeCode 字典类型代码
     * @return 可用选项值列表
     */
    Set<String> selectAvailableValues(String dictionaryTypeCode);


    /**
     * 根据标签获取值
     * 根据字典类型代码和标签查询对应的值
     *
     * @param dictionaryTypeCode 字典类型代码
     * @param label              标签
     * @return 对应的值，如果不存在则返回null
     */
    String selectValueByLabel(String dictionaryTypeCode, String label);

    /**
     * 根据值获取标签
     * 根据字典类型代码和值查询对应的标签
     *
     * @param dictionaryTypeCode 字典类型代码
     * @param value              值
     * @return 对应的标签，如果不存在则返回null
     */
    String selectLabelByValue(String dictionaryTypeCode, String value);

    /**
     * 根据字典类型代码获取标签列表
     * 查询指定字典类型代码下的所有标签
     *
     * @param dictionaryTypeCode 字典类型代码
     * @return 标签列表
     */
    Set<String> selectLabelListByDictionaryTypeCode(String dictionaryTypeCode);

    /**
     * 根据字典类型代码获取值列表
     * 查询指定字典类型代码下的所有值
     *
     * @param dictionaryTypeCode 字典类型代码
     * @return 值列表
     */
    Set<String> selectValueListByDictionaryTypeCode(String dictionaryTypeCode);

    /**
     * 查询字典数据是否存在
     * 根据ID查询字典数据是否存在
     *
     * @param dictionaryDataId 字典数据ID
     * @return 如果字典数据存在返回true，否则返回false
     */
    boolean selectDictionaryDataExists(Long dictionaryDataId);

    /**
     * 查询字典数据值是否存在
     * 查询指定的字典数据值是否已经存在
     *
     * @param validateDictionaryDataValueUniqueBo 字典数据值唯一性校验业务对象
     * @return 如果字典数据值已存在返回true，否则返回false
     */
    boolean selectDictionaryDataValueExists(ValidateDictionaryDataValueUniqueBo validateDictionaryDataValueUniqueBo);

}
