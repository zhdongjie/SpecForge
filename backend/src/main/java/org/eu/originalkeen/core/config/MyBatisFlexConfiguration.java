package org.eu.originalkeen.core.config;

import com.mybatisflex.annotation.InsertListener;
import com.mybatisflex.annotation.UpdateListener;
import com.mybatisflex.core.FlexGlobalConfig;
import com.mybatisflex.core.audit.AuditManager;
import com.mybatisflex.core.audit.ConsoleMessageCollector;
import com.mybatisflex.core.audit.MessageCollector;
import com.mybatisflex.spring.boot.MyBatisFlexCustomizer;
import org.eu.originalkeen.core.domain.Audit;
import org.eu.originalkeen.core.domain.entity.PrimaryKeyEntity;
import org.eu.originalkeen.core.utils.SecurityUtils;
import org.springframework.context.annotation.Configuration;

import java.util.Date;

/**
 * MyBatisFlex配置类
 * 负责配置MyBatisFlex的全局设置，包括审计功能和实体监听器
 */
@Configuration
public class MyBatisFlexConfiguration implements MyBatisFlexCustomizer, InsertListener, UpdateListener {

    /**
     * 自定义MyBatisFlex全局配置
     * 启用审计功能，配置消息收集器，注册实体监听器
     *
     * @param globalConfig MyBatisFlex全局配置对象
     */
    @Override
    public void customize(FlexGlobalConfig globalConfig) {
        AuditManager.setAuditEnable(true);

        MessageCollector collector = new ConsoleMessageCollector();
        AuditManager.setMessageCollector(collector);

        globalConfig.registerInsertListener(this, PrimaryKeyEntity.class);

        globalConfig.registerUpdateListener(this, PrimaryKeyEntity.class);
    }

    /**
     * 实体插入监听器
     * 在实体插入前自动设置审计字段（创建时间、创建人等）
     *
     * @param entity 要插入的实体对象
     */
    @Override
    public void onInsert(Object entity) {
        if (entity instanceof Audit audit) {
            Date currentTime = new Date(System.currentTimeMillis());
            Long userId = SecurityUtils.getUserId();

            audit.setCreatedBy(userId);
            audit.setCreatedTime(currentTime);
            audit.setLastModifiedBy(userId);
            audit.setLastModifiedTime(currentTime);
        }
    }

    /**
     * 实体更新监听器
     * 在实体更新前自动设置审计字段（最后修改时间、最后修改人）
     *
     * @param entity 要更新的实体对象
     */
    @Override
    public void onUpdate(Object entity) {
        if (entity instanceof Audit audit) {
            Date currentTime = new Date(System.currentTimeMillis());
            Long userId = SecurityUtils.getUserId();

            audit.setLastModifiedBy(userId);
            audit.setLastModifiedTime(currentTime);
        }
    }

}
