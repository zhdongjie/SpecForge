package org.eu.originalkeen.system.user.manager;

import org.eu.originalkeen.core.domain.bo.AuthorityBo;
import org.eu.originalkeen.core.domain.bo.PermissionBo;
import org.eu.originalkeen.core.domain.bo.UserBo;
import org.eu.originalkeen.core.domain.vo.PageVo;
import org.eu.originalkeen.core.domain.vo.ResponseVo;
import org.eu.originalkeen.core.exception.BusinessException;
import org.eu.originalkeen.core.exception.business.FieldValidationException;
import org.eu.originalkeen.system.permission.service.PermissionService;
import org.eu.originalkeen.system.role.domain.bo.RoleBo;
import org.eu.originalkeen.system.role.service.RoleService;
import org.eu.originalkeen.system.role.service.UserRoleService;
import org.eu.originalkeen.system.user.domain.bo.ValidateUserBo;
import org.eu.originalkeen.system.user.domain.bo.ValidateUsernameUniqueBo;
import org.eu.originalkeen.system.user.domain.dto.CreateUserDto;
import org.eu.originalkeen.system.user.domain.dto.EnquiryUserPageDto;
import org.eu.originalkeen.system.user.domain.dto.UpdateUserDto;
import org.eu.originalkeen.system.user.domain.dto.ValidateUsernameUniqueDto;
import org.eu.originalkeen.system.user.domain.entity.UserEntity;
import org.eu.originalkeen.system.user.domain.vo.UserDetailsVo;
import org.eu.originalkeen.system.user.domain.vo.UserPageVo;
import org.eu.originalkeen.system.user.service.UserService;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.collections4.CollectionUtils;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsPasswordService;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Objects;
import java.util.Set;
import java.util.stream.Collectors;

import static org.eu.originalkeen.system.user.domain.entity.table.UserTableDef.user;

/**
 * 用户管理器
 * 提供用户相关的业务处理功能，整合用户服务、角色服务和权限服务等
 * <p>
 * 主要功能：
 * 1. 用户的创建、更新、删除和查询
 * 2. 用户与角色的关联管理
 * 3. 用户信息的校验逻辑
 * 4. 用户认证和授权信息的加载
 * 5. 用户数据的导入导出
 * <p>
 * 实现了Spring Security的UserDetailsService和UserDetailsPasswordService接口
 * 使用@Slf4j注解提供日志记录功能
 */
@Slf4j
@Component
public class UserManager implements UserDetailsService, UserDetailsPasswordService {

    /**
     * 密码编码器
     * 用于加密用户密码，确保密码安全存储
     */
    @Resource
    private PasswordEncoder passwordEncoder;

    /**
     * 用户服务
     * 提供用户基础数据的增删改查操作
     */
    @Resource
    private UserService userService;

    /**
     * 用户角色关联服务
     * 管理用户与角色之间的关联关系
     */
    @Resource
    private UserRoleService userRoleService;

    /**
     * 角色服务
     * 提供角色相关的查询操作，包括默认角色和有效角色的获取
     */
    @Resource
    private RoleService roleService;

    /**
     * 权限服务
     * 提供用户权限的查询功能，用于构建用户的授权信息
     */
    @Resource
    private PermissionService permissionService;

    /**
     * 校验用户名是否唯一
     * 校验指定的用户名在系统中是否已经存在
     *
     * @param validateUsernameUniqueDto 用户名唯一性校验的DTO对象
     * @return 包含用户名是否存在的响应对象，true表示已存在，false表示不存在
     */
    @Transactional(readOnly = true)
    public ResponseVo<Boolean> validateUsernameUnique(ValidateUsernameUniqueDto validateUsernameUniqueDto) {
        // 1. 转换DTO为业务对象
        //    将前端传来的DTO转换为内部业务处理对象
        ValidateUsernameUniqueBo validateUsernameUniqueBo = ValidateUsernameUniqueBo.of(validateUsernameUniqueDto);

        // 2. 查询用户名是否存在
        //    校验数据库中是否已存在相同的用户名（排除当前用户ID）
        Set<String> existsUsernames = userService.selectExistsUsernames(validateUsernameUniqueBo);

        // 3. 返回校验结果
        //    如果列表不为空，表示用户名已存在
        return ResponseVo.success(CollectionUtils.isNotEmpty(existsUsernames));
    }

