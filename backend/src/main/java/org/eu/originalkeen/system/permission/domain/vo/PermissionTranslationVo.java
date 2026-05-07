package org.eu.originalkeen.system.permission.domain.vo;

import com.fasterxml.jackson.annotation.JsonIgnore;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serial;
import java.io.Serializable;

/**
 * 权限翻译视图对象
 * 用于返回权限翻译信息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PermissionTranslationVo implements Serializable {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -6454093916970543817L;

    /**
     * 权限表ID
     * 关联的权限主表ID
     */
    @JsonIgnore
    private Long permissionId;

    /**
     * 语言代码
     * 翻译的语言代码，对应 system_language_code 字典数据
     */
    private String languageCode;

    /**
     * 权限名称
     * 权限在该语言下的名称
     */
    private String permissionName;

} 
