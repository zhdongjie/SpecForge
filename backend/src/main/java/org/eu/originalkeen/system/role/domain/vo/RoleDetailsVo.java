package org.eu.originalkeen.system.role.domain.vo;

import com.mybatisflex.annotation.RelationOneToMany;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;
import java.util.List;

/**
 * 角色详情视图对象
 * 用于返回角色详细信息的数据
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class RoleDetailsVo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -4740826535133584708L;

    /**
     * 角色ID
     * 角色的唯一标识
     */
    private Long id;

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
     * 角色翻译列表
     * 角色的多语言翻译信息
     */
    @RelationOneToMany(
            selfField = "id",
            targetField = "roleId",
            targetTable = "system_role_translation",
            selectColumns = "language_code, role_name, remark"
    )
    private List<RoleTranslationVo> translations;

}
