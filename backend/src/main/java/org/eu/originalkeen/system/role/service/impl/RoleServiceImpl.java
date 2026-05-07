package org.eu.originalkeen.system.role.service.impl;

import com.mybatisflex.core.paginate.Page;
import com.mybatisflex.core.query.If;
import com.mybatisflex.core.query.QueryChain;
import com.mybatisflex.spring.service.impl.ServiceImpl;
import org.eu.originalkeen.core.constant.SystemConstant;
import org.eu.originalkeen.core.domain.dto.OrderDto;
import org.eu.originalkeen.core.domain.vo.PageVo;
import org.eu.originalkeen.core.exception.BusinessException;
import org.eu.originalkeen.core.utils.LocaleUtils;
import org.eu.originalkeen.system.role.domain.bo.RoleBo;
import org.eu.originalkeen.system.role.domain.bo.ValidateRoleCodeUniqueBo;
import org.eu.originalkeen.system.role.domain.dto.EnquiryRolePageDto;
import org.eu.originalkeen.system.role.domain.entity.RoleEntity;
import org.eu.originalkeen.system.role.domain.vo.RoleDetailsVo;
import org.eu.originalkeen.system.role.domain.vo.RoleListVo;
import org.eu.originalkeen.system.role.domain.vo.RolePageVo;
import org.eu.originalkeen.system.role.mapper.RoleMapper;
import org.eu.originalkeen.system.role.service.RoleService;
import org.apache.commons.collections4.CollectionUtils;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;

import java.util.HashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;

import static com.mybatisflex.core.util.StringUtil.camelToUnderline;
import static org.eu.originalkeen.system.role.domain.entity.table.RoleTableDef.role;
import static org.eu.originalkeen.system.role.domain.entity.table.RoleTranslationTableDef.role_translation;
import static org.eu.originalkeen.system.role.domain.entity.table.UserRoleTableDef.user_role;

/**
 * 角色服务实现类
 * 实现角色管理相关的业务逻辑，包括角色的增删改查和唯一性校验
 * <p>
 * 主要功能：
 * 1. 角色信息的分页查询和详情查询
 * 2. 角色列表查询和默认角色管理
 * 3. 角色唯一性校验和有效性校验
 * <p>
 * 继承自ServiceImpl，自动注入RoleMapper用于数据库操作
 */
@Service
public class RoleServiceImpl extends ServiceImpl<RoleMapper, RoleEntity> implements RoleService {

    /**
     * 分页查询角色列表
     * 根据查询条件分页获取角色列表
     *
     * @param enquiryRolePageDto 角色分页查询的DTO对象，包含分页参数和查询条件
     * @return 包含角色分页数据的响应对象
     */
    @Override
    public PageVo<RolePageVo> enquiryPage(EnquiryRolePageDto enquiryRolePageDto) {
        // 1. 创建分页对象
        //    根据当前页码和页面大小创建分页对象
        Page<RolePageVo> page = Page.of(enquiryRolePageDto.getCurrentPage(), enquiryRolePageDto.getPageSize());

        // 2. 构建查询条件
        //    创建查询链，包含需要的字段、表连接和过滤条件
        QueryChain<RoleEntity> queryChain = queryChain()
                .select(
                        role.id,
                        role_translation.role_name,
                        role.role_code,
                        role.sort,
                        role.role_status,
                        role_translation.remark,
                        role.created_time
                )
                .from(role)
                .innerJoin(role_translation)
                .on(role.id.eq(role_translation.role_id))
                .where(role.role_status.eq(enquiryRolePageDto.getRoleStatus(), If::hasText))
                .and(role.created_time.gt(enquiryRolePageDto.getCreatedTimeStart(), If::notNull))
                .and(role.created_time.lt(enquiryRolePageDto.getCreatedTimeEnd(), If::notNull))
                .and(role_translation.role_name.like(enquiryRolePageDto.getRoleName(), If::hasText))
                .and(role_translation.language_code.eq(LocaleUtils.getLangCode()));

        // 3. 处理排序条件
        //    根据传入的排序条件添加排序规则
        List<OrderDto> orders = enquiryRolePageDto.getOrders();
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

        // 4. 执行分页查询
        //    调用pageAs方法执行查询并将结果映射为RolePageVo对象
        Page<RolePageVo> roleVoPage = pageAs(
                page,
                queryChain,
                RolePageVo.class
        );

        // 5. 转换为统一的分页响应对象
        return PageVo.of(roleVoPage);
    }

