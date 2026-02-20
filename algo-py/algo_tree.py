from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class TreeNode:
    """二叉树节点：val 为节点值，left/right 为左右子节点。"""

    val: int
    left: TreeNode | None = None
    right: TreeNode | None = None

def mid_order(root: TreeNode | None) -> list[int]:
    '''中根遍历二叉树，返回一个列表'''
    if root is None:
        return []
    return mid_order(root.left) + [root.val] + mid_order(root.right)

def pre_order(root: TreeNode | None) -> list[int]:
    '''前根遍历二叉树，返回一个列表'''
    if root is None:
        return []
    return [root.val] + pre_order(root.left) + pre_order(root.right)

def post_order(root: TreeNode | None) -> list[int]:
    '''后根遍历二叉树，返回一个列表'''
    if root is None:
        return []
    return post_order(root.left) + post_order(root.right) + [root.val]

def level_order(root: TreeNode | None) -> list[list[int]]:
    '''层序遍历二叉树，返回一个列表，每个元素是一个列表，表示一层的节点'''
    if root is None:
        return []
    queue = [root]
    result = []
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.pop(0)
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result

def max_depth(root: TreeNode | None) -> int:
    '''返回二叉树的最大深度，即二叉树的层数'''
    if root is None:
        return 0
    return max(max_depth(root.left), max_depth(root.right)) + 1

def max_depth_path(root: TreeNode | None) -> list[int]:
    '''返回二叉树的最大深度分支上的所有节点值（任选一条最深路径）'''
    if root is None:
        return []
    left_path = max_depth_path(root.left)
    right_path = max_depth_path(root.right)
    if len(left_path) >= len(right_path):
        return [root.val] + left_path
    return [root.val] + right_path

def num_trees(n: int) -> int:
    '''返回n个节点的二叉树的种数'''
    if n <= 1:
        return 1
    return sum(num_trees(i) * num_trees(n-i-1) for i in range(n))


def num_trees2(n: int) -> int:
    '''返回n个节点的二叉树的种数, 采用卡塔兰数算法 C_n = C(2n,n)/(n+1)'''
    return math.comb(2 * n, n) // (n + 1)


def is_same_tree(root1: TreeNode | None, root2: TreeNode | None) -> bool:
    '''判断两棵二叉树是否相同'''
    if root1 is None and root2 is None:
        return True
    if root1 is None or root2 is None:
        return False
    return root1.val == root2.val and is_same_tree(root1.left, root2.left) and is_same_tree(root1.right, root2.right)

def is_valid_BST(root: TreeNode | None) -> bool:
    '''判断二叉树是否为有效的二叉搜索树，即中根遍历的节点值是递增的'''
    prev = float('-inf')
    def inorder(node: TreeNode | None) -> bool:
        nonlocal prev
        if node is None:
            return True
        if not inorder(node.left):
            return False
        if node.val <= prev:
            return False
        prev = node.val
        return inorder(node.right)
    return inorder(root)

def sorted_list_to_BST(nums: list[int]) -> TreeNode | None:
    '''将有序列表转换为二叉搜索树'''
    if not nums:
        return None
    mid = len(nums) // 2
    root = TreeNode(nums[mid])
    root.left = sorted_list_to_BST(nums[:mid])
    root.right = sorted_list_to_BST(nums[mid+1:])
    return root

def _tree_levels(root: TreeNode) -> list[list[TreeNode | None]]:
    """层序遍历收集每层节点，用 None 占位以对齐父子。"""
    levels: list[list[TreeNode | None]] = []
    row: list[TreeNode | None] = [root]
    while row:
        levels.append(row)
        next_row: list[TreeNode | None] = []
        for node in row:
            if node is None:
                next_row.extend([None, None])
            else:
                next_row.extend([node.left, node.right])
        if all(n is None for n in next_row):
            break
        row = next_row
    return levels


def print_tree(root: TreeNode | None) -> None:
    '''打印二叉树, 直观显示出根节点与叶子节点之间的关系。输出示例:
           1
         /   \\
        2     3
       / \\   / \\
      4   5 6   7
     / \\
    8   9
    '''
    if root is None:
        print("(空树)")
        return
    levels = _tree_levels(root)
    depth = len(levels)
    w = 2**depth * 4  # 最底层总宽度（字符数）
    line_buf = [" "] * w

    def set_str(buf: list[str], start: int, s: str) -> None:
        start = max(0, start)
        for i, c in enumerate(s):
            if start + i < len(buf):
                buf[start + i] = c

    for i, level in enumerate(levels):
        step = w // (2**i)  # 本层相邻节点中心间距
        # 本层节点行
        for k in range(w):
            line_buf[k] = " "
        for j, node in enumerate(level):
            pos = (2 * j + 1) * step // 2
            s = str(node.val) if node else ""
            set_str(line_buf, pos - len(s) // 2, s)
        print("".join(line_buf).rstrip())

        # 连接线行 / \
        if i >= depth - 1:
            break
        step_next = step // 2
        for k in range(w):
            line_buf[k] = " "
        for j, node in enumerate(level):
            if not node or (not node.left and not node.right):
                continue
            p_pos = (2 * j + 1) * step // 2
            l_pos = (4 * j + 1) * step_next // 2
            r_pos = (4 * j + 3) * step_next // 2
            if node.left:
                set_str(line_buf, (p_pos + l_pos) // 2, "/")
            if node.right:
                set_str(line_buf, (p_pos + r_pos) // 2, "\\")
        print("".join(line_buf).rstrip())


if __name__ == "__main__":
    example_root = TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3, TreeNode(6), TreeNode(7)))
    print(mid_order(example_root))  # [4, 2, 5, 1, 6, 3, 7]
    print(pre_order(example_root))  # [1, 2, 4, 5, 3, 6, 7]
    print(post_order(example_root))  # [4, 5, 2, 6, 7, 3, 1]
    print(level_order(example_root))  # [[1], [2, 3], [4, 5, 6, 7]]
    print(max_depth_path(example_root))   # 一条最深路径，如 [1, 2, 4] 或 [1, 3, 7]
    print(num_trees(7))   # 429
    print(num_trees2(7))  # 429，卡塔兰数
    print(is_same_tree(example_root, example_root))  # True
    print(is_same_tree(example_root, TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3, TreeNode(6), TreeNode(8)))))  # False
    print(is_valid_BST(example_root))  # False
    print(is_valid_BST(TreeNode(2, TreeNode(1), TreeNode(3))))  # True

    print_tree(sorted_list_to_BST([1, 2, 3, 4, 5, 6, 7, 10,15,20,25,30,35,40,45,50]))  # 转换为二叉搜索树
    
