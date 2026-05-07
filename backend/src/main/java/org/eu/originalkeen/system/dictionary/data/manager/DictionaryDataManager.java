package org.eu.originalkeen.system.dictionary.data.manager;

import org.eu.originalkeen.core.constant.SystemConstant;
import org.eu.originalkeen.core.domain.vo.PageVo;
import org.eu.originalkeen.core.domain.vo.ResponseVo;
import org.eu.originalkeen.core.exception.BusinessException;
import org.eu.originalkeen.core.exception.business.FieldValidationException;
import org.eu.originalkeen.core.utils.TranslationUtils;
import org.eu.originalkeen.system.dictionary.data.domain.bo.DictionaryDataTranslationBo;
import org.eu.originalkeen.system.dictionary.data.domain.bo.ValidateDictionaryDataBo;
import org.eu.originalkeen.system.dictionary.data.domain.bo.ValidateDictionaryDataLabelUniqueBo;
import org.eu.originalkeen.system.dictionary.data.domain.bo.ValidateDictionaryDataValueUniqueBo;
import org.eu.originalkeen.system.dictionary.data.domain.dto.*;
import org.eu.originalkeen.system.dictionary.data.domain.entity.DictionaryDataEntity;
import org.eu.originalkeen.system.dictionary.data.domain.vo.DictionaryDataDetailsVo;
import org.eu.originalkeen.system.dictionary.data.domain.vo.DictionaryDataListVo;
import org.eu.originalkeen.system.dictionary.data.domain.vo.DictionaryDataPageVo;
import org.eu.originalkeen.system.dictionary.data.service.DictionaryDataService;
import org.eu.originalkeen.system.dictionary.data.service.DictionaryDataTranslationService;
import org.eu.originalkeen.system.dictionary.type.service.DictionaryTypeService;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.collections4.CollectionUtils;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Objects;
import java.util.Set;

import static org.eu.originalkeen.system.dictionary.data.domain.entity.table.DictionaryDataTableDef.dictionary_data;

/**
 * 字典数据管理器
 * 提供字典数据管理相关的业务处理功能，整合字典数据服务、字典数据翻译服务和字典类型服务
 * <p>
 * 主要功能：
 * 1. 字典数据的创建、更新、删除和查询
 * 2. 字典数据与翻译的关联管理
 * 3. 字典数据信息的校验逻辑
 * 4. 字典数据值和标签的唯一性校验
 * 5. 字典数据的业务规则处理
 * <p>
 * 使用@Slf4j注解提供日志记录功能
 */
@Slf4j
@Component
public class DictionaryDataManager {

    /**
     * 字典类型服务
     * 用于校验字典类型代码是否存在，确保字典数据关联的字典类型有效
     */
    @Resource
    private DictionaryTypeService dictionaryTypeService;

    /**
     * 字典数据服务
     * 用于管理字典数据基本信息，提供字典数据的增删改查和值校验等功能
     */
    @Resource
    private DictionaryDataService dictionaryDataService;

    /**
     * 字典数据翻译服务
     * 用于管理字典数据多语言翻译信息，提供翻译数据的批量保存、更新和删除等功能
     */
    @Resource
    private DictionaryDataTranslationService dictionaryDataTranslationService;

    /**
     * 校验字典数据标签唯一性
     * 校验字典数据标签是否已被使用
     *
     * @param validateDictionaryDataLabelUniqueDto 字典数据标签校验数据传输对象
     * @return 校验结果响应对象，true表示已存在，false表示不存在
     */
    @Transactional(readOnly = true)
    public ResponseVo<Boolean> validateDictionaryDataLabelUnique(ValidateDictionaryDataLabelUniqueDto validateDictionaryDataLabelUniqueDto) {
        // 1. 转换DTO为业务对象
        //    将前端传来的DTO转换为内部业务处理对象
        ValidateDictionaryDataLabelUniqueBo validateDictionaryDataLabelUniqueBo = ValidateDictionaryDataLabelUniqueBo.of(validateDictionaryDataLabelUniqueDto);

        // 2. 查询字典数据标签是否存在
        //    校验数据库中是否已存在相同的标签（排除当前字典数据ID）
        Set<String> existingLabels = dictionaryDataTranslationService.selectExistsDictionaryDataLabels(validateDictionaryDataLabelUniqueBo);

        // 3. 返回校验结果
        //    如果列表不为空，表示字典数据标签已存在
        return ResponseVo.success(CollectionUtils.isNotEmpty(existingLabels));
    }

