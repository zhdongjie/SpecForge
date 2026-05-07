package org.eu.originalkeen.system.role.service;

import com.mybatisflex.core.service.IService;
import org.eu.originalkeen.core.domain.vo.PageVo;
import org.eu.originalkeen.system.role.domain.bo.RoleBo;
import org.eu.originalkeen.system.role.domain.bo.ValidateRoleCodeUniqueBo;
import org.eu.originalkeen.system.role.domain.dto.EnquiryRolePageDto;
import org.eu.originalkeen.system.role.domain.entity.RoleEntity;
import org.eu.originalkeen.system.role.domain.vo.RoleDetailsVo;
import org.eu.originalkeen.system.role.domain.vo.RoleListVo;
import org.eu.originalkeen.system.role.domain.vo.RolePageVo;

import java.util.List;
import java.util.Set;

/**
 * 角色服务接口
 * 提供角色管理相关的业务逻辑方法
 */
public interface RoleService extends IService<RoleEntity> {

    /**
     * 查询角色分页
     * 分页查询角色列表
     *
     * @param enquiryRolePageDto 查询角色分页数据传输对象
     * @return 角色分页数据响应对象
     */
    PageVo<RolePageVo> enquiryPage(EnquiryRolePageDto enquiryRolePageDto);

    /**
     * 查询角色详情
     * 根据ID查询角色详细信息
     *
     * @param id 角色ID
     * @return 角色详情响应对象
     */
    RoleDetailsVo enquiryDetails(Long id);

    /**
     * 查询角色列表
     * 查询所有角色的列表
     *
     * @return 角色列表响应对象
     */
    List<RoleListVo> enquiryList();

    /**
     * 查询默认角色ID列表
     * 获取系统中定义的默认角色的ID列表
     *
     * @return 默认角色ID列表
     */
    Set<Long> selectDefaultRoleIds();

    /**
     * 查询有效的角色ID列表
     * 从给定的角色ID列表中筛选出有效的角色ID
     *
     * @param roleIds 需要校验的角色ID列表
     * @return 有效的角色ID列表
     */
    Set<Long> selectEffectiveRoleIds(Set<Long> roleIds);

    /**
     * 校验角色是否存在
     * 根据角色ID校验角色是否存在
     *
     * @param roleId 要校验的角色ID
     * @return 如果角色存在返回true，否则返回false
     */
    boolean selectRoleExists(Long roleId);

    /**
     * 校验角色代码是否存在
     * 校验指定的角色代码是否已经存在
     *
     * @param validateRoleCodeUniqueBo 角色代码唯一性校验对象
     * @return 如果角色代码已存在返回true，否则返回false
     */
    boolean selectRoleCodeExists(ValidateRoleCodeUniqueBo validateRoleCodeUniqueBo);

    /**
     * 查询用户的角色列表
     * 根据用户ID查询该用户所拥有的所有角色
     *
     * @param userId 用户ID
     * @return 角色列表
     */
    List<RoleBo> selectUserRoles(Long userId);

}