    /**
     * 创建新的用户
     * 在系统中创建一个新的用户记录，并建立与角色的关联关系
     *
     * @param createUserDto 创建用户的DTO对象，包含用户的各项属性和角色ID列表
     * @return 创建结果的响应对象
     * @throws BusinessException        当用户名已存在时抛出
     * @throws FieldValidationException 当用户属性校验失败时抛出
     */
    @Transactional
    public ResponseVo<Void> create(CreateUserDto createUserDto) {
        // 1. 校验用户信息：校验用户名、邮箱、手机号码的唯一性，性别的有效性等
        //    校验用户提交的各项属性是否符合业务规则
        ValidateUserBo validateUserBo = ValidateUserBo.of(createUserDto);
        validateUserInfo(validateUserBo);

        // 2. 创建用户实体并加密密码
        //    使用PasswordEncoder对密码进行单向加密，确保密码安全存储
        UserEntity userEntity = UserEntity.of(
                createUserDto,
                passwordEncoder.encode(createUserDto.getPassword())
        );

        // 3. 保存用户基本信息到数据库
        //    此时会生成用户ID，后续关联操作需要使用此ID
        userService.save(userEntity);

        Set<Long> roleIds = createUserDto.getRoleIds();
        Set<Long> effectiveRoleIds;
        // 4. 查询有效的角色ID列表
        //    如果角色传入的角色ID不为空，校验用户提交的角色ID是否有效，过滤掉无效的角色ID
        //    如果传入的角色ID为空，使用默认角色
        if (CollectionUtils.isNotEmpty(roleIds)) {
            effectiveRoleIds = getEffectiveRoleIds(roleIds);
        } else {
            effectiveRoleIds = roleService.selectDefaultRoleIds();
        }

        // 5. 创建用户与角色的关联关系
        //    在用户角色关联表中创建记录，建立用户与角色的多对多关系
        userRoleService.createUserRoleRelation(
                userEntity.getId(),
                effectiveRoleIds
        );

        // 6. 返回成功响应
        return ResponseVo.success();
    }

    /**
     * 批量删除用户
     * 删除指定的一组用户，并删除相关的头像引用和角色关联
     *
     * @param userIds 要删除的用户ID列表
     * @return 删除结果的响应对象
     */
    @Transactional
    public ResponseVo<Void> batchDelete(Set<Long> userIds) {
        // 1. 删除用户基本信息
        //    从用户表中删除指定ID的用户记录
        userService.removeByIds(userIds);

        // 2. 删除用户角色关联关系
        //    清理用户角色关联表中的关联记录
        userRoleService.deleteUserRoleRelation(userIds);

        // 3. 返回成功响应
        return ResponseVo.success();
    }

    /**
     * 更新用户信息
     * 更新指定用户的各项属性，并更新与角色的关联关系
     *
     * @param updateUserDto 更新用户的DTO对象，包含要更新的用户属性和角色ID列表
     * @return 更新结果的响应对象
     * @throws BusinessException        当用户不存在，或用户名与其他用户冲突时抛出
     * @throws FieldValidationException 当用户属性校验失败时抛出
     */
    @Transactional
    public ResponseVo<Void> update(UpdateUserDto updateUserDto) {
        // 1. 校验用户信息
        //    校验用户是否存在、用户名/邮箱/手机号是否与其他用户冲突、性别是否有效
        ValidateUserBo validateUserBo = ValidateUserBo.of(updateUserDto);
        validateUserInfo(validateUserBo);

        // 2. 创建用户实体并更新基本信息
        //    根据DTO构建实体对象，更新用户表中的记录
        UserEntity userEntity = UserEntity.of(updateUserDto);
        Long userId = updateUserDto.getId();
        userService.update(userEntity, user.id.eq(userId));

        // 3. 获取有效的角色ID列表
        //    校验传入的角色ID是否有效，筛选出有效的角色ID
        Set<Long> effectiveRoleIds = getEffectiveRoleIds(updateUserDto.getRoleIds());

        // 4. 更新用户与角色的关联关系
        //    比较新旧角色列表，删除不需要的角色关联，新增需要的角色关联
        updateUserRoleRelation(userId, effectiveRoleIds);

        // 5. 返回成功响应
        return ResponseVo.success();
    }

