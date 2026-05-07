package org.eu.originalkeen.system.dictionary.type.manager;

import org.eu.originalkeen.core.constant.SystemConstant;
import org.eu.originalkeen.core.domain.vo.PageVo;
import org.eu.originalkeen.core.domain.vo.ResponseVo;
import org.eu.originalkeen.core.exception.BusinessException;
import org.eu.originalkeen.core.exception.business.FieldValidationException;
import org.eu.originalkeen.system.dictionary.data.service.DictionaryDataService;
import org.eu.originalkeen.system.dictionary.type.domain.bo.ValidateDictionaryTypeBo;
import org.eu.originalkeen.system.dictionary.type.domain.bo.ValidateDictionaryTypeCodeUniqueBo;
import org.eu.originalkeen.system.dictionary.type.domain.bo.ValidateDictionaryTypeNameUniqueBo;
import org.eu.originalkeen.system.dictionary.type.domain.dto.*;
import org.eu.originalkeen.system.dictionary.type.domain.entity.DictionaryTypeEntity;
import org.eu.originalkeen.system.dictionary.type.domain.vo.DictionaryTypeDetailsVo;
import org.eu.originalkeen.system.dictionary.type.domain.vo.DictionaryTypeListVo;
import org.eu.originalkeen.system.dictionary.type.domain.vo.DictionaryTypePageVo;
import org.eu.originalkeen.system.dictionary.type.service.DictionaryTypeService;
import org.eu.originalkeen.system.dictionary.type.service.DictionaryTypeTranslationService;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.collections4.CollectionUtils;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Objects;
import java.util.Set;

import static org.eu.originalkeen.system.dictionary.type.domain.entity.table.DictionaryTypeTableDef.dictionary_type;

/**
 * 字典类型管理器
 * 提供字典类型相关的业务处理功能，整合字典类型服务、字典类型翻译服务和字典数据服务等
 * <p>
 * 主要功能：
 * 1. 字典类型的创建、更新、删除和查询
 * 2. 字典类型与翻译的关联管理
 * 3. 字典类型信息的校验逻辑
 * 4. 字典类型的业务规则处理
 * 5. 字典类型与字典数据的关联校验
 * <p>
 * 该管理器作为字典类型模块的核心组件，负责处理控制层与服务层之间的交互
 * 封装了复杂的业务逻辑和校验规则，确保数据的一致性和完整性
 * 使用@Slf4j注解提供日志记录功能
 */
@Slf4j
@Component
public class DictionaryTypeManager {

    /**
     * 字典类型服务
     * 用于管理字典类型基础数据的增删改查操作
     * 提供字典类型的存在性校验、代码唯一性校验和使用情况查询等功能
     */
    @Resource
    private DictionaryTypeService dictionaryTypeService;

    /**
     * 字典类型翻译服务
     * 用于管理字典类型的多语言翻译数据
     * 提供字典类型名称唯一性校验、翻译记录的创建、更新和删除等功能
     */
    @Resource
    private DictionaryTypeTranslationService dictionaryTypeTranslationService;

    /**
     * 字典数据服务
     * 用于管理字典数据信息和校验
     * 提供字典数据值的有效性校验，确保字典类型状态等引用的字典值有效
     */
    @Resource
    private DictionaryDataService dictionaryDataService;

    /**
     * 校验字典类型名称是否唯一
     * 校验指定的字典类型名称在系统中是否已经存在
     *
     * @param validateDictionaryTypeNameUniqueDto 字典类型名称唯一性校验的DTO对象
     * @return 包含字典类型名称是否存在的响应对象，true表示已存在，false表示不存在
     */
    @Transactional(readOnly = true)
    public ResponseVo<Boolean> validateDictionaryTypeNameUnique(ValidateDictionaryTypeNameUniqueDto validateDictionaryTypeNameUniqueDto) {
        // 1. 转换DTO为业务对象
        //    将前端传来的DTO转换为内部业务处理对象
        ValidateDictionaryTypeNameUniqueBo validateDictionaryTypeNameUniqueBo = ValidateDictionaryTypeNameUniqueBo.of(validateDictionaryTypeNameUniqueDto);

        // 2. 查询字典类型名称是否存在
        //    调用服务层方法校验数据库中是否已存在相同的字典类型名称
        Set<String> existsDictionaryTypeNames = dictionaryTypeTranslationService.selectExistsDictionaryTypeNames(validateDictionaryTypeNameUniqueBo);

        // 3. 返回校验结果
        //    如果列表不为空，表示字典类型名称已存在
        return ResponseVo.success(CollectionUtils.isNotEmpty(existsDictionaryTypeNames));
    }

