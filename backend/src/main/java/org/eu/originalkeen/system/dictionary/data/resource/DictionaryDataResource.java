package org.eu.originalkeen.system.dictionary.data.resource;

import org.eu.originalkeen.core.annotation.OperateLog;
import org.eu.originalkeen.core.domain.vo.PageVo;
import org.eu.originalkeen.core.domain.vo.ResponseVo;
import org.eu.originalkeen.core.enums.OperateType;
import org.eu.originalkeen.system.dictionary.data.domain.dto.*;
import org.eu.originalkeen.system.dictionary.data.domain.vo.DictionaryDataDetailsVo;
import org.eu.originalkeen.system.dictionary.data.domain.vo.DictionaryDataListVo;
import org.eu.originalkeen.system.dictionary.data.domain.vo.DictionaryDataPageVo;
import org.eu.originalkeen.system.dictionary.data.manager.DictionaryDataManager;
import jakarta.annotation.Resource;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Set;

/**
 * 字典数据资源控制器
 * 提供字典数据管理相关的REST API接口
 */
@CrossOrigin
@Validated
@RestController
@RequestMapping("/v1/system/dictionary-data")
public class DictionaryDataResource {

    /**
     * 字典数据管理器
     * 提供字典数据相关的业务处理功能，整合字典数据服务和字典数据翻译服务
     */
    @Resource
    private DictionaryDataManager dictionaryDataManager;

    /**
     * 校验字典数据标签唯一性
     * 校验字典数据标签是否已被使用
     *
     * @param validateDictionaryDataLabelUniqueDto 字典数据标签校验数据传输对象
     * @return 校验结果响应实体，true表示已存在，false表示不存在
     */
    @GetMapping("/label/unique")
    @PreAuthorize("hasAuthority('system:dictionary-data:validate-label')")
    public ResponseEntity<ResponseVo<Boolean>> validateDictionaryDataLabelUnique(
            @Validated ValidateDictionaryDataLabelUniqueDto validateDictionaryDataLabelUniqueDto
    ) {
        return ResponseEntity.ok(dictionaryDataManager.validateDictionaryDataLabelUnique(validateDictionaryDataLabelUniqueDto));
    }

    /**
     * 校验字典数据值唯一性
     * 校验字典数据值是否已被使用
     *
     * @param validateDictionaryDataValueUniqueDto 字典数据值校验数据传输对象
     * @return 校验结果响应实体，true表示已存在，false表示不存在
     */
    @GetMapping("/value/unique")
    @PreAuthorize("hasAuthority('system:dictionary-data:validate-value')")
    public ResponseEntity<ResponseVo<Boolean>> validateDictionaryDataValueUnique(
            @Validated ValidateDictionaryDataValueUniqueDto validateDictionaryDataValueUniqueDto
    ) {
        return ResponseEntity.ok(dictionaryDataManager.validateDictionaryDataValueUnique(validateDictionaryDataValueUniqueDto));
    }

    /**
     * 创建字典数据
     * 创建新的字典数据记录及其翻译信息
     *
     * @param createDictionaryDataDto 创建字典数据数据传输对象
     * @return 创建结果响应实体
     */
    @PostMapping
    @PreAuthorize("hasAuthority('system:dictionary-data:create')")
    @OperateLog(title = "Create Dictionary Data", operateType = OperateType.INSERT)
    public ResponseEntity<ResponseVo<Void>> create(@RequestBody @Validated CreateDictionaryDataDto createDictionaryDataDto) {
        return ResponseEntity.ok(dictionaryDataManager.create(createDictionaryDataDto));
    }

    /**
     * 批量删除字典数据
     * 删除多个字典数据记录及其关联的翻译信息
     *
     * @param dictionaryDataIds 要删除的字典数据ID列表
     * @return 删除结果响应实体
     */
    @DeleteMapping
    @PreAuthorize("hasAuthority('system:dictionary-data:delete')")
    @OperateLog(title = "Batch Delete Dictionary Data", operateType = OperateType.DELETE)
    public ResponseEntity<ResponseVo<Void>> batchDelete(@RequestParam("dictionaryDataIds") @NotEmpty(message = "{form.dictionaryData.dictionaryDataIdListIsRequired}") Set<Long> dictionaryDataIds) {
        return ResponseEntity.ok(dictionaryDataManager.batchDelete(dictionaryDataIds));
    }

    /**
     * 更新字典数据
     * 更新字典数据记录及其翻译信息
     *
     * @param updateDictionaryDataDto 更新字典数据数据传输对象
     * @return 更新结果响应实体
     */
    @PutMapping
    @PreAuthorize("hasAuthority('system:dictionary-data:update')")
    @OperateLog(title = "Update Dictionary Data", operateType = OperateType.UPDATE)
    public ResponseEntity<ResponseVo<Void>> update(@RequestBody @Validated UpdateDictionaryDataDto updateDictionaryDataDto) {
        return ResponseEntity.ok(dictionaryDataManager.update(updateDictionaryDataDto));
    }

    /**
     * 查询字典数据分页
     * 分页查询字典数据列表，支持条件过滤和排序
     *
     * @param enquiryDictionaryDataPageDto 查询字典数据分页数据传输对象
     * @return 字典数据分页数据响应实体
     */
    @GetMapping("/page")
    @PreAuthorize("hasAuthority('system:dictionary-data:page')")
    public ResponseEntity<ResponseVo<PageVo<DictionaryDataPageVo>>> enquiryPage(EnquiryDictionaryDataPageDto enquiryDictionaryDataPageDto) {
        return ResponseEntity.ok(dictionaryDataManager.enquiryPage(enquiryDictionaryDataPageDto));
    }

    /**
     * 查询字典数据详情
     * 根据ID查询字典数据详细信息，包括基本信息和翻译信息
     *
     * @param id 字典数据ID
     * @return 字典数据详情响应实体
     */
    @GetMapping("/{id}")
    @PreAuthorize("hasAuthority('system:dictionary-data:details')")
    public ResponseEntity<ResponseVo<DictionaryDataDetailsVo>> enquiryDetails(@PathVariable("id") Long id) {
        return ResponseEntity.ok(dictionaryDataManager.enquiryDetails(id));
    }

    /**
     * 查询字典数据选项列表
     * 根据字典类型代码查询字典数据选项列表，用于前端下拉框等组件
     *
     * @param dictionaryTypeCode 字典类型代码
     * @return 字典数据选项列表响应实体
     */
    @GetMapping("/list/{dictionaryTypeCode}")
    @PreAuthorize("hasAuthority('system:dictionary-data:list')")
    public ResponseEntity<ResponseVo<List<DictionaryDataListVo>>> enquiryList(
            @PathVariable("dictionaryTypeCode") @NotBlank(message = "{form.dictionaryType.dictionaryTypeCodeIsRequired}") String dictionaryTypeCode
    ) {
        return ResponseEntity.ok(dictionaryDataManager.enquiryList(dictionaryTypeCode));
    }

}
