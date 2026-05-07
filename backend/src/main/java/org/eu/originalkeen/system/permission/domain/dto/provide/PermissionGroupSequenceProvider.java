package org.eu.originalkeen.system.permission.domain.dto.provide;

import org.eu.originalkeen.core.constant.SystemConstant;
import org.eu.originalkeen.system.permission.domain.dto.CreatePermissionDto;
import org.eu.originalkeen.system.permission.domain.dto.PermissionDtoWrapper;
import org.eu.originalkeen.system.permission.domain.dto.UpdatePermissionDto;
import org.apache.commons.lang3.StringUtils;
import org.hibernate.validator.spi.group.DefaultGroupSequenceProvider;

import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

/**
 * 权限分组校验提供器
 * 根据权限类型动态提供校验组序列，用于实现条件校验
 */
public class PermissionGroupSequenceProvider {

    /**
     * 创建权限分组校验提供器
     * 为创建权限DTO提供校验组序列
     */
    public static class CreatePermission implements DefaultGroupSequenceProvider<CreatePermissionDto> {
        /**
         * 获取校验组
         * 根据权限类型动态添加校验组
         *
         * @param bean 要校验的创建权限DTO
         * @return 校验组列表
         */
        @Override
        public List<Class<?>> getValidationGroups(CreatePermissionDto bean) {
            List<Class<?>> groups = new ArrayList<>();

            groups.add(CreatePermissionDto.class);

            addValidateGroup(bean, groups);

            return groups;
        }
    }

    /**
     * 更新权限分组校验提供器
     * 为更新权限DTO提供校验组序列
     */
    public static class UpdatePermission implements DefaultGroupSequenceProvider<UpdatePermissionDto> {
        /**
         * 获取校验组
         * 根据权限类型动态添加校验组
         *
         * @param bean 要校验的更新权限DTO
         * @return 校验组列表
         */
        @Override
        public List<Class<?>> getValidationGroups(UpdatePermissionDto bean) {
            List<Class<?>> groups = new ArrayList<>();

            groups.add(UpdatePermissionDto.class);

            addValidateGroup(bean, groups);

            return groups;
        }
    }

    /**
     * 添加校验组
     * 根据权限类型添加相应的校验组
     *
     * @param bean   权限DTO包装器
     * @param groups 校验组列表
     */
    private static void addValidateGroup(PermissionDtoWrapper bean, List<Class<?>> groups) {
        if (Objects.nonNull(bean) && StringUtils.isNotEmpty(bean.getPermissionType())) {
            if (StringUtils.equals(SystemConstant.PERMISSION_TYPE_SUBHEADER, bean.getPermissionType())) {
                groups.add(Subheader.class);
            }
            if (StringUtils.equals(SystemConstant.PERMISSION_TYPE_GROUP, bean.getPermissionType())) {
                groups.add(Group.class);
            }
            if (StringUtils.equals(SystemConstant.PERMISSION_TYPE_TEMPLATE, bean.getPermissionType())) {
                groups.add(Template.class);
            }
            if (StringUtils.equals(SystemConstant.PERMISSION_TYPE_LINK, bean.getPermissionType())) {
                groups.add(Link.class);
            }
            if (StringUtils.equals(SystemConstant.PERMISSION_TYPE_BUTTON, bean.getPermissionType())) {
                groups.add(Button.class);
            }
            if (StringUtils.equals(SystemConstant.PERMISSION_TYPE_FUNCTION, bean.getPermissionType())) {
                groups.add(Function.class);
            }
        }
    }

    /**
     * 私有构造函数
     * 防止实例化工具类
     */
    private PermissionGroupSequenceProvider() {
    }

}