    /**
     * 校验字典类型代码是否唯一
     * 校验指定的字典类型代码在系统中是否已经存在
     *
     * @param validateDictionaryTypeCodeUniqueDto 字典类型代码唯一性校验的DTO对象
     * @return 包含字典类型代码是否存在的响应对象，true表示已存在，false表示不存在
     */
    @Transactional(readOnly = true)
    public ResponseVo<Boolean> validateDictionaryTypeCodeUnique(ValidateDictionaryTypeCodeUniqueDto validateDictionaryTypeCodeUniqueDto) {
        // 1. 转换DTO为业务对象
        //    将前端传来的DTO转换为内部业务处理对象
        ValidateDictionaryTypeCodeUniqueBo validateDictionaryTypeCodeUniqueBo = ValidateDictionaryTypeCodeUniqueBo.of(validateDictionaryTypeCodeUniqueDto);

        // 2. 查询字典类型代码是否存在
        //    调用服务层方法校验数据库中是否已存在相同的字典类型代码
        boolean exists = dictionaryTypeService.selectDictionaryTypeCodeExists(validateDictionaryTypeCodeUniqueBo);

        // 3. 返回校验结果
        //    封装为统一的响应对象返回给前端
        return ResponseVo.success(exists);
    }

    /**
     * 创建字典类型
     * 在系统中创建一个新的字典类型记录，并创建对应的翻译记录
     *
     * @param createDictionaryTypeDto 创建字典类型的DTO对象，包含字典类型的各项属性
     * @return 创建结果的响应对象
     * @throws BusinessException        当字典类型状态无效时抛出
     * @throws FieldValidationException 当字典类型代码或名称已存在时抛出
     */
    @Transactional
    public ResponseVo<Void> create(CreateDictionaryTypeDto createDictionaryTypeDto) {
        // 1. 转换DTO为校验业务对象
        //    准备用于校验的业务对象
        ValidateDictionaryTypeBo validateDictionaryTypeBo = ValidateDictionaryTypeBo.of(createDictionaryTypeDto);

        // 2. 校验字典类型信息
        //    校验字典类型名称唯一性、代码唯一性和状态有效性
        validateDictionaryTypeInfo(validateDictionaryTypeBo);

        // 3. 创建字典类型实体
        //    将DTO转换为实体对象
        DictionaryTypeEntity dictionaryTypeEntity = DictionaryTypeEntity.of(createDictionaryTypeDto);

        // 4. 保存字典类型
        //    调用服务层方法保存到数据库
        dictionaryTypeService.save(dictionaryTypeEntity);

        // 5. 保存字典类型翻译
        //    创建字典类型的多语言翻译记录
        dictionaryTypeTranslationService.createDictionaryTypeTranslations(dictionaryTypeEntity.getId(), createDictionaryTypeDto.getTranslations());

        // 6. 返回成功响应
        //    操作成功完成，返回统一的成功响应
        return ResponseVo.success();
    }

    /**
     * 批量删除字典类型
     * 删除指定的一组字典类型及其翻译
     *
     * @param dictionaryTypeIds 要删除的字典类型ID列表
     * @return 删除结果的响应对象
     * @throws BusinessException 当字典类型正在被字典数据使用时抛出，返回被使用的字典类型代码
     */
    @Transactional
    public ResponseVo<Void> batchDelete(Set<Long> dictionaryTypeIds) {
        // 1. 校验字典类型是否在字典数据中被使用
        //    查询被使用的字典类型代码，防止删除已被使用的字典类型
        Set<String> usedDictionaryTypeCodes = dictionaryTypeService.selectUsedDictionaryTypeCodes(dictionaryTypeIds);

        // 2. 如果有字典类型被使用，抛出异常
        //    记录警告日志并抛出业务异常，提示用户无法删除
        if (CollectionUtils.isNotEmpty(usedDictionaryTypeCodes)) {
            log.warn("Dictionary types are in use and cannot be deleted: [{}]", String.join(", ", usedDictionaryTypeCodes));
            throw new BusinessException("form.dictionaryType.unableDeleteDictionaryTypes", String.join(", ", usedDictionaryTypeCodes));
        }

        // 3. 删除字典类型
        //    调用服务层方法批量删除字典类型记录
        dictionaryTypeService.removeByIds(dictionaryTypeIds);

        // 4. 删除字典类型翻译
        //    删除关联的多语言翻译记录
        dictionaryTypeTranslationService.deleteDictionaryTypeTranslations(dictionaryTypeIds);

        // 5. 返回成功响应
        //    操作成功完成，返回统一的成功响应
        return ResponseVo.success();
    }

