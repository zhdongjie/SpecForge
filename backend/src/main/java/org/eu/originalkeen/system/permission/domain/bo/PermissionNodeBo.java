package org.eu.originalkeen.system.permission.domain.bo;

import com.mybatisflex.annotation.RelationOneToMany;
import org.eu.originalkeen.core.domain.Tree;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.apache.commons.collections4.CollectionUtils;

import java.io.Serial;
import java.io.Serializable;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

/**
 * 权限节点业务对象
 * 用于表示树形结构的权限节点，实现Tree接口以支持树形结构
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class PermissionNodeBo implements Serializable, Tree<Long, PermissionNodeBo> {

    /**
     * 序列化版本号
     */
    @Serial
    private static final long serialVersionUID = -4421466438171982637L;

    /**
     * 权限ID
     * 权限节点的唯一标识
     */
    private Long id;

    /**
     * 父级ID
     * 父级权限的ID，用于构建权限树结构
     */
    private Long parentId;

    /**
     * 子节点列表
     * 当前权限节点的子权限节点列表，用于构建树形结构
     */
    @RelationOneToMany(
            selfField = "id",
            targetField = "parentId",
            targetTable = "system_permission",
            selectColumns = "id"
    )
    private List<PermissionNodeBo> children;

    /**
     * 获取所有节点ID
     * 获取当前节点及其所有子节点的ID列表
     *
     * @return 节点ID列表
     */
    public Set<Long> getAllNodeIds() {
        Set<Long> nodeIds = new HashSet<>();
        nodeIds.add(this.id);
        addAllChildIds(this.children, nodeIds);
        return nodeIds;
    }

    /**
     * 添加所有子节点ID
     * 递归添加所有子节点的ID到列表中
     *
     * @param nodes   节点列表
     * @param nodeIds 节点ID列表
     */
    private void addAllChildIds(List<PermissionNodeBo> nodes, Set<Long> nodeIds) {
        if (CollectionUtils.isNotEmpty(nodes)) {
            for (PermissionNodeBo node : nodes) {
                nodeIds.add(node.getId());
                List<PermissionNodeBo> childrenNode = node.getChildren();
                addAllChildIds(childrenNode, nodeIds);
            }
        }
    }

}
