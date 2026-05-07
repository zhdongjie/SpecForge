package org.eu.originalkeen.core.domain;

import java.util.List;

/**
 * 树形结构接口
 * 用于定义树形结构数据的必要方法，支持树形数据的构建和遍历
 *
 * @param <K> 节点ID的类型
 * @param <T> 实现树接口的子类类型
 */
public interface Tree<K, T extends Tree<K, T>> {

    /**
     * 获取节点ID
     * 返回当前节点的唯一标识
     *
     * @return 节点ID
     */
    K getId();

    /**
     * 获取父节点ID
     * 返回当前节点的父节点ID，用于构建树形结构
     *
     * @return 父节点ID
     */
    K getParentId();

    /**
     * 获取子节点列表
     * 返回当前节点的所有子节点列表
     *
     * @return 子节点列表
     */
    List<T> getChildren();

}
