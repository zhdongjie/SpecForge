package org.eu.originalkeen.system.dictionary.data.service.impl;

import com.mybatisflex.core.paginate.Page;
import com.mybatisflex.core.query.If;
import com.mybatisflex.core.query.QueryChain;
import com.mybatisflex.spring.service.impl.ServiceImpl;
import org.eu.originalkeen.core.constant.SystemConstant;
import org.eu.originalkeen.core.domain.dto.OrderDto;
import org.eu.originalkeen.core.domain.vo.PageVo;
import org.eu.originalkeen.core.exception.business.FieldValidationException;
import org.eu.originalkeen.core.utils.LocaleUtils;
import org.eu.originalkeen.system.dictionary.data.domain.bo.ValidateDictionaryDataValueUniqueBo;
import org.eu.originalkeen.system.dictionary.data.domain.dto.EnquiryDictionaryDataPageDto;
import org.eu.originalkeen.system.dictionary.data.domain.entity.DictionaryDataEntity;
import org.eu.originalkeen.system.dictionary.data.domain.vo.DictionaryDataDetailsVo;
import org.eu.originalkeen.system.dictionary.data.domain.vo.DictionaryDataListVo;
import org.eu.originalkeen.system.dictionary.data.domain.vo.DictionaryDataPageVo;
import org.eu.originalkeen.system.dictionary.data.mapper.DictionaryDataMapper;
import org.eu.originalkeen.system.dictionary.data.service.DictionaryDataService;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.collections4.CollectionUtils;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static com.mybatisflex.core.util.StringUtil.camelToUnderline;
import static org.eu.originalkeen.system.dictionary.data.domain.entity.table.DictionaryDataTableDef.dictionary_data;
import static org.eu.originalkeen.system.dictionary.data.domain.entity.table.DictionaryDataTranslationTableDef.dictionary_data_translation;

/**
 * 字典数据服务实现类
 * 实现字典数据管理相关的业务逻辑
 * <p>
 * 主要功能：
 * 1. 实现字典数据服务接口定义的所有方法
 * 2. 处理字典数据的查询、校验和管理
 * 3. 提供字典数据的分页查询和详情获取
 * 4. 支持字典数据值与标签的相互转换
 * 5. 管理字典数据的有效性和唯一性校验
 * <p>
 * 继承自ServiceImpl，自动注入DictionaryDataMapper用于数据库操作
 */
@Slf4j
@Service
public class DictionaryDataServiceImpl extends ServiceImpl<DictionaryDataMapper, DictionaryDataEntity> implements DictionaryDataService {

    /**
     * 分页查询字典数据列表
     * 根据查询条件分页获取字典数据列表，支持按字典类型代码、值和标签过滤
     *
     * @param enquiryDictionaryDataPageDto 查询字典数据分页数据传输对象，包含分页参数和查询条件
     * @return 字典数据分页数据响应对象
     */
    @Override
    public PageVo<DictionaryDataPageVo> enquiryPage(EnquiryDictionaryDataPageDto enquiryDictionaryDataPageDto) {
        // 1. 创建分页对象，设置当前页和每页大小
        Page<DictionaryDataPageVo> page = Page.of(enquiryDictionaryDataPageDto.getCurrentPage(), enquiryDictionaryDataPageDto.getPageSize());

        // 2. 构建查询链，包含字段选择、表关联和条件过滤
        QueryChain<DictionaryDataEntity> queryChain = queryChain()
                .select(
                        dictionary_data.id,
                        dictionary_data.dictionary_type_code,
                        dictionary_data.value,
                        dictionary_data_translation.label,
                        dictionary_data.sort,
                        dictionary_data.dictionary_data_status,
                        dictionary_data_translation.remark,
                        dictionary_data.created_time
                )
                .from(dictionary_data)
                .innerJoin(dictionary_data_translation)
                .on(dictionary_data.id.eq(dictionary_data_translation.dictionary_data_id))
                .where(dictionary_data.dictionary_type_code.eq(enquiryDictionaryDataPageDto.getDictionaryTypeCode(), If::hasText))
                .and(dictionary_data.value.like(enquiryDictionaryDataPageDto.getValue(), If::hasText))
                .and(dictionary_data_translation.label.like(enquiryDictionaryDataPageDto.getLabel(), If::hasText))
                .and(dictionary_data_translation.language_code.eq(LocaleUtils.getLangCode()));

        // 3. 处理排序条件，根据传入的排序参数添加排序规则
        List<OrderDto> orders = enquiryDictionaryDataPageDto.getOrders();
        if (CollectionUtils.isNotEmpty(orders)) {
            for (OrderDto order : orders) {
                queryChain.orderBy(
                        camelToUnderline(order.getKey()),
                        StringUtils.isNotEmpty(order.getKey())
                                ? order.isAsc()
                                : null
                );
            }
        }

        // 4. 执行分页查询，将结果映射为指定的视图对象类型
        Page<DictionaryDataPageVo> dictionaryDataPageVo = pageAs(
                page,
                queryChain,
                DictionaryDataPageVo.class
        );

        // 5. 将MyBatisFlex的分页对象转换为统一的分页视图对象
        return PageVo.of(dictionaryDataPageVo);
    }

