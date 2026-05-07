package org.eu.originalkeen.system.role.service;

import com.mybatisflex.core.service.IService;
import org.eu.originalkeen.system.role.domain.bo.ValidateRoleNameUniqueBo;
import org.eu.originalkeen.system.role.domain.dto.RoleTranslationDto;
import org.eu.originalkeen.system.role.domain.entity.RoleTranslationEntity;

import java.util.List;
import java.util.Set;

/**
 * 角色翻译服务接口
 * 提供角色翻译的业务逻辑方法
 */
public interface RoleTranslationService extends IService<RoleTranslationEntity> {

    /**
     * 查询角色名称是否存在
     * 根据角色名称校验是否已存在记录
     *
     * @param validateRoleNameUniqueBo 角色名称唯一性校验业务对象
     * @return 存在返回true，不存在返回false
     */
    Set<String> selectExistsRoleNames(ValidateRoleNameUniqueBo validateRoleNameUniqueBo);

    /**
     * 创建角色翻译
     * 创建新的角色翻译记录
     *
     * @param roleId       角色ID
     * @param translations 角色翻译DTO列表
     */
    void createRoleTranslations(Long roleId, List<RoleTranslationDto> translations);

    /**
     * 删除角色翻译
     * 删除指定角色ID列表的角色翻译记录
     *
     * @param roleIds 角色ID列表
     */
    void deleteRoleTranslations(Set<Long> roleIds);

    /**
     * 更新角色翻译
     * 更新指定角色的翻译记录
     *
     * @param roleId       角色ID
     * @param translations 角色翻译DTO列表
     */
    void updateRoleTranslations(Long roleId, List<RoleTranslationDto> translations);

    /**
     * 查询已被使用的角色名称
     * 根据角色ID列表查询对应的角色名称
     *
     * @param usedRoleIds 已被使用的角色ID列表
     * @return 已被使用的角色名称列表
     */
    Set<String> selectUsedRoleNames(Set<Long> usedRoleIds);

}