    /**
     * 更新字典类型
     * 更新指定字典类型的各项属性，并更新对应的翻译记录
     *
     * @param updateDictionaryTypeDto 更新字典类型的DTO对象，包含要更新的字典类型属性
     * @return 更新结果的响应对象
     * @throws BusinessException        当字典类型不存在或字典类型状态无效时抛出
     * @throws FieldValidationException 当字典类型代码或名称与其他字典类型冲突时抛出
     */
    @Transactional
    public ResponseVo<Void> update(UpdateDictionaryTypeDto updateDictionaryTypeDto) {
        // 1. 转换DTO为校验业务对象
        //    准备用于校验的业务对象
        ValidateDictionaryTypeBo validateDictionaryTypeBo = ValidateDictionaryTypeBo.of(updateDictionaryTypeDto);

        // 2. 校验字典类型信息
        //    校验字典类型存在性、名称唯一性、代码唯一性和状态有效性
        validateDictionaryTypeInfo(validateDictionaryTypeBo);

        // 3. 创建字典类型实体
        //    将DTO转换为实体对象
        DictionaryTypeEntity dictionaryTypeEntity = DictionaryTypeEntity.of(updateDictionaryTypeDto);

        // 4. 获取字典类型ID
        //    用于更新操作的条件
        Long dictionaryTypeId = updateDictionaryTypeDto.getId();

        // 5. 更新字典类型
        //    调用服务层方法更新数据库记录
        dictionaryTypeService.update(dictionaryTypeEntity, dictionary_type.id.eq(dictionaryTypeId));

        // 6. 更新字典类型翻译
        //    更新关联的多语言翻译记录
        dictionaryTypeTranslationService.updateDictionaryTypeTranslations(dictionaryTypeId, updateDictionaryTypeDto.getTranslations());

        // 7. 返回成功响应
        //    操作成功完成，返回统一的成功响应
        return ResponseVo.success();
    }

    /**
     * 分页查询字典类型列表
     * 根据查询条件分页获取字典类型列表
     *
     * @param enquiryDictionaryTypePageDto 字典类型分页查询的DTO对象，包含分页参数和查询条件
     * @return 包含字典类型分页数据的响应对象
     */
    @Transactional(readOnly = true)
    public ResponseVo<PageVo<DictionaryTypePageVo>> enquiryPage(EnquiryDictionaryTypePageDto enquiryDictionaryTypePageDto) {
        // 1. 调用服务层查询分页数据
        //    执行分页查询并获取结果
        PageVo<DictionaryTypePageVo> dictionaryTypePageVo = dictionaryTypeService.enquiryPage(enquiryDictionaryTypePageDto);

        // 2. 返回查询结果
        //    封装为统一的响应对象返回给前端
        return ResponseVo.success(dictionaryTypePageVo);
    }

    /**
     * 查询字典类型详情
     * 获取指定字典类型ID的详细信息，包括多语言翻译
     *
     * @param id 要查询的字典类型ID
     * @return 包含字典类型详细信息的响应对象
     * @throws BusinessException 当字典类型不存在时抛出
     */
    @Transactional(readOnly = true)
    public ResponseVo<DictionaryTypeDetailsVo> enquiryDetails(Long id) {
        // 1. 调用服务层查询详情
        //    根据ID查询字典类型详情
        DictionaryTypeDetailsVo dictionaryTypeDetailsVo = dictionaryTypeService.enquiryDetails(id);

        // 2. 校验查询结果是否存在
        //    如果查询结果为空，记录警告日志并抛出异常
        if (Objects.isNull(dictionaryTypeDetailsVo)) {
            log.warn("Dictionary type [{}] not found when enquiring details", id);
            throw new BusinessException("form.dictionaryType.dictionaryTypeNotFound");
        }

        // 3. 返回查询结果
        //    封装为统一的响应对象返回给前端
        return ResponseVo.success(dictionaryTypeDetailsVo);
    }