    /**
     * 分页查询用户列表
     * 根据查询条件分页获取用户列表，支持按用户名和角色过滤
     *
     * @param enquiryUserPageDto 用户分页查询的DTO对象，包含分页参数和查询条件
     * @return 包含用户分页数据的响应对象
     */
    @Transactional(readOnly = true)
    public ResponseVo<PageVo<UserPageVo>> enquiryPage(EnquiryUserPageDto enquiryUserPageDto) {
        // 1. 调用用户服务的分页查询方法
        //    将查询条件传递给服务层，获取分页结果
        PageVo<UserPageVo> userPageVo = userService.enquiryPage(enquiryUserPageDto);

        // 2. 封装并返回查询结果
        //    将分页数据包装为统一响应格式
        return ResponseVo.success(userPageVo);
    }

    /**
     * 查询用户详情
     * 获取指定用户ID的详细信息
     *
     * @param id 要查询的用户ID
     * @return 包含用户详细信息的响应对象
     * @throws BusinessException 当用户不存在时抛出
     */
    @Transactional(readOnly = true)
    public ResponseVo<UserDetailsVo> enquiryDetails(Long id) {
        // 1. 调用用户服务查询用户详情
        //    根据ID查询用户的详细信息
        UserDetailsVo userDetails = userService.enquiryDetails(id);

        // 2. 校验用户是否存在
        //    如果用户不存在，记录警告日志并抛出业务异常
        if (Objects.isNull(userDetails)) {
            log.warn("User [{}] not found when enquiring details", id);
            throw new BusinessException("form.user.userNotFound");
        }

        // 3. 封装并返回查询结果
        //    将用户详情数据包装为统一响应格式
        return ResponseVo.success(userDetails);
    }

    /**
     * 根据用户名加载用户认证信息
     * 实现Spring Security的UserDetailsService接口，加载用户的认证和授权信息
     *
     * @param username 用户名
     * @return 用户详细信息，包含认证和授权数据
     * @throws UsernameNotFoundException 当用户名不存在时抛出
     */
    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        // 1. 根据用户名查询用户基本信息
        //    获取用户ID、用户名、密码等基础数据
        UserBo userBoInfo = userService.selectUserInfoByUsername(username);

        // 2. 校验用户是否存在
        //    如果用户不存在，记录警告日志并抛出异常
        if (Objects.isNull(userBoInfo)) {
            log.warn("User [{}] not found when loading user by username", username);
            throw new UsernameNotFoundException(username);
        }

        Long userId = userBoInfo.getId();

        // 3. 查询用户拥有的所有角色名称
        //    获取用户关联的角色代码列表
        List<RoleBo> roles = roleService.selectUserRoles(userId);
        userBoInfo.setRoles(roles);

        // 4. 将角色转换为Spring Security需要的Authority格式
        //    添加ROLE_前缀并构建授权对象
        addRoleAuthorities(userBoInfo, roles);

        // 5. 查询用户拥有的所有权限
        //    获取用户通过角色间接拥有的所有权限
        List<PermissionBo> permissions = permissionService.selectUserPermissions(userId);
        userBoInfo.setPermissions(permissions);

        // 6. 将权限转换为Spring Security需要的Authority格式
        //    构建权限授权对象并添加到用户信息中
        addPermissionAuthorities(userBoInfo, permissions);

