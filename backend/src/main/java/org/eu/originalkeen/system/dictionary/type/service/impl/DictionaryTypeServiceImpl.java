package org.eu.originalkeen.system.dictionary.type.service.impl;

import com.mybatisflex.core.paginate.Page;
import com.mybatisflex.core.query.If;
import com.mybatisflex.core.query.QueryChain;
import com.mybatisflex.spring.service.impl.ServiceImpl;
import org.eu.originalkeen.core.constant.SystemConstant;
import org.eu.originalkeen.core.domain.dto.OrderDto;
import org.eu.originalkeen.core.domain.vo.PageVo;
import org.eu.originalkeen.core.exception.BusinessException;
import org.eu.originalkeen.core.utils.LocaleUtils;
import org.eu.originalkeen.system.dictionary.type.domain.bo.ValidateDictionaryTypeCodeUniqueBo;
import org.eu.originalkeen.system.dictionary.type.domain.dto.EnquiryDictionaryTypePageDto;
import org.eu.originalkeen.system.dictionary.type.domain.entity.DictionaryTypeEntity;
import org.eu.originalkeen.system.dictionary.type.domain.vo.DictionaryTypeDetailsVo;
import org.eu.originalkeen.system.dictionary.type.domain.vo.DictionaryTypeListVo;
import org.eu.originalkeen.system.dictionary.type.domain.vo.DictionaryTypePageVo;
import org.eu.originalkeen.system.dictionary.type.mapper.DictionaryTypeMapper;
import org.eu.originalkeen.system.dictionary.type.service.DictionaryTypeService;
import org.apache.commons.collections4.CollectionUtils;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;

import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;

import static com.mybatisflex.core.util.StringUtil.camelToUnderline;
import static org.eu.originalkeen.system.dictionary.data.domain.entity.table.DictionaryDataTableDef.dictionary_data;
import static org.eu.originalkeen.system.dictionary.type.domain.entity.table.DictionaryTypeTableDef.dictionary_type;
import static org.eu.originalkeen.system.dictionary.type.domain.entity.table.DictionaryTypeTranslationTableDef.dictionary_type_translation;

/**
 * 字典类型服务实现类
 * 实现字典类型管理相关的业务逻辑
 * <p>
 * 主要功能：
 * 1. 实现字典类型服务接口定义的所有方法
 * 2. 处理字典类型的查询、校验和管理
 * 3. 提供字典类型的分页查询和详情获取
 * 4. 支持字典类型的使用情况查询
 * <p>
 * 继承自ServiceImpl，自动注入DictionaryTypeMapper用于数据库操作
 */
@Service
public class DictionaryTypeServiceImpl extends ServiceImpl<DictionaryTypeMapper, DictionaryTypeEntity> implements DictionaryTypeService {

    /**
     * 分页查询字典类型列表
     * 根据查询条件分页获取字典类型列表
     *
     * @param enquiryDictionaryTypePageDto 字典类型分页查询的DTO对象，包含分页参数和查询条件
     * @return 包含字典类型分页数据的响应对象
     */
    @Override
    public PageVo<DictionaryTypePageVo> enquiryPage(EnquiryDictionaryTypePageDto enquiryDictionaryTypePageDto) {
        // 1. 创建分页对象
        //    根据当前页码和页面大小创建分页对象
        Page<DictionaryTypePageVo> page = Page.of(enquiryDictionaryTypePageDto.getCurrentPage(), enquiryDictionaryTypePageDto.getPageSize());

        // 2. 构建查询条件链
        //    创建复杂的查询链，包括表连接、条件过滤等
        QueryChain<DictionaryTypeEntity> queryChain = queryChain()
                .select(
                        dictionary_type.id,
                        dictionary_type_translation.dictionary_type_name,
                        dictionary_type.dictionary_type_code,
                        dictionary_type.sort,
                        dictionary_type.dictionary_type_status,
                        dictionary_type_translation.remark
                )
                .from(dictionary_type)
                // 2.1 左连接字典类型翻译表，获取当前语言的名称和备注
                .innerJoin(dictionary_type_translation)
                .on(dictionary_type.id.eq(dictionary_type_translation.dictionary_type_id))
                // 2.2 添加多个条件筛选，使用If条件判断是否应用筛选
                .where(dictionary_type.dictionary_type_status.eq(enquiryDictionaryTypePageDto.getDictionaryTypeStatus(), If::hasText))
                .and(dictionary_type_translation.dictionary_type_name.like(enquiryDictionaryTypePageDto.getDictionaryTypeName(), If::hasText))
                // 2.3 根据当前语言环境筛选字典类型翻译
                .and(dictionary_type_translation.language_code.eq(LocaleUtils.getLangCode()));

        // 3. 处理排序条件
        //    根据传入的排序条件添加排序规则
        List<OrderDto> orders = enquiryDictionaryTypePageDto.getOrders();
        if (CollectionUtils.isNotEmpty(orders)) {
            for (OrderDto order : orders) {
                // 3.1 添加排序条件，支持多字段排序
                queryChain.orderBy(
                        camelToUnderline(order.getKey()),
                        StringUtils.isNotEmpty(order.getKey())
                                ? order.isAsc()
                                : null
                );
            }
        }

        // 4. 执行分页查询
        //    调用mapper执行查询并将结果映射为DictionaryTypePageVo对象
        Page<DictionaryTypePageVo> dictionaryTypePageVo = pageAs(
                page,
                queryChain,
                DictionaryTypePageVo.class
        );

        // 5. 转换为统一的分页响应对象
        //    将Page对象转换为PageVo对象返回
        return PageVo.of(dictionaryTypePageVo);
    }

