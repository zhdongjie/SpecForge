package org.eu.originalkeen.system.user.service.impl;

import com.mybatisflex.core.paginate.Page;
import com.mybatisflex.core.query.If;
import com.mybatisflex.core.query.QueryChain;
import com.mybatisflex.core.relation.RelationManager;
import com.mybatisflex.spring.service.impl.ServiceImpl;
import org.eu.originalkeen.core.domain.bo.UserBo;
import org.eu.originalkeen.core.domain.dto.OrderDto;
import org.eu.originalkeen.core.domain.vo.PageVo;
import org.eu.originalkeen.core.exception.BusinessException;
import org.eu.originalkeen.core.utils.LocaleUtils;
import org.eu.originalkeen.system.role.domain.entity.UserRoleEntity;
import org.eu.originalkeen.system.user.domain.bo.ValidateUsernameUniqueBo;
import org.eu.originalkeen.system.user.domain.dto.EnquiryUserPageDto;
import org.eu.originalkeen.system.user.domain.entity.UserEntity;
import org.eu.originalkeen.system.user.domain.vo.UserDetailsVo;
import org.eu.originalkeen.system.user.domain.vo.UserPageVo;
import org.eu.originalkeen.system.user.mapper.UserMapper;
import org.eu.originalkeen.system.user.service.UserService;
import org.apache.commons.collections4.CollectionUtils;
import org.apache.commons.lang3.StringUtils;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

import static com.mybatisflex.core.util.StringUtil.camelToUnderline;
import static org.eu.originalkeen.system.role.domain.entity.table.UserRoleTableDef.user_role;
import static org.eu.originalkeen.system.user.domain.entity.table.UserTableDef.user;

/**
 * 用户服务实现类
 * 实现用户管理相关功能，包括用户的增删改查、导入导出、权限管理等
 * <p>
 * 主要功能：
 * 1. 用户信息的分页查询和详情查询
 * 2. 用户数据的导出和密码管理
 * 3. 用户唯一性校验（用户名、邮箱、手机号）
 * <p>
 * 继承自ServiceImpl，自动注入UserMapper用于数据库操作
 */
@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, UserEntity>
        implements UserService {

    /**
     * 分页查询用户列表
     * 根据查询条件分页获取用户列表，支持按用户名和角色过滤
     *
     * @param enquiryUserPageDto 用户分页查询的DTO对象，包含分页参数和查询条件
     * @return 包含用户分页数据的响应对象
     */
    @Override
    public PageVo<UserPageVo> enquiryPage(EnquiryUserPageDto enquiryUserPageDto) {
        // 1. 设置额外的查询条件参数
        //    添加当前语言代码，用于查询对应语言的数据
        RelationManager.addExtraConditionParam("languageCode", LocaleUtils.getLangCode());

        // 2. 创建分页对象
        //    根据当前页码和页面大小创建分页对象
        Page<UserPageVo> page = Page.of(enquiryUserPageDto.getCurrentPage(), enquiryUserPageDto.getPageSize());

        // 3. 构建查询条件
        //    创建复杂的查询链，包括表连接、条件过滤等
        QueryChain<UserEntity> queryChain = queryChain()
                .select(
                        user.id,
                        user.username,
                        user.created_time
                )
                .from(user)
                // TODO: mybatis-flex目前缺少条件构造函数，这里临时使用UserRoleEntity.class作为条件连接的替代方案，后续版本更新时需要优化
                .innerJoin(UserRoleEntity.class, CollectionUtils.isNotEmpty(enquiryUserPageDto.getRoleIds()))
                .on(user.id.eq(user_role.user_id))
                .where(user.username.like(enquiryUserPageDto.getUsername(), If::hasText))
                .and(user_role.role_id.in(enquiryUserPageDto.getRoleIds(), If::notEmpty))
                .and(user.created_time.gt(enquiryUserPageDto.getCreatedTimeStart(), If::notNull))
                .and(user.created_time.lt(enquiryUserPageDto.getCreatedTimeEnd(), If::notNull));

        // 4. 处理排序条件
        //    根据传入的排序条件添加排序规则
        List<OrderDto> orders = enquiryUserPageDto.getOrders();
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

        // 5. 执行分页查询
        //    调用mapper执行查询并将结果映射为UserPageVo对象
        Page<UserPageVo> userVoPage = mapper.paginateWithRelationsAs(
                page,
                queryChain,
                UserPageVo.class
        );

        // 6. 转换为统一的分页响应对象
        return PageVo.of(userVoPage);
    }

    /**
     * 查询用户详情
     * 获取指定用户ID的详细信息
     *
     * @param id 要查询的用户ID
     * @return 包含用户详细信息的响应对象
     * @throws BusinessException 当用户不存在时抛出
     */
    @Override
    public UserDetailsVo enquiryDetails(Long id) {
        return mapper.selectOneWithRelationsByQueryAs(
                queryChain()
                        .select(
                                user.id,
                                user.username
                        )
                        .from(user)
                        .where(user.id.eq(id)),
                UserDetailsVo.class
        );
    }

    /**
     * 根据用户名查询用户信息
     * 查询指定用户名的用户详细信息，用于认证和授权
     *
     * @param username 用户名
     * @return 用户信息对象
     * @throws UsernameNotFoundException 当用户名不存在时抛出
     */
    @Override
    public UserBo selectUserInfoByUsername(String username) {
        return queryChain()
                .select(
                        user.id,
                        user.username,
                        user.encoded_password,
                        user.created_time
                )
                .from(user)
                .where(user.username.eq(username))
                .oneAs(UserBo.class);
    }

    /**
     * 更新用户密码
     * 根据用户ID更新用户的密码
     *
     * @param userId             用户ID
     * @param encodedNewPassword 新的已加密密码
     */
    @Override
    public void updatePassword(Long userId, String encodedNewPassword) {
        updateChain()
                .set(user.encoded_password, encodedNewPassword)
                .where(user.id.eq(userId))
                .update();
    }

    /**
     * 校验用户是否存在
     * 根据用户ID校验用户是否存在
     *
     * @param userId 要校验的用户ID
     * @return 如果用户存在返回true，否则返回false
     */
    @Override
    public boolean selectUserExists(Long userId) {
        return exists(user.id.eq(userId));
    }

    /**
     * 查询已存在的用户名列表
     * 校验数据库中是否存在指定的用户名
     *
     * @param validateUsernameUniqueBo 用户名唯一性校验的业务对象
     * @return 数据库中已存在的用户名列表
     */
    @Override
    public Set<String> selectExistsUsernames(ValidateUsernameUniqueBo validateUsernameUniqueBo) {
        return new HashSet<>(queryChain()
                .select(user.username)
                .from(user)
                .where(user.id.ne(validateUsernameUniqueBo.getId(), If::notNull))
                .and(user.username.in(validateUsernameUniqueBo.getUsernames()))
                .listAs(String.class)
        );
    }

    /**
     * 查询用户的加密密码
     * 从数据库中获取指定用户的加密密码
     *
     * @param userId 用户ID
     * @return 加密后的密码字符串
     */
    @Override
    public String selectEncodedPassword(Long userId) {
        return queryChain()
                .select(user.encoded_password)
                .from(user)
                .where(user.id.eq(userId))
                .oneAs(String.class);
    }

}
