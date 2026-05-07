package org.eu.originalkeen.system.role.domain.entity;

import com.mybatisflex.annotation.Table;
import org.eu.originalkeen.core.domain.Audit;
import org.eu.originalkeen.core.domain.entity.PrimaryKeyEntity;
import org.eu.originalkeen.system.role.domain.dto.CreateRoleDto;
import org.eu.originalkeen.system.role.domain.dto.UpdateRoleDto;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.Date;

/**
 * 角色实体类
 * 对应数据库中system_role表，存储角色信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Table("system_role")
@EqualsAndHashCode(callSuper = true)
public class RoleEntity extends PrimaryKeyEntity implements Serializable, Audit {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -3562338673917641395L;

    /**
     * 角色代码
     * 角色的唯一代码标识
     */
    private String roleCode;

    /**
     * 排序值
     * 角色的显示顺序，值越小越靠前
     */
    private Integer sort;

    /**
     * 角色状态
     * 角色的状态，对应 system_role_status 字典数据
     */
    private String roleStatus;

    /**
     * 创建时间
     * 记录创建的时间
     */
    private Date createdTime;

    /**
     * 创建人
     * 记录创建人的用户ID
     */
    private Long createdBy;

    /**
     * 最后修改时间
     * 记录最后一次修改的时间
     */
    private Date lastModifiedTime;

    /**
     * 最后修改人
     * 记录最后一次修改人的用户ID
     */
    private Long lastModifiedBy;

    /**
     * 从创建角色DTO创建角色实体
     * 将角色创建数据转换为实体对象
     *
     * @param createRoleDto 创建角色DTO
     * @return 角色实体对象
     */
    public static RoleEntity of(CreateRoleDto createRoleDto) {
        return new RoleEntity(
                createRoleDto.getRoleCode(),
                createRoleDto.getSort(),
                createRoleDto.getRoleStatus(),
                null,
                null,
                null,
                null
        );
    }

    /**
     * 从更新角色DTO创建角色实体
     * 将角色更新数据转换为实体对象
     *
     * @param updateRoleDto 更新角色DTO
     * @return 角色实体对象
     */
    public static RoleEntity of(UpdateRoleDto updateRoleDto) {
        return new RoleEntity(
                updateRoleDto.getRoleCode(),
                updateRoleDto.getSort(),
                updateRoleDto.getRoleStatus(),
                null,
                null,
                null,
                null
        );
    }

}
