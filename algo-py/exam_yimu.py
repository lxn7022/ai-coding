from __future__ import annotations

import math
from dataclasses import dataclass


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



PRD = """
1、给定一个二叉树的 根节点 root，想象自己站在它的右侧，
按照从顶部到底部的顺序，返回从右侧所能看到的节点值。

"""


@dataclass
class TreeNode:
    val: int
    left: TreeNode | None = None
    right: TreeNode | None = None
    
def right_side_view(root: TreeNode | None) -> list[int]:
    """先根遍历一棵树，返回一个列表，列表的元素是树的右视图"""
    if root is None:
        return []
    return [root.val] + right_side_view(root.right)


def right_side_view2(root: TreeNode | None) -> list[int]:
    """层次遍历一棵树，返回一个列表，列表的元素是树的每一层的最右边的节点"""
    if root is None:
        return []
    queue = [root]
    result = []
    while queue:
        level_size = len(queue)
        for i in range(level_size):
            node = queue.pop(0)
            if i == level_size - 1:  # 当前层最后一个（最右）
                result.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
    return result


PRD2 = """
2、假设你正在爬楼梯。需要 n 阶你才能到达楼顶。
每次你可以爬 1 或 2 个台阶。你有多少种不同的方法可以爬到楼顶呢？要求空间复杂度O(1),时间复杂度不高于O(n)
 
示例 1：
输入：n = 2输出：2
解释：有两种方法可以爬到楼顶。
1. 1 阶 + 1 阶
2. 2 阶
示例 2：
输入：n = 3输出：3
解释：有三种方法可以爬到楼顶。
1. 1 阶 + 1 阶 + 1 阶
2. 1 阶 + 2 阶
3. 2 阶 + 1 阶
 
提示：
1 <= n <= 45


这是经典的「爬楼梯」问题：共有 n 阶，每次只能走 1 阶或 2 阶，求到达楼顶有多少种不同走法。

思路

到第 n 阶的最后一步只有两种可能：从第 n-1 阶走 1 步，或从第 n-2 阶走 2 步。
因此：f(n) = f(n-1) + f(n-2)，是一个斐波那契递推式。

实现要点

边界条件
    n=1：只有 1 种（走 1 阶）→ 返回 1
    n=2：有 2 种（1+1 或 2）→ 返回 2
递推（n ≥ 3）
    用 a, b 保存 f(n-2) 和 f(n-1)，在循环里滚动更新为 f(n-1) 和 f(n)。
    每次做 a, b = b, a + b，最后 b 就是 f(n)。
复杂度
    时间 O(n)，空间 O(1)，比纯递归更高效。

"""

def step_count(n: int) -> int:
    """假设有n阶楼梯,每次可以爬 1 或 2 个台阶, 返回有多少种不同的方法可以爬到楼顶"""
    if n == 1:  # 1阶：1种
        return 1
    if n == 2:  # 2阶：2种（1+1 或 2）
        return 2
    # 递推：f(n)=f(n-1)+f(n-2)，用两个变量滚动计算
    a, b = 1, 2
    for _ in range(3, n + 1):
        a, b = b, a + b
    return b

def step_count2(n: int) -> int:
    """假设有n阶楼梯,每次可以爬 1 或 2 个台阶, 返回有多少种不同的方法可以爬到楼顶, 使用递归算法
    n ≤ 0：返回 [[]]，表示已到达楼顶，只有一种走法
    n = 1：返回 [[1]]，即一步走 1 阶
    n ≥ 2：递归合并两类走法——先走 1 阶的 [[1] + path for path in step_count3(n-1)]，
            和先走 2 阶的 [[2] + path for path in step_count3(n-2)]
    
    """
    if n == 1:  # 1阶：1种
        return 1
    if n == 2:  # 2阶：2种（1+1 或 2）
        return 2
    return step_count2(n-1) + step_count2(n-2)

def step_count3(n: int) -> list[list[int]]:
    """假设你正在爬楼梯。需要 n 阶你才能到达楼顶，每次你可以爬 1 或 2 个台阶。返回不同的爬法的列表
    n ≤ 0：返回 [[]]，表示已到达楼顶，只有一种走法
    n = 1：返回 [[1]]，即一步走 1 阶
    n ≥ 2：递归合并两类走法——先走 1 阶的 [[1] + path for path in step_count3(n-1)]，
            和先走 2 阶的 [[2] + path for path in step_count3(n-2)]
    """
    if n <= 0:
        return [[]]
    if n == 1:
        return [[1]]
    return [[1] + path for path in step_count3(n - 1)] + [[2] + path for path in step_count3(n - 2)]    

if __name__ == "__main__":
    # 测试用例: 完整二叉树
    root = TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)))
    print("树结构:")
    print_tree(root)
    #print("right_side_view:", right_side_view(root))
    print("right_side_view2:", right_side_view2(root))

    # 空树
    print("\n空树 right_side_view2:", right_side_view2(None))

    # 单节点
    single = TreeNode(1)
    print("单节点 right_side_view2:", right_side_view2(single))

    # 仅左子树（测试每层最右）
    left_only = TreeNode(1, TreeNode(2, TreeNode(3)))
    print("仅左子树 right_side_view2:", right_side_view2(left_only))

    # 测试 step_count / step_count2
    print("\nstep_count / step_count2 爬楼梯:")
    for n in [1, 2, 3, 4, 5, 10]:
        r1, r2 = step_count(n), step_count2(n)
        print(f"  n={n} -> step_count={r1}, step_count2={r2} 种方法")

    # 测试 step_count3（返回所有爬法路径）
    print("\nstep_count3 爬楼梯路径:")
    for n in [1, 2, 3, 4]:
        paths = step_count3(n)
        print(f"  n={n} -> {len(paths)} 种: {paths}")