    /**
     * 校验字典数据值唯一性
     * 校验字典数据值是否已被使用
     *
     * @param validateDictionaryDataValueUniqueDto 字典数据值校验数据传输对象
     * @return 校验结果响应对象，true表示已存在，false表示不存在
     */
    @Transactional(readOnly = true)
    public ResponseVo<Boolean> validateDictionaryDataValueUnique(ValidateDictionaryDataValueUniqueDto validateDictionaryDataValueUniqueDto) {
        // 1. 转换DTO为业务对象
        //    将前端传来的DTO转换为内部业务处理对象
        ValidateDictionaryDataValueUniqueBo validateDictionaryDataValueUniqueBo = ValidateDictionaryDataValueUniqueBo.of(validateDictionaryDataValueUniqueDto);

        // 2. 查询字典数据值是否存在
        //    校验数据库中是否已存在相同的值（排除当前字典数据ID）
        boolean exists = dictionaryDataService.selectDictionaryDataValueExists(validateDictionaryDataValueUniqueBo);

        // 3. 返回校验结果
        //    返回字典数据值是否存在的布尔值
        return ResponseVo.success(exists);
    }

    /**
     * 创建字典数据
     * 创建新的字典数据记录及其翻译信息
     *
     * @param createDictionaryDataDto 创建字典数据数据传输对象
     * @return 创建结果响应对象
     * @throws BusinessException        当字典数据信息校验失败时抛出
     * @throws FieldValidationException 当字段校验失败时抛出
     */
    @Transactional
    public ResponseVo<Void> create(CreateDictionaryDataDto createDictionaryDataDto) {
        // 1. 校验字典数据信息
        //    校验字典数据的各项属性是否符合业务规则，包括值唯一性、标签唯一性、字典类型存在性等
        ValidateDictionaryDataBo validateDictionaryDataBo = ValidateDictionaryDataBo.of(createDictionaryDataDto);
        validateDictionaryDataInfo(validateDictionaryDataBo);

        // 2. 创建字典数据实体并保存
        //    根据DTO构建实体对象，保存到数据库，生成字典数据ID
        DictionaryDataEntity dictionaryDataEntity = DictionaryDataEntity.of(createDictionaryDataDto);
        dictionaryDataService.save(dictionaryDataEntity);

        // 3. 保存字典数据翻译信息
        //    为字典数据创建多语言翻译记录，关联到刚创建的字典数据ID
        dictionaryDataTranslationService.batchSave(dictionaryDataEntity.getId(), createDictionaryDataDto.getTranslations());

        // 4. 返回成功响应
        return ResponseVo.success();
    }

    /**
     * 批量删除字典数据
     * 删除多个字典数据记录及其关联的翻译信息
     *
     * @param dictionaryDataIds 要删除的字典数据ID列表
     * @return 删除结果响应对象
     */
    @Transactional
    public ResponseVo<Void> batchDelete(Set<Long> dictionaryDataIds) {
        // 1. 删除字典数据主表记录
        //    从字典数据表中删除指定ID的记录
        dictionaryDataService.removeByIds(dictionaryDataIds);

        // 2. 删除关联的字典数据翻译记录
        //    删除与这些字典数据关联的所有翻译记录
        dictionaryDataTranslationService.deleteByDictionaryDataIds(dictionaryDataIds);

        // 3. 返回成功响应
        return ResponseVo.success();
    }