    /**
     * 查询字典数据详情
     * 根据ID查询字典数据详细信息，包括基本信息
     *
     * @param id 字典数据ID
     * @return 字典数据详情响应对象
     */
    @Override
    public DictionaryDataDetailsVo enquiryDetails(Long id) {
        return mapper.selectOneWithRelationsByQueryAs(
                queryChain()
                        .select(
                                dictionary_data.id,
                                dictionary_data.dictionary_type_code,
                                dictionary_data.value,
                                dictionary_data.sort,
                                dictionary_data.dictionary_data_status
                        )
                        .from(dictionary_data)
                        .where(dictionary_data.id.eq(id)),
                DictionaryDataDetailsVo.class
        );
    }

    /**
     * 查询字典数据选项列表
     * 根据字典类型代码查询字典数据选项列表，仅返回启用状态的数据
     *
     * @param dictionaryTypeCode 字典类型代码
     * @return 字典数据选项列表响应对象
     */
    @Override
    public List<DictionaryDataListVo> enquiryList(String dictionaryTypeCode) {
        return queryChain()
                .select(
                        dictionary_data.value,
                        dictionary_data_translation.label,
                        dictionary_data.dictionary_data_status.as("status")
                )
                .from(dictionary_data)
                .innerJoin(dictionary_data_translation)
                .on(dictionary_data.id.eq(dictionary_data_translation.dictionary_data_id))
                .where(dictionary_data.dictionary_type_code.eq(dictionaryTypeCode))
                .and(dictionary_data_translation.language_code.eq(LocaleUtils.getLangCode()))
                .orderBy(dictionary_data.sort.asc())
                .listAs(DictionaryDataListVo.class);
    }

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
    @Override
    public void validateDictionaryDataValue(String dictionaryTypeCode, String value, String field, String errorMessageCode) {
        // 1. 校验字典值是否存在，查询指定类型和值的字典数据是否存在且处于启用状态
        boolean exists = exists(
                dictionary_data.dictionary_type_code.eq(dictionaryTypeCode)
                        .and(dictionary_data.value.eq(value))
                        .and(dictionary_data.dictionary_data_status.eq(SystemConstant.DICTIONARY_DATA_ENABLED_STATUS))
        );

        // 2. 如果字典值不存在，则准备抛出异常
        if (!exists) {
            // 3. 记录警告日志，标识字典值校验失败
            log.warn("Dictionary data value [{}] not found for dictionary type [{}]", value, dictionaryTypeCode);

            // 4. 查询该字典类型下所有可用的选项值，用于提供有效选项信息
            Set<String> availableValues = selectAvailableValues(dictionaryTypeCode);

            // 5. 将可用选项拼接为字符串，用于错误消息展示
            String availableOptions = String.join(", ", availableValues);

            // 6. 抛出字段校验异常，并携带可用选项信息
            throw new FieldValidationException(field, errorMessageCode, availableOptions);
        }
    }

    /**
     * 查询指定字典类型下的所有可用选项值
     * 根据字典类型代码查询所有启用状态的字典数据值
     *
     * @param dictionaryTypeCode 字典类型代码
     * @return 可用选项值列表
     */
    @Override
    public Set<String> selectAvailableValues(String dictionaryTypeCode) {
        return new HashSet<>(queryChain()
                .select(dictionary_data.value)
                .from(dictionary_data)
                .where(dictionary_data.dictionary_type_code.eq(dictionaryTypeCode))
                .and(dictionary_data.dictionary_data_status.eq(SystemConstant.DICTIONARY_DATA_ENABLED_STATUS))
                .orderBy(dictionary_data.sort.asc())
                .listAs(String.class)
        );
    }