    /**
     * 查询角色详情
     * 获取指定角色ID的详细信息
     *
     * @param id 要查询的角色ID
     * @return 包含角色详细信息的响应对象
     * @throws BusinessException 当角色不存在时抛出
     */
    @Override
    public RoleDetailsVo enquiryDetails(Long id) {
        return mapper.selectOneWithRelationsByQueryAs(queryChain()
                        .select(
                                role.id,
                                role.role_code,
                                role.sort,
                                role.role_status
                        )
                        .from(role)
                        .where(role.id.eq(id)),
                RoleDetailsVo.class
        );
    }

    /**
     * 查询所有角色列表
     * 获取系统中所有角色的列表
     *
     * @return 包含所有角色列表的响应对象
     */
    @Override
    public List<RoleListVo> enquiryList() {
        return listAs(
                queryChain()
                        .select(role.id, role_translation.role_name, role.role_status.as("status"))
                        .from(role)
                        .innerJoin(role_translation)
                        .on(role.id.eq(role_translation.role_id))
                        .and(role_translation.language_code.eq(LocaleUtils.getLangCode()))
                        .orderBy(role.sort.asc()),
                RoleListVo.class
        );
    }

    /**
     * 查询默认角色ID列表
     * 获取系统中定义的默认角色的ID列表，从SystemConstant中获取默认角色代码列表
     *
     * @return 默认角色ID列表
     */
    @Override
    public Set<Long> selectDefaultRoleIds() {
        return new HashSet<>(queryChain()
                .select(role.id)
                .from(role)
                .where(role.role_code.in(SystemConstant.DEFAULT_ROLE_CODES))
                .listAs(Long.class)
        );
    }

    /**
     * 查询有效的角色ID列表
     * 从给定的角色ID列表中筛选出实际存在于数据库中的有效角色ID
     *
     * @param roleIds 需要校验的角色ID列表
     * @return 有效的角色ID列表
     */
    @Override
    public Set<Long> selectEffectiveRoleIds(Set<Long> roleIds) {
        return new HashSet<>(queryChain()
                .select(role.id)
                .from(role)
                .where(role.id.in(roleIds))
                .and(role.role_status.eq(SystemConstant.ROLE_ENABLED_STATUS))
                .listAs(Long.class)
        );
    }

    /**
     * 校验角色是否存在
     * 根据角色ID校验角色是否存在
     *
     * @param roleId 要校验的角色ID
     * @return 如果角色存在返回true，否则返回false
     */
    @Override
    public boolean selectRoleExists(Long roleId) {
        return exists(role.id.eq(roleId));
    }

    /**
     * 校验角色代码是否存在
     * 校验指定的角色代码是否已经存在，排除当前角色ID
     *
     * @param validateRoleCodeUniqueBo 角色代码唯一性校验对象
     * @return 如果角色代码已存在返回true，否则返回false
     */
    @Override
    public boolean selectRoleCodeExists(ValidateRoleCodeUniqueBo validateRoleCodeUniqueBo) {
        return exists(role.role_code.eq(validateRoleCodeUniqueBo.getRoleCode())
                .and(role.id.ne(validateRoleCodeUniqueBo.getId(), Objects::nonNull))
        );
    }

    /**
     * 查询用户的角色
     * 根据用户ID查询用户所有的角色
     *
     * @param userId 用户ID
     * @return 用户的角色列表
     */
    @Override
    public List<RoleBo> selectUserRoles(Long userId) {
        return queryChain()
                .select(role.role_code, role_translation.role_name)
                .from(user_role)
                .innerJoin(role)
                .on(user_role.role_id.eq(role.id))
                .innerJoin(role_translation)
                .on(role.id.eq(role_translation.role_id))
                .where(user_role.user_id.eq(userId))
                .and(role_translation.language_code.eq(LocaleUtils.getLangCode()))
                .listAs(RoleBo.class);
    }

}
