package org.eu.originalkeen.system.user.service;

import com.mybatisflex.core.service.IService;
import org.eu.originalkeen.core.domain.bo.UserBo;
import org.eu.originalkeen.core.domain.vo.PageVo;
import org.eu.originalkeen.system.user.domain.bo.ValidateUsernameUniqueBo;
import org.eu.originalkeen.system.user.domain.dto.EnquiryUserPageDto;
import org.eu.originalkeen.system.user.domain.entity.UserEntity;
import org.eu.originalkeen.system.user.domain.vo.UserDetailsVo;
import org.eu.originalkeen.system.user.domain.vo.UserPageVo;

import java.util.Set;

/**
 * 用户服务接口
 * 提供用户管理相关的业务逻辑方法
 */
public interface UserService extends IService<UserEntity> {

    /**
     * 分页查询用户列表
     * 根据查询条件分页获取用户列表
     *
     * @param enquiryUserPageDto 用户分页查询的DTO对象
     * @return 包含用户分页数据的响应对象
     */
    PageVo<UserPageVo> enquiryPage(EnquiryUserPageDto enquiryUserPageDto);

    /**
     * 查询用户详情
     * 获取指定用户ID的详细信息
     *
     * @param id 要查询的用户ID
     * @return 用户详情视图对象
     */
    UserDetailsVo enquiryDetails(Long id);

    /**
     * 根据用户名查询用户信息
     * 查询指定用户名的用户详细信息，用于认证和授权
     *
     * @param username 用户名
     * @return 用户信息对象
     */
    UserBo selectUserInfoByUsername(String username);

    /**
     * 更新用户密码
     * 根据用户ID更新用户的密码
     *
     * @param userId             用户ID
     * @param encodedNewPassword 新的已加密密码
     */
    void updatePassword(Long userId, String encodedNewPassword);

    /**
     * 校验用户是否存在
     * 根据用户ID校验用户是否存在
     *
     * @param userId 要校验的用户ID
     * @return 如果用户存在返回true，否则返回false
     */
    boolean selectUserExists(Long userId);

    /**
     * 查询已存在的用户名列表
     * 校验数据库中是否存在指定的用户名
     *
     * @param validateUsernameUniqueBo 用户名唯一性校验的业务对象
     * @return 数据库中已存在的用户名列表
     */
    Set<String> selectExistsUsernames(ValidateUsernameUniqueBo validateUsernameUniqueBo);

    /**
     * 查询用户的加密密码
     * 从数据库中获取指定用户的加密密码
     *
     * @param userId 用户ID
     * @return 加密后的密码字符串
     */
    String selectEncodedPassword(Long userId);

}