    /**
     * 更新字典数据
     * 更新字典数据记录及其翻译信息
     *
     * @param updateDictionaryDataDto 更新字典数据数据传输对象
     * @return 更新结果响应对象
     * @throws BusinessException        当字典数据信息校验失败时抛出
     * @throws FieldValidationException 当字段校验失败时抛出
     */
    @Transactional
    public ResponseVo<Void> update(UpdateDictionaryDataDto updateDictionaryDataDto) {
        // 1. 校验字典数据信息
        //    校验字典数据的各项属性是否符合业务规则，包括值唯一性、标签唯一性、字典类型存在性等
        ValidateDictionaryDataBo validateDictionaryDataBo = ValidateDictionaryDataBo.of(updateDictionaryDataDto);
        validateDictionaryDataInfo(validateDictionaryDataBo);

        // 2. 获取字典数据ID
        //    从DTO中获取要更新的字典数据ID
        Long dictionaryDataId = updateDictionaryDataDto.getId();

        // 3. 更新字典数据实体
        //    根据DTO构建实体对象，更新数据库中的记录
        DictionaryDataEntity dictionaryDataEntity = DictionaryDataEntity.of(updateDictionaryDataDto);
        dictionaryDataService.update(dictionaryDataEntity, dictionary_data.id.eq(dictionaryDataId));

        // 4. 更新字典数据翻译信息
        //    更新与该字典数据关联的多语言翻译记录
        dictionaryDataTranslationService.batchUpdate(dictionaryDataId, updateDictionaryDataDto.getTranslations());

        // 5. 返回成功响应
        return ResponseVo.success();
    }

    /**
     * 分页查询字典数据列表
     * 分页查询字典数据列表，支持条件过滤和排序
     *
     * @param enquiryDictionaryDataPageDto 查询字典数据分页数据传输对象
     * @return 字典数据分页数据响应对象
     */
    @Transactional(readOnly = true)
    public ResponseVo<PageVo<DictionaryDataPageVo>> enquiryPage(EnquiryDictionaryDataPageDto enquiryDictionaryDataPageDto) {
        // 1. 调用字典数据服务执行分页查询
        //    根据查询条件，获取分页数据结果
        PageVo<DictionaryDataPageVo> dictionaryDataPageVo = dictionaryDataService.enquiryPage(enquiryDictionaryDataPageDto);

        // 2. 封装查询结果为响应对象
        //    将分页数据包装为统一的响应格式
        return ResponseVo.success(dictionaryDataPageVo);
    }

    /**
     * 查询字典数据详情
     * 根据ID查询字典数据详细信息，包括基本信息和翻译信息
     *
     * @param id 字典数据ID
     * @return 字典数据详情响应对象
     * @throws BusinessException 当字典数据不存在时抛出
     */
    @Transactional(readOnly = true)
    public ResponseVo<DictionaryDataDetailsVo> enquiryDetails(Long id) {
        // 1. 调用字典数据服务查询详情信息
        //    根据ID查询字典数据的详细信息，包括基本信息和翻译信息
        DictionaryDataDetailsVo dictionaryDataDetailsVo = dictionaryDataService.enquiryDetails(id);

        // 2. 校验查询结果是否存在
        //    如果查询结果为空，表示字典数据不存在，抛出业务异常
        if (Objects.isNull(dictionaryDataDetailsVo)) {
            log.warn("Dictionary data [{}] not found when enquiring details", id);
            throw new BusinessException("form.dictionaryData.dictionaryDataNotFound");
        }

        // 3. 封装查询结果为响应对象
        //    将详情数据包装为统一的响应格式
        return ResponseVo.success(dictionaryDataDetailsVo);
    }

    /**
     * 查询字典数据选项列表
     * 根据字典类型代码查询字典数据选项列表，用于前端下拉框等组件
     * <p>
     * 业务流程：
     * 1. 调用字典数据服务查询选项列表
     * 2. 封装查询结果为响应对象
     *
     * @param dictionaryTypeCode 字典类型代码
     * @return 字典数据选项列表响应对象
     */
    @Transactional(readOnly = true)
    public ResponseVo<List<DictionaryDataListVo>> enquiryList(String dictionaryTypeCode) {
        // 1. 调用字典数据服务查询选项列表
        //    根据字典类型代码，获取该类型下的所有可用字典数据
        List<DictionaryDataListVo> dictionaryDataList = dictionaryDataService.enquiryList(dictionaryTypeCode);

        // 2. 封装查询结果为响应对象
        //    将列表数据包装为统一的响应格式
        return ResponseVo.success(dictionaryDataList);
    }