    /**
     * 查询字典类型列表
     * 查询所有字典类型的列表
     *
     * @return 字典类型列表响应对象
     */
    @Transactional(readOnly = true)
    public ResponseVo<List<DictionaryTypeListVo>> enquiryList() {
        // 1. 调用服务层查询列表数据
        //    查询所有启用状态的字典类型列表
        List<DictionaryTypeListVo> dictionaryTypeListVos = dictionaryTypeService.enquiryList();

        // 2. 返回查询结果
        //    封装为统一的响应对象返回给前端
        return ResponseVo.success(dictionaryTypeListVos);
    }

    /**
     * 校验字典类型信息
     * 校验字典类型的存在性、代码唯一性、名称唯一性和状态有效性
     *
     * @param validateDictionaryTypeBo 校验字典类型业务对象
     * @throws BusinessException        当字典类型不存在或字典类型状态无效时抛出
     * @throws FieldValidationException 当字典类型代码或名称已存在时抛出
     */
    private void validateDictionaryTypeInfo(ValidateDictionaryTypeBo validateDictionaryTypeBo) {
        Long dictionaryTypeId = validateDictionaryTypeBo.getId();

        // 1. 校验字典类型是否存在（更新时）
        //    如果是更新操作，需要校验要更新的字典类型记录是否存在
        if (Objects.nonNull(dictionaryTypeId)) {
            boolean dictionaryTypeExists = dictionaryTypeService.selectDictionaryTypeExists(dictionaryTypeId);
            if (!dictionaryTypeExists) {
                log.warn("Dictionary type [{}] not found when validating dictionary type info", dictionaryTypeId);
                throw new BusinessException("form.dictionaryType.dictionaryTypeNotFound");
            }
        }

        // 2. 校验字典类型状态
        //    校验状态值是否在字典中存在
        dictionaryDataService.validateDictionaryDataValue(
                SystemConstant.DICTIONARY_CODE_DICTIONARY_TYPE_STATUS,
                validateDictionaryTypeBo.getDictionaryTypeStatus(),
                "dictionaryTypeStatus",
                "form.dictionaryType.invalidDictionaryTypeStatus"
        );

        // 3. 校验字典类型代码唯一性
        //    校验代码是否已被其他记录使用
        ValidateDictionaryTypeCodeUniqueBo validateDictionaryTypeCodeUniqueBo = ValidateDictionaryTypeCodeUniqueBo.of(validateDictionaryTypeBo);
        boolean codeExists = dictionaryTypeService.selectDictionaryTypeCodeExists(validateDictionaryTypeCodeUniqueBo);
        if (codeExists) {
            log.warn("Dictionary type code [{}] already exists", validateDictionaryTypeCodeUniqueBo.getDictionaryTypeCode());
            throw new FieldValidationException("dictionaryTypeCode", "form.dictionaryType.dictionaryTypeCodeAlreadyExists");
        }

        // 4. 校验字典类型名称唯一性
        //    校验名称是否已被其他记录使用
        ValidateDictionaryTypeNameUniqueBo validateDictionaryTypeNameUniqueBo = ValidateDictionaryTypeNameUniqueBo.of(validateDictionaryTypeBo);
        Set<String> existsDictionaryTypeNames = dictionaryTypeTranslationService.selectExistsDictionaryTypeNames(validateDictionaryTypeNameUniqueBo);
        if (CollectionUtils.isNotEmpty(existsDictionaryTypeNames)) {
            log.warn("Dictionary type names [{}] already exist", String.join(", ", existsDictionaryTypeNames));
            throw new FieldValidationException("translations", "form.dictionaryType.dictionaryTypeNameAlreadyExists", String.join(", ", existsDictionaryTypeNames));
        }
    }

}