        // 7. 返回完整的用户认证授权信息
        return userBoInfo;
    }

    /**
     * 更新用户密码
     * 实现Spring Security的UserDetailsPasswordService接口，更新用户的密码
     *
     * @param userDetails        用户详细信息
     * @param newEncodedPassword 新的已加密密码
     * @return 更新后的用户详细信息
     */
    @Override
    public UserDetails updatePassword(UserDetails userDetails, String newEncodedPassword) {
        // 1. 校验传入的用户详情是否为系统自定义的UserBo类型
        //    只处理系统内部的用户类型
        if (userDetails instanceof UserBo userBoInfo) {
            // 2. 更新数据库中用户的密码
            //    调用用户服务更新密码记录
            userService.updatePassword(userBoInfo.getId(), newEncodedPassword);

            // 3. 更新当前用户对象中的密码
            //    确保内存中的对象与数据库同步
            userBoInfo.setEncodedPassword(newEncodedPassword);
        }
        // 注意：如果不是UserBo类型，不进行任何操作，直接返回原对象

        // 4. 返回更新后的用户详情
        return userDetails;
    }

    /**
     * 添加权限授权信息
     * 将用户的权限转换为授权对象并添加到用户信息中
     *
     * @param userBoInfo  用户信息对象
     * @param permissions 用户的权限列表
     */
    private void addPermissionAuthorities(UserBo userBoInfo, List<PermissionBo> permissions) {
        List<AuthorityBo> permissionsAuthorities = permissions.stream()
                .map(AuthorityBo::of)
                .toList();
        userBoInfo.addAuthorities(permissionsAuthorities);
    }

    /**
     * 添加角色授权信息
     * 将用户的角色转换为授权对象并添加到用户信息中
     *
     * @param userBoInfo 用户信息对象
     * @param roles      用户的角色列表
     */
    private void addRoleAuthorities(UserBo userBoInfo, List<RoleBo> roles) {
        List<AuthorityBo> roleAuthorities = roles.stream()
                .map(AuthorityBo::of)
                .toList();
        userBoInfo.addAuthorities(roleAuthorities);
    }

    /**
     * 更新用户角色关联关系
     * 根据新的角色ID列表，更新用户与角色的关联关系，删除不再需要的关联，添加新的关联
     *
     * @param userId           要更新角色关联的用户ID
     * @param effectiveRoleIds 新的有效角色ID列表
     */
    private void updateUserRoleRelation(Long userId, Set<Long> effectiveRoleIds) {
        // 1. 查询用户当前拥有的所有角色ID
        //    获取数据库中已存在的用户-角色关联关系
        Set<Long> oldRoleIds = userRoleService.selectRoleIdsByUserId(userId);

        // 2. 判断新旧角色列表是否有变化
        //    如果新旧列表完全相同，则不需要进行任何更新操作
        if (!CollectionUtils.containsAll(oldRoleIds, effectiveRoleIds)
                || !CollectionUtils.containsAll(effectiveRoleIds, oldRoleIds)) {

            // 3. 找出需要删除的角色关联
            //    筛选出在旧列表中存在但在新列表中不存在的角色ID
            Set<Long> deletedRoleIds = filterDeletedRoleId(effectiveRoleIds, oldRoleIds);

            // 4. 删除不再需要的角色关联
            //    如果有需要删除的角色关联，调用服务删除这些关联记录
            if (CollectionUtils.isNotEmpty(deletedRoleIds)) {
                userRoleService.deleteUserRoleRelation(userId, deletedRoleIds);
            }

            // 5. 找出需要新增的角色关联
            //    筛选出在新列表中存在但在旧列表中不存在的角色ID
            Set<Long> addedRoleIds = filterAddedRoleIds(effectiveRoleIds, oldRoleIds);

            // 6. 创建新的角色关联
            //    如果有需要新增的角色关联，调用服务创建这些关联记录
            if (CollectionUtils.isNotEmpty(addedRoleIds)) {
                userRoleService.createUserRoleRelation(userId, addedRoleIds);
            }
        }
        // 如果两个列表完全相等，则无需进行任何更新操作
    }

    /**
     * 过滤出需要删除的角色ID
     * 从旧角色ID列表中过滤出在新角色ID列表中不存在的ID
     *
     * @param newRoleIds 新的角色ID列表
     * @param oldRoleIds 旧的角色ID列表
     * @return 需要删除的角色ID列表
     */
    private Set<Long> filterDeletedRoleId(
            Set<Long> newRoleIds,
            Set<Long> oldRoleIds
    ) {
        return oldRoleIds.stream()
                .filter(oldRoleId -> !newRoleIds.contains(oldRoleId))
                .collect(Collectors.toSet());
    }

    /**
     * 过滤出需要新增的角色ID
     * 从新角色ID列表中过滤出在旧角色ID列表中不存在的ID
     *
     * @param newRoleIds 新的角色ID列表
     * @param oldRoleIds 旧的角色ID列表
     * @return 需要新增的角色ID列表
     */
    private Set<Long> filterAddedRoleIds(
            Set<Long> newRoleIds,
            Set<Long> oldRoleIds
    ) {
        return newRoleIds.stream()
                .filter(newRoleId -> !oldRoleIds.contains(newRoleId))
                .collect(Collectors.toSet());
    }

    /**
     * 获取有效的角色ID列表
     * 从用户提交的角色ID列表中筛选出有效的角色ID
     *
     * @param roleIds 用户提交的角色ID列表
     * @return 有效的角色ID列表
     * @throws FieldValidationException 当没有有效的角色ID时抛出
     */
    private Set<Long> getEffectiveRoleIds(Set<Long> roleIds) {
        Set<Long> effectiveRoleIds = roleService.selectEffectiveRoleIds(roleIds);

        if (CollectionUtils.isEmpty(effectiveRoleIds)) {
            log.warn("Invalid role list: no valid roles found");
            throw new FieldValidationException("roleIds", "form.user.invalidRoleList");
        }
        return effectiveRoleIds;
    }

    /**
     * 校验用户信息
     * 校验用户各项属性的有效性和唯一性，包括用户是否存在、性别是否有效、用户名/邮箱/电话号码是否唯一
     * <p>
     * 校验流程：
     * 1. 如果是更新操作，校验用户是否存在
     * 2. 校验用户性别值是否有效
     * 3. 校验用户名是否唯一
     * 4. 校验电子邮箱是否唯一（如果提供）
     * 5. 校验电话号码是否唯一（如果提供）
     *
     * @param validateUserBo 要校验的用户业务对象
     * @throws BusinessException        当用户不存在时抛出
     * @throws FieldValidationException 当用户属性校验失败时抛出
     */
    private void validateUserInfo(ValidateUserBo validateUserBo) {
        // 1. 如果是更新操作，校验用户是否存在
        //    对于更新操作，需要确保要更新的用户记录存在
        Long userId = validateUserBo.getId();
        if (Objects.nonNull(userId)) {
            // 查询用户信息是否存在
            boolean userExists = userService.selectUserExists(userId);
            if (!userExists) {
                log.warn("User [{}] not found when validating user info", userId);
                throw new BusinessException("form.user.userNotFound");
            }
        }

        // 2. 校验用户名的唯一性
        //    确保用户名不与现有用户冲突
        String username = validateUserBo.getUsername();
        ValidateUsernameUniqueBo validateUsernameUniqueBo = ValidateUsernameUniqueBo.of(validateUserBo);
        Set<String> existsUsernames = userService.selectExistsUsernames(validateUsernameUniqueBo);
        if (CollectionUtils.isNotEmpty(existsUsernames)) {
            log.warn("Username [{}] already in use", username);
            throw new FieldValidationException("username", "form.user.usernameAlreadyUse");
        }

    }

}
