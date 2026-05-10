export const findTreePath = <T extends { children: T[] }>(
  keyName: keyof T,
  currentKey: string | number,
  tree: T[]
) => {
  const path: T[] = []

  const dfs = (nodes: T[]) => {
    for (const node of nodes) {
      path.push(node)

      if (node[keyName] === currentKey) return true

      if (node.children?.length && dfs(node.children)) return true

      path.pop()
    }
    return false
  }

  dfs(tree)
  return path
}

export const findTreeNode = <T extends { children: T[] }>(
  keyName: keyof T,
  currentKey: string | number,
  tree: T[]
): T | null => {
  for (const node of tree) {
    if (node[keyName] === currentKey) return node

    const result = findTreeNode(keyName, currentKey, node.children)
    if (result) return result
  }

  return null
}
