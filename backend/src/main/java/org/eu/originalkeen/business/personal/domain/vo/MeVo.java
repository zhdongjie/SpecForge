package org.eu.originalkeen.business.personal.domain.vo;

import com.fasterxml.jackson.annotation.JsonFormat;
import org.eu.originalkeen.core.constant.SystemConstant;
import org.eu.originalkeen.core.domain.bo.UserBo;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.apache.commons.lang3.StringUtils;

import java.io.Serial;
import java.io.Serializable;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

/**
 * 个人信息视图对象
 * 用于返回当前登录用户的个人信息和权限信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class MeVo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -8766122666151339642L;

    /**
     * 用户名
     * 用户的登录账号
     */
    private String username;

    /**
     * 角色列表
     * 用户拥有的角色标识列表
     */
    private List<String> roles;

    /**
     * 路由列表
     * 用户可访问的前端路由菜单列表
     */
    private List<RouterVo> routers;

    /**
     * 按钮列表
     * 用户可操作的按钮权限标识列表
     */
    private List<String> buttons;

    /**
     * 创建时间
     * 用户账号的创建时间
     */
    private Date createdTime;

    /**
     * 从用户业务对象创建MeVo对象
     * 将用户信息和权限信息转换为前端所需的格式
     *
     * @param userBo 用户业务对象
     * @return MeVo对象
     */
    public static MeVo of(UserBo userBo) {
        List<String> roles = new ArrayList<>();
        List<RouterVo> routers = new ArrayList<>();
        List<String> buttons = new ArrayList<>();

        userBo.getRoles().forEach(role -> roles.add(role.getRoleName()));

        userBo.getPermissions().forEach(permission -> {
            String permissionType = permission.getPermissionType();
            if (!StringUtils.equals(SystemConstant.PERMISSION_TYPE_FUNCTION, permissionType)) {
                if (StringUtils.equals(SystemConstant.PERMISSION_TYPE_BUTTON, permissionType)) {
                    buttons.add(permission.getAuthority());
                } else {
                    routers.add(RouterVo.of(permission));
                }
            }
        });

        return new MeVo(
                userBo.getUsername(),
                roles,
                routers,
                buttons,
                userBo.getCreatedTime()
        );
    }

}
