package org.eu.originalkeen.system.role.domain.vo;

import com.fasterxml.jackson.annotation.JsonIgnore;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 角色翻译视图对象
 * 用于返回角色翻译信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class RoleTranslationVo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -1536883389658233679L;

    /**
     * 角色表ID
     * 关联的角色主表ID
     */
    @JsonIgnore
    private Long roleId;

    /**
     * 语言代码
     * 翻译的语言代码，对应 system_language_code 字典数据
     */
    private String languageCode;

    /**
     * 角色名称
     * 角色在该语言下的名称
     */
    private String roleName;

    /**
     * 备注信息
     * 角色的备注说明
     */
    private String remark;

}
