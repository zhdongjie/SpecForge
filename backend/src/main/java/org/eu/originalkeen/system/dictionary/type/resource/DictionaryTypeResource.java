package org.eu.originalkeen.system.dictionary.type.resource;

import org.eu.originalkeen.core.annotation.OperateLog;
import org.eu.originalkeen.core.domain.vo.PageVo;
import org.eu.originalkeen.core.domain.vo.ResponseVo;
import org.eu.originalkeen.core.enums.OperateType;
import org.eu.originalkeen.system.dictionary.type.domain.dto.*;
import org.eu.originalkeen.system.dictionary.type.domain.vo.DictionaryTypeDetailsVo;
import org.eu.originalkeen.system.dictionary.type.domain.vo.DictionaryTypeListVo;
import org.eu.originalkeen.system.dictionary.type.domain.vo.DictionaryTypePageVo;
import org.eu.originalkeen.system.dictionary.type.manager.DictionaryTypeManager;
import jakarta.annotation.Resource;
import jakarta.validation.constraints.NotEmpty;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Set;

/**
 * 字典类型资源控制器
 * 提供字典类型管理相关的REST API接口
 */
@CrossOrigin
@Validated
@RestController
@RequestMapping("/v1/system/dictionary-type")
public class DictionaryTypeResource {


    /**
     * 字典类型管理器
     * 负责协调字典类型相关的业务逻辑处理和事务管理
     */
    @Resource
    private DictionaryTypeManager dictionaryTypeManager;

    /**
     * 校验字典类型名称唯一性
     * 校验字典类型名称是否已被使用
     *
     * @param validateDictionaryTypeNameUniqueDto 字典类型名称校验数据传输对象
     * @return 校验结果响应实体，true表示可用，false表示已存在
     */
    @GetMapping("/dictionary-type-name/unique")
    @PreAuthorize("hasAuthority('system:dictionary-type:validate-dictionary-type-name')")
    public ResponseEntity<ResponseVo<Boolean>> validateDictionaryTypeNameUnique(
            @Validated ValidateDictionaryTypeNameUniqueDto validateDictionaryTypeNameUniqueDto
    ) {
        return ResponseEntity.ok(dictionaryTypeManager.validateDictionaryTypeNameUnique(validateDictionaryTypeNameUniqueDto));
    }

    /**
     * 校验字典类型代码唯一性
     * 校验字典类型代码是否已被使用
     *
     * @param validateDictionaryTypeCodeUniqueDto 字典类型代码校验数据传输对象
     * @return 校验结果响应实体，true表示可用，false表示已存在
     */
    @GetMapping("/dictionary-type-code/unique")
    @PreAuthorize("hasAuthority('system:dictionary-type:validate-dictionary-type-code')")
    public ResponseEntity<ResponseVo<Boolean>> validateDictionaryTypeCodeUnique(
            @Validated ValidateDictionaryTypeCodeUniqueDto validateDictionaryTypeCodeUniqueDto
    ) {
        return ResponseEntity.ok(dictionaryTypeManager.validateDictionaryTypeCodeUnique(validateDictionaryTypeCodeUniqueDto));
    }

    /**
     * 创建字典类型
     * 创建新的字典类型
     *
     * @param createDictionaryTypeDto 创建字典类型数据传输对象
     * @return 创建结果响应实体
     */
    @PostMapping
    @PreAuthorize("hasAuthority('system:dictionary-type:create')")
    @OperateLog(title = "Create Dictionary Type", operateType = OperateType.INSERT)
    public ResponseEntity<ResponseVo<Void>> create(@RequestBody @Validated CreateDictionaryTypeDto createDictionaryTypeDto) {
        return ResponseEntity.ok(dictionaryTypeManager.create(createDictionaryTypeDto));
    }

    /**
     * 批量删除字典类型
     * 删除多个字典类型
     *
     * @param dictionaryTypeIds 要删除的字典类型ID列表
     * @return 删除结果响应实体
     */
    @DeleteMapping
    @PreAuthorize("hasAuthority('system:dictionary-type:delete')")
    @OperateLog(title = "Batch Delete Dictionary Types", operateType = OperateType.DELETE)
    public ResponseEntity<ResponseVo<Void>> batchDelete(@RequestParam("dictionaryTypeIds") @NotEmpty(message = "{form.dictionaryType.dictionaryTypeIdListIsRequired}") Set<Long> dictionaryTypeIds) {
        return ResponseEntity.ok(dictionaryTypeManager.batchDelete(dictionaryTypeIds));
    }

    /**
     * 更新字典类型
     * 更新字典类型信息
     *
     * @param updateDictionaryTypeDto 更新字典类型数据传输对象
     * @return 更新结果响应实体
     */
    @PutMapping
    @PreAuthorize("hasAuthority('system:dictionary-type:update')")
    @OperateLog(title = "Update Dictionary Type", operateType = OperateType.UPDATE)
    public ResponseEntity<ResponseVo<Void>> update(@RequestBody @Validated UpdateDictionaryTypeDto updateDictionaryTypeDto) {
        return ResponseEntity.ok(dictionaryTypeManager.update(updateDictionaryTypeDto));
    }

    /**
     * 查询字典类型分页
     * 分页查询字典类型列表
     *
     * @param enquiryDictionaryTypePageDto 查询字典类型分页数据传输对象
     * @return 字典类型分页数据响应实体
     */
    @GetMapping("/page")
    @PreAuthorize("hasAuthority('system:dictionary-type:page')")
    public ResponseEntity<ResponseVo<PageVo<DictionaryTypePageVo>>> enquiryPage(EnquiryDictionaryTypePageDto enquiryDictionaryTypePageDto) {
        return ResponseEntity.ok(dictionaryTypeManager.enquiryPage(enquiryDictionaryTypePageDto));
    }

    /**
     * 查询字典类型详情
     * 根据ID查询字典类型详细信息
     *
     * @param id 字典类型ID
     * @return 字典类型详情响应实体
     */
    @GetMapping("/{id}")
    @PreAuthorize("hasAuthority('system:dictionary-type:details')")
    public ResponseEntity<ResponseVo<DictionaryTypeDetailsVo>> enquiryDetails(@PathVariable("id") Long id) {
        return ResponseEntity.ok(dictionaryTypeManager.enquiryDetails(id));
    }

    /**
     * 查询字典类型列表
     * 查询所有字典类型的列表
     *
     * @return 字典类型列表响应实体
     */
    @GetMapping("/list")
    @PreAuthorize("hasAuthority('system:dictionary-type:list')")
    public ResponseEntity<ResponseVo<List<DictionaryTypeListVo>>> enquiryList() {
        return ResponseEntity.ok(dictionaryTypeManager.enquiryList());
    }

} 