    /**
     * 校验字典数据信息
     * 校验字典数据的各项属性是否符合规则
     *
     * @param validateDictionaryDataBo 校验字典数据业务对象
     * @throws BusinessException        当字典数据信息校验失败时抛出
     * @throws FieldValidationException 当字段校验失败时抛出，包含具体的字段错误信息
     */
    private void validateDictionaryDataInfo(ValidateDictionaryDataBo validateDictionaryDataBo) {
        // 1. 如果是更新操作，校验字典数据是否存在
        //    更新操作需要确保要更新的字典数据记录存在
        Long dictionaryDataId = validateDictionaryDataBo.getId();
        if (Objects.nonNull(dictionaryDataId)) {
            boolean dictionaryDataExists = dictionaryDataService.selectDictionaryDataExists(dictionaryDataId);

            if (!dictionaryDataExists) {
                log.warn("Dictionary data [{}] not found when validating dictionary data info", dictionaryDataId);
                throw new BusinessException("form.dictionaryData.dictionaryDataNotFound");
            }
        }

        // 2. 校验翻译数据
        //    校验翻译数据的语言代码是否有效，是否包含必要的语言
        TranslationUtils.validateTranslations(
                validateDictionaryDataBo.getTranslations(),
                DictionaryDataTranslationBo::getLanguageCode
        );

        // 3. 校验字典数据状态
        //    校验字典数据状态是否是有效的状态值
        dictionaryDataService.validateDictionaryDataValue(
                SystemConstant.DICTIONARY_CODE_DICTIONARY_DATA_STATUS,
                validateDictionaryDataBo.getDictionaryDataStatus(),
                "dictionaryDataStatus",
                "form.dictionaryData.invalidDictionaryDataStatus"
        );

        // 4. 校验字典类型代码是否存在
        //    确保字典数据关联的字典类型是存在的
        String dictionaryTypeCode = validateDictionaryDataBo.getDictionaryTypeCode();
        boolean dictionaryTypeExists = dictionaryTypeService.selectDictionaryTypeCodeExists(dictionaryTypeCode);
        if (!dictionaryTypeExists) {
            log.warn("Dictionary type code [{}] not found when validating dictionary data info", dictionaryTypeCode);
            throw new FieldValidationException("dictionaryTypeCode", "form.dictionaryData.invalidDictionaryType");
        }

        // 5. 校验字典数据标签是否唯一
        //    确保同一字典类型下不存在相同的标签
        ValidateDictionaryDataLabelUniqueBo validateDictionaryDataLabelUniqueBo = ValidateDictionaryDataLabelUniqueBo.of(validateDictionaryDataBo);
        Set<String> existingLabels = dictionaryDataTranslationService.selectExistsDictionaryDataLabels(validateDictionaryDataLabelUniqueBo);

        if (CollectionUtils.isNotEmpty(existingLabels)) {
            log.warn("Dictionary data labels already exists: [{}]", String.join(", ", existingLabels));
            throw new FieldValidationException("translations", "form.dictionaryData.labelsAlreadyExists", String.join(", ", existingLabels));
        }

        // 6. 校验字典数据值是否唯一（在同一字典类型下）
        //    确保同一字典类型下不存在相同的值
        ValidateDictionaryDataValueUniqueBo validateDictionaryDataValueUniqueBo = ValidateDictionaryDataValueUniqueBo.of(validateDictionaryDataBo);
        boolean valueExists = dictionaryDataService.selectDictionaryDataValueExists(validateDictionaryDataValueUniqueBo);
        if (valueExists) {
            log.warn("Dictionary data value already exists: [{}]", validateDictionaryDataValueUniqueBo.getValue());
            throw new FieldValidationException("value", "form.dictionaryData.valueAlreadyExists");
        }
    }

}