    /**
     * 查询字典数据是否存在
     * 根据ID查询字典数据是否存在
     *
     * @param dictionaryDataId 字典数据ID
     * @return 如果字典数据存在返回true，否则返回false
     */
    @Override
    public boolean selectDictionaryDataExists(Long dictionaryDataId) {
        return exists(dictionary_data.id.eq(dictionaryDataId));
    }

    /**
     * 查询字典数据值是否存在
     * 查询指定的字典数据值是否已经存在，排除当前字典数据ID
     *
     * @param validateDictionaryDataValueUniqueBo 字典数据值唯一性校验业务对象
     * @return 如果字典数据值已存在返回true，否则返回false
     */
    @Override
    public boolean selectDictionaryDataValueExists(ValidateDictionaryDataValueUniqueBo validateDictionaryDataValueUniqueBo) {
        return exists(
                dictionary_data.id.ne(validateDictionaryDataValueUniqueBo.getId(), If::notNull)
                        .and(dictionary_data.dictionary_type_code.eq(validateDictionaryDataValueUniqueBo.getDictionaryTypeCode()))
                        .and(dictionary_data.value.eq(validateDictionaryDataValueUniqueBo.getValue()))
        );
    }

    /**
     * 根据标签获取值
     * 根据字典类型代码和标签查询对应的值，仅查询启用状态的数据
     *
     * @param dictionaryTypeCode 字典类型代码
     * @param label              标签
     * @return 对应的值，如果不存在则返回null
     */
    @Override
    public String selectValueByLabel(String dictionaryTypeCode, String label) {
        return queryChain()
                .select(dictionary_data.value)
                .from(dictionary_data)
                .innerJoin(dictionary_data_translation)
                .on(dictionary_data.id.eq(dictionary_data_translation.dictionary_data_id))
                .where(dictionary_data.dictionary_type_code.eq(dictionaryTypeCode))
                .and(dictionary_data_translation.label.eq(label))
                .and(dictionary_data.dictionary_data_status.eq(SystemConstant.DICTIONARY_DATA_ENABLED_STATUS))
                .oneAs(String.class);
    }

    /**
     * 根据值获取标签
     * 根据字典类型代码和值查询对应的标签，仅查询启用状态的数据
     *
     * @param dictionaryTypeCode 字典类型代码
     * @param value              值
     * @return 对应的标签，如果不存在则返回null
     */
    @Override
    public String selectLabelByValue(String dictionaryTypeCode, String value) {
        return queryChain()
                .select(dictionary_data_translation.label)
                .from(dictionary_data_translation)
                .leftJoin(dictionary_data)
                .on(dictionary_data_translation.dictionary_data_id.eq(dictionary_data.id))
                .where(dictionary_data.dictionary_type_code.eq(dictionaryTypeCode))
                .and(dictionary_data.value.eq(value))
                .and(dictionary_data_translation.language_code.eq(LocaleUtils.getLangCode()))
                .oneAs(String.class);
    }

    /**
     * 根据字典类型代码获取标签列表
     * 查询指定字典类型代码下的所有标签，仅查询启用状态的数据
     *
     * @param dictionaryTypeCode 字典类型代码
     * @return 标签列表
     */
    @Override
    public Set<String> selectLabelListByDictionaryTypeCode(String dictionaryTypeCode) {
        return new HashSet<>(queryChain()
                .select(dictionary_data_translation.label)
                .from(dictionary_data_translation)
                .leftJoin(dictionary_data)
                .on(dictionary_data_translation.dictionary_data_id.eq(dictionary_data.id))
                .where(dictionary_data.dictionary_type_code.eq(dictionaryTypeCode))
                .and(dictionary_data_translation.language_code.eq(LocaleUtils.getLangCode()))
                .and(dictionary_data.dictionary_data_status.eq(SystemConstant.DICTIONARY_DATA_ENABLED_STATUS))
                .listAs(String.class)
        );
    }

    /**
     * 根据字典类型代码获取值列表
     * 查询指定字典类型代码下的所有值，仅查询启用状态的数据
     *
     * @param dictionaryTypeCode 字典类型代码
     * @return 值列表
     */
    @Override
    public Set<String> selectValueListByDictionaryTypeCode(String dictionaryTypeCode) {
        return new HashSet<>(queryChain()
                .select(dictionary_data.value)
                .from(dictionary_data)
                .where(dictionary_data.dictionary_type_code.eq(dictionaryTypeCode))
                .and(dictionary_data.dictionary_data_status.eq(SystemConstant.DICTIONARY_DATA_ENABLED_STATUS))
                .listAs(String.class)
        );
    }

}