    /**
     * 查询字典类型详情
     * 获取指定字典类型ID的详细信息，包括多语言翻译
     *
     * @param id 要查询的字典类型ID
     * @return 包含字典类型详细信息的响应对象
     * @throws BusinessException 当字典类型不存在时抛出
     */
    @Override
    public DictionaryTypeDetailsVo enquiryDetails(Long id) {
        return mapper.selectOneWithRelationsByQueryAs(
                queryChain()
                        .select(
                                dictionary_type.id,
                                dictionary_type.dictionary_type_code,
                                dictionary_type.sort,
                                dictionary_type.dictionary_type_status
                        )
                        .from(dictionary_type)
                        .where(dictionary_type.id.eq(id)),
                DictionaryTypeDetailsVo.class
        );
    }

    /**
     * 查询字典类型列表
     * 查询所有字典类型的列表，用于下拉选择等场景
     *
     * @return 字典类型列表视图对象列表
     */
    @Override
    public List<DictionaryTypeListVo> enquiryList() {
        return listAs(
                queryChain()
                        .select(
                                dictionary_type.id,
                                dictionary_type_translation.dictionary_type_name,
                                dictionary_type.dictionary_type_code
                        )
                        .from(dictionary_type)
                        // 左连接字典类型翻译表，获取当前语言的名称
                        .innerJoin(dictionary_type_translation)
                        .on(dictionary_type.id.eq(dictionary_type_translation.dictionary_type_id))
                        // 只查询启用状态的字典类型
                        .where(dictionary_type.dictionary_type_status.eq(SystemConstant.DICTIONARY_TYPE_ENABLED_STATUS))
                        // 根据当前语言环境筛选字典类型翻译
                        .and(dictionary_type_translation.language_code.eq(LocaleUtils.getLangCode()))
                        // 按排序字段升序排列
                        .orderBy(dictionary_type.sort.asc()),
                DictionaryTypeListVo.class
        );
    }

    /**
     * 校验字典类型是否存在
     * 根据字典类型ID校验字典类型是否存在
     *
     * @param dictionaryTypeId 要校验的字典类型ID
     * @return 如果字典类型存在返回true，否则返回false
     */
    @Override
    public boolean selectDictionaryTypeExists(Long dictionaryTypeId) {
        return exists(dictionary_type.id.eq(dictionaryTypeId));
    }

    /**
     * 校验字典类型代码是否存在
     * 校验指定的字典类型代码是否已经存在，排除当前字典类型ID
     *
     * @param validateDictionaryTypeCodeUniqueBo 字典类型代码唯一性校验对象
     * @return 如果字典类型代码已存在返回true，否则返回false
     */
    @Override
    public boolean selectDictionaryTypeCodeExists(ValidateDictionaryTypeCodeUniqueBo validateDictionaryTypeCodeUniqueBo) {
        return exists(dictionary_type.dictionary_type_code.eq(validateDictionaryTypeCodeUniqueBo.getDictionaryTypeCode())
                .and(dictionary_type.id.ne(validateDictionaryTypeCodeUniqueBo.getId(), Objects::nonNull))
        );
    }

    /**
     * 查询被使用的字典类型代码
     * 根据字典类型ID列表查询被字典数据使用的字典类型代码
     *
     * @param dictionaryTypeIds 字典类型ID列表
     * @return 被使用的字典类型代码列表
     */
    @Override
    public Set<String> selectUsedDictionaryTypeCodes(Set<Long> dictionaryTypeIds) {
        return new HashSet<>(queryChain()
                .select(dictionary_type.dictionary_type_code)
                .from(dictionary_type)
                // 内连接字典数据表，找出被使用的字典类型
                .leftJoin(dictionary_data)
                .on(dictionary_type.dictionary_type_code.eq(dictionary_data.dictionary_type_code))
                // 根据字典类型ID列表筛选记录
                .where(dictionary_type.id.in(dictionaryTypeIds))
                // 按字典类型代码分组，避免重复
                .groupBy(dictionary_type.dictionary_type_code)
                // 执行查询并转换为字符串列表，再转为HashSet
                .listAs(String.class)
        );
    }

    /**
     * 查询字典类型代码是否存在
     * 根据字典类型代码查询字典类型是否存在
     *
     * @param dictionaryTypeCode 字典类型代码
     * @return 如果字典类型存在返回true，否则返回false
     */
    @Override
    public boolean selectDictionaryTypeCodeExists(String dictionaryTypeCode) {
        return exists(dictionary_type.dictionary_type_code.eq(dictionaryTypeCode));
    }

} 
