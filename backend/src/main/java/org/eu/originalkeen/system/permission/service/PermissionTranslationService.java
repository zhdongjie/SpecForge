package org.eu.originalkeen.system.permission.service;

import com.mybatisflex.core.service.IService;
import org.eu.originalkeen.system.permission.domain.bo.ValidatePermissionNameUniqueBo;
import org.eu.originalkeen.system.permission.domain.dto.PermissionTranslationDto;
import org.eu.originalkeen.system.permission.domain.entity.PermissionTranslationEntity;

import java.util.List;
import java.util.Set;

/**
 * 权限翻译服务接口
 * 提供权限翻译的业务逻辑方法
 */
public interface PermissionTranslationService extends IService<PermissionTranslationEntity> {

    /**
     * 查询权限名称是否存在
     * 根据权限名称校验是否已存在记录
     *
     * @param validatePermissionNameUniqueBo 权限名称唯一性校验业务对象
     * @return 存在返回true，不存在返回false
     */
    Set<String> selectExistsPermissionNames(ValidatePermissionNameUniqueBo validatePermissionNameUniqueBo);

    /**
     * 创建权限翻译
     * 创建新的权限翻译记录
     *
     * @param permissionId 权限ID
     * @param translations 权限翻译DTO列表
     */
    void createPermissionTranslations(Long permissionId, List<PermissionTranslationDto> translations);

    /**
     * 删除权限翻译
     * 删除指定权限ID列表的权限翻译记录
     *
     * @param permissionIds 权限ID列表
     */
    void deletePermissionTranslations(Set<Long> permissionIds);

    /**
     * 更新权限翻译
     * 更新指定权限的翻译记录
     *
     * @param permissionId 权限ID
     * @param translations 权限翻译DTO列表
     */
    void updatePermissionTranslations(Long permissionId, List<PermissionTranslationDto> translations);

    /**
     * 查询已被使用的权限名称
     * 根据权限ID列表查询对应的权限名称
     *
     * @param usedPermissionIds 已被使用的权限ID列表
     * @return 已被使用的权限名称列表
     */
    Set<String> selectUsedPermissionNames(Set<Long> usedPermissionIds);

}
