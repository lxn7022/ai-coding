from __future__ import annotations

from bisect import bisect_left
from collections import Counter, defaultdict, deque, OrderedDict
import heapq
from typing import List, Optional


class ListNode:
    def __init__(self, val: int = 0, next: Optional["ListNode"] = None):
        self.val = val
        self.next = next


class Node:
    def __init__(self, x: int, next: "Node" = None, random: "Node" = None):
        self.val = int(x)
        self.next = next
        self.random = random


class TreeNode:
    def __init__(self, val: int = 0, left: Optional["TreeNode"] = None, right: Optional["TreeNode"] = None):
        self.val = val
        self.left = left
        self.right = right


class Solution:
    # 哈希
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        """1. 两数之和
        思路：哈希表记录数值到下标，遍历到当前值时查找补数是否已出现。
        """
        m = {}
        for i, x in enumerate(nums):
            if target - x in m:
                return [m[target - x], i]
            m[x] = i
        return []

    def groupAnagrams(self, strs: List[str]) -> List[List[str]]:
        """49. 字母异位词分组
        思路：将字符串排序后作为键，相同键归为同一组。
        """
        g = defaultdict(list)
        for s in strs:
            g[tuple(sorted(s))].append(s)
        return list(g.values())

    def longestConsecutive(self, nums: List[int]) -> int:
        """128. 最长连续序列
        思路：先放入集合，只从序列起点向右扩展统计连续长度。
        """
        s = set(nums)
        best = 0
        for x in s:
            if x - 1 not in s:
                y = x
                while y in s:
                    y += 1
                best = max(best, y - x)
        return best

    # 双指针
    def moveZeroes(self, nums: List[int]) -> None:
        """283. 移动零
        思路：用写指针前移所有非零元素，再把尾部补零。
        """
        k = 0
        for x in nums:
            if x != 0:
                nums[k] = x
                k += 1
        for i in range(k, len(nums)):
            nums[i] = 0

    def maxArea(self, height: List[int]) -> int:
        """11. 盛最多水的容器
        思路：左右双指针夹逼，每次移动短板并更新面积最大值。
        """
        l, r, ans = 0, len(height) - 1, 0
        while l < r:
            ans = max(ans, (r - l) * min(height[l], height[r]))
            if height[l] < height[r]:
                l += 1
            else:
                r -= 1
        return ans

    def threeSum(self, nums: List[int]) -> List[List[int]]:
        """15. 三数之和
        思路：排序后固定首元素，剩余区间双指针查找并去重。
        """
        nums.sort()
        n = len(nums)
        ans = []
        for i in range(n):
            if i and nums[i] == nums[i - 1]:
                continue
            if nums[i] > 0:
                break
            l, r = i + 1, n - 1
            while l < r:
                s = nums[i] + nums[l] + nums[r]
                if s == 0:
                    ans.append([nums[i], nums[l], nums[r]])
                    l += 1
                    r -= 1
                    while l < r and nums[l] == nums[l - 1]:
                        l += 1
                    while l < r and nums[r] == nums[r + 1]:
                        r -= 1
                elif s < 0:
                    l += 1
                else:
                    r -= 1
        return ans

    def trap(self, height: List[int]) -> int:
        """42. 接雨水
        思路：双指针维护左右最高挡板，按较低侧累计雨水。
        """
        l, r = 0, len(height) - 1
        lm = rm = 0
        ans = 0
        while l < r:
            if height[l] < height[r]:
                lm = max(lm, height[l])
                ans += lm - height[l]
                l += 1
            else:
                rm = max(rm, height[r])
                ans += rm - height[r]
                r -= 1
        return ans

    # 滑动窗口/子串/数组/矩阵
    def lengthOfLongestSubstring(self, s: str) -> int:
        """3. 无重复字符的最长子串
        思路：滑动窗口配合字符最近位置，重复时收缩左边界。
        """
        pos, l, ans = {}, 0, 0
        for r, ch in enumerate(s):
            if ch in pos and pos[ch] >= l:
                l = pos[ch] + 1
            pos[ch] = r
            ans = max(ans, r - l + 1)
        return ans

    def findAnagrams(self, s: str, p: str) -> List[int]:
        """438. 找到字符串中所有字母异位词
        思路：固定长度窗口维护字符计数，与目标计数相等即记录起点。
        """
        if len(p) > len(s):
            return []
        need = Counter(p)
        win = Counter(s[: len(p)])
        ans = [0] if win == need else []
        m = len(p)
        for i in range(m, len(s)):
            win[s[i]] += 1
            c = s[i - m]
            win[c] -= 1
            if win[c] == 0:
                del win[c]
            if win == need:
                ans.append(i - m + 1)
        return ans

    def subarraySum(self, nums: List[int], k: int) -> int:
        """560. 和为 K 的子数组
        思路：前缀和加哈希计数，统计 sum-k 出现次数。
        """
        cnt = defaultdict(int)
        cnt[0] = 1
        s = ans = 0
        for x in nums:
            s += x
            ans += cnt[s - k]
            cnt[s] += 1
        return ans

    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        """239. 滑动窗口最大值
        思路：单调队列维护窗口候选下标，队首即当前最大值下标。
        """
        q = deque()
        ans = []
        for i, x in enumerate(nums):
            while q and q[0] <= i - k:
                q.popleft()
            while q and nums[q[-1]] <= x:
                q.pop()
            q.append(i)
            if i >= k - 1:
                ans.append(nums[q[0]])
        return ans

    def minWindow(self, s: str, t: str) -> str:
        """76. 最小覆盖子串
        思路：右指针扩张满足需求后，左指针尽量收缩更新最短区间。
        """
        need = Counter(t)
        required = len(need)
        win = defaultdict(int)
        formed = l = 0
        best = (10**9, 0, 0)
        for r, ch in enumerate(s):
            win[ch] += 1
            if ch in need and win[ch] == need[ch]:
                formed += 1
            while formed == required:
                if r - l + 1 < best[0]:
                    best = (r - l + 1, l, r)
                c = s[l]
                win[c] -= 1
                if c in need and win[c] < need[c]:
                    formed -= 1
                l += 1
        return "" if best[0] == 10**9 else s[best[1] : best[2] + 1]

    def maxSubArray(self, nums: List[int]) -> int:
        """53. 最大子数组和
        思路：动态规划维护以当前位置结尾的最大和并更新全局最优。
        """
        cur = ans = nums[0]
        for x in nums[1:]:
            cur = max(x, cur + x)
            ans = max(ans, cur)
        return ans

    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        """56. 合并区间
        思路：按起点排序后线性扫描，重叠区间合并到当前结果。
        """
        intervals.sort()
        ans = []
        for a, b in intervals:
            if not ans or ans[-1][1] < a:
                ans.append([a, b])
            else:
                ans[-1][1] = max(ans[-1][1], b)
        return ans

    def rotateArray(self, nums: List[int], k: int) -> None:
        """189. 轮转数组
        思路：k 取模后用切片重组为后 k 段加前 n-k 段。
        """
        n = len(nums)
        k %= n
        nums[:] = nums[-k:] + nums[:-k]

    def productExceptSelf(self, nums: List[int]) -> List[int]:
        """238. 除了自身以外数组的乘积
        思路：先算前缀积写入答案，再反向乘以后缀积。
        """
        n = len(nums)
        ans = [1] * n
        p = 1
        for i in range(n):
            ans[i] = p
            p *= nums[i]
        s = 1
        for i in range(n - 1, -1, -1):
            ans[i] *= s
            s *= nums[i]
        return ans

    def firstMissingPositive(self, nums: List[int]) -> int:
        """41. 缺失的第一个正数
        思路：原地交换把值 x 放到下标 x-1，最后找首个错位位置。
        """
        n = len(nums)
        for i in range(n):
            while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
                j = nums[i] - 1
                nums[i], nums[j] = nums[j], nums[i]
        for i, x in enumerate(nums):
            if x != i + 1:
                return i + 1
        return n + 1

    def setZeroes(self, matrix: List[List[int]]) -> None:
        """73. 矩阵置零
        思路：首行首列作标记位，二次遍历按标记清零并处理首行首列。
        """
        r, c = len(matrix), len(matrix[0])
        row0 = any(matrix[0][j] == 0 for j in range(c))
        col0 = any(matrix[i][0] == 0 for i in range(r))
        for i in range(1, r):
            for j in range(1, c):
                if matrix[i][j] == 0:
                    matrix[i][0] = matrix[0][j] = 0
        for i in range(1, r):
            for j in range(1, c):
                if matrix[i][0] == 0 or matrix[0][j] == 0:
                    matrix[i][j] = 0
        if row0:
            for j in range(c):
                matrix[0][j] = 0
        if col0:
            for i in range(r):
                matrix[i][0] = 0

    def spiralOrder(self, matrix: List[List[int]]) -> List[int]:
        """54. 螺旋矩阵
        思路：维护上下左右边界，按四个方向逐层遍历。
        """
        ans = []
        top, bottom, left, right = 0, len(matrix) - 1, 0, len(matrix[0]) - 1
        while top <= bottom and left <= right:
            for j in range(left, right + 1):
                ans.append(matrix[top][j])
            top += 1
            for i in range(top, bottom + 1):
                ans.append(matrix[i][right])
            right -= 1
            if top <= bottom:
                for j in range(right, left - 1, -1):
                    ans.append(matrix[bottom][j])
                bottom -= 1
            if left <= right:
                for i in range(bottom, top - 1, -1):
                    ans.append(matrix[i][left])
                left += 1
        return ans

    def rotateImage(self, matrix: List[List[int]]) -> None:
        """48. 旋转图像
        思路：先主对角线转置，再逐行反转实现顺时针旋转。
        """
        n = len(matrix)
        for i in range(n):
            for j in range(i + 1, n):
                matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
        for row in matrix:
            row.reverse()

    def searchMatrixII(self, matrix: List[List[int]], target: int) -> bool:
        """240. 搜索二维矩阵 II
        思路：从右上角出发，大于目标左移，小于目标下移。
        """
        if not matrix or not matrix[0]:
            return False
        i, j = 0, len(matrix[0]) - 1
        while i < len(matrix) and j >= 0:
            if matrix[i][j] == target:
                return True
            if matrix[i][j] > target:
                j -= 1
            else:
                i += 1
        return False

    # 链表
    def getIntersectionNode(self, headA: ListNode, headB: ListNode) -> Optional[ListNode]:
        """160. 相交链表
        思路：双指针走完本链后切换到对方链表，最终在交点相遇。
        """
        a, b = headA, headB
        while a != b:
            a = a.next if a else headB
            b = b.next if b else headA
        return a

    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """206. 反转链表
        思路：迭代反转 next 指针，维护前驱与当前节点。
        """
        prev = None
        while head:
            nxt = head.next
            head.next = prev
            prev = head
            head = nxt
        return prev

    def isPalindrome(self, head: Optional[ListNode]) -> bool:
        """234. 回文链表
        思路：将链表值收集到数组，与逆序数组比较。
        """
        vals = []
        while head:
            vals.append(head.val)
            head = head.next
        return vals == vals[::-1]

    def hasCycle(self, head: Optional[ListNode]) -> bool:
        """141. 环形链表
        思路：快慢指针相遇则存在环。
        """
        s = f = head
        while f and f.next:
            s = s.next
            f = f.next.next
            if s == f:
                return True
        return False

    def detectCycle(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """142. 环形链表 II
        思路：快慢指针相遇后，一指针回到头节点同步前进，重逢点即入口。
        """
        s = f = head
        while f and f.next:
            s = s.next
            f = f.next.next
            if s == f:
                p = head
                while p != s:
                    p = p.next
                    s = s.next
                return p
        return None

    def mergeTwoLists(self, list1: Optional[ListNode], list2: Optional[ListNode]) -> Optional[ListNode]:
        """21. 合并两个有序链表
        思路：哑结点加双指针，持续接入较小节点。
        """
        d = cur = ListNode()
        while list1 and list2:
            if list1.val <= list2.val:
                cur.next, list1 = list1, list1.next
            else:
                cur.next, list2 = list2, list2.next
            cur = cur.next
        cur.next = list1 or list2
        return d.next

    def addTwoNumbers(self, l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:
        """2. 两数相加
        思路：逐位相加并处理进位，构建结果链表。
        """
        d = cur = ListNode()
        carry = 0
        while l1 or l2 or carry:
            x = l1.val if l1 else 0
            y = l2.val if l2 else 0
            carry, v = divmod(x + y + carry, 10)
            cur.next = ListNode(v)
            cur = cur.next
            l1 = l1.next if l1 else None
            l2 = l2.next if l2 else None
        return d.next

    def removeNthFromEnd(self, head: Optional[ListNode], n: int) -> Optional[ListNode]:
        """19. 删除链表的倒数第 N 个结点
        思路：快指针先走 n 步，再与慢指针同速前进定位删除点。
        """
        d = ListNode(0, head)
        f = s = d
        for _ in range(n):
            f = f.next
        while f.next:
            f, s = f.next, s.next
        s.next = s.next.next
        return d.next

    def swapPairs(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """24. 两两交换链表中的节点
        思路：以哑结点为前驱，循环重连每一对相邻节点。
        """
        d = ListNode(0, head)
        cur = d
        while cur.next and cur.next.next:
            a, b = cur.next, cur.next.next
            cur.next, a.next, b.next = b, b.next, a
            cur = a
        return d.next

    def reverseKGroup(self, head: Optional[ListNode], k: int) -> Optional[ListNode]:
        """25. K 个一组翻转链表
        思路：每组先确认长度达到 k，再原地反转并接回主链。
        """
        d = ListNode(0, head)
        pre = d
        while True:
            end = pre
            for _ in range(k):
                end = end.next
                if not end:
                    return d.next
            nxt = end.next
            p, cur = nxt, pre.next
            while cur != nxt:
                cur.next, p, cur = p, cur, cur.next
            start = pre.next
            pre.next = end
            pre = start

    def copyRandomList(self, head: "Optional[Node]") -> "Optional[Node]":
        """138. 随机链表的复制
        思路：哈希映射旧节点到新节点，二次遍历补齐 next 与 random。
        """
        if not head:
            return None
        m = {}
        cur = head
        while cur:
            m[cur] = Node(cur.val)
            cur = cur.next
        cur = head
        while cur:
            m[cur].next = m.get(cur.next)
            m[cur].random = m.get(cur.random)
            cur = cur.next
        return m[head]

    def sortList(self, head: Optional[ListNode]) -> Optional[ListNode]:
        """148. 排序链表
        思路：链表归并排序：快慢指针切分，递归排序后合并。
        """
        if not head or not head.next:
            return head
        s, f = head, head.next
        while f and f.next:
            s = s.next
            f = f.next.next
        mid = s.next
        s.next = None
        l = self.sortList(head)
        r = self.sortList(mid)
        return self.mergeTwoLists(l, r)

    def mergeKLists(self, lists: List[Optional[ListNode]]) -> Optional[ListNode]:
        """23. 合并 K 个升序链表
        思路：最小堆维护各链表当前头，弹出最小并推进该链表。
        """
        h = []
        for i, node in enumerate(lists):
            if node:
                heapq.heappush(h, (node.val, i, node))
        d = cur = ListNode()
        while h:
            _, i, node = heapq.heappop(h)
            cur.next = node
            cur = cur.next
            if node.next:
                heapq.heappush(h, (node.next.val, i, node.next))
        return d.next

    # 二叉树
    def inorderTraversal(self, root: Optional[TreeNode]) -> List[int]:
        """94. 二叉树的中序遍历
        思路：显式栈模拟中序遍历过程。
        """
        ans, st = [], []
        while st or root:
            while root:
                st.append(root)
                root = root.left
            root = st.pop()
            ans.append(root.val)
            root = root.right
        return ans

    def maxDepth(self, root: Optional[TreeNode]) -> int:
        """104. 二叉树的最大深度
        思路：递归求左右子树深度并取较大值加一。
        """
        return 0 if not root else 1 + max(self.maxDepth(root.left), self.maxDepth(root.right))

    def invertTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        """226. 翻转二叉树
        思路：递归交换每个节点的左右子树。
        """
        if root:
            root.left, root.right = self.invertTree(root.right), self.invertTree(root.left)
        return root

    def isSymmetric(self, root: Optional[TreeNode]) -> bool:
        """101. 对称二叉树
        思路：递归比较左右子树的镜像位置节点。
        """
        def dfs(a, b):
            if not a and not b:
                return True
            if not a or not b or a.val != b.val:
                return False
            return dfs(a.left, b.right) and dfs(a.right, b.left)
        return dfs(root.left, root.right) if root else True

    def diameterOfBinaryTree(self, root: Optional[TreeNode]) -> int:
        """543. 二叉树的直径
        思路：后序求高度并用左右高度和更新最大直径。
        """
        ans = 0

        def h(node):
            nonlocal ans
            if not node:
                return 0
            l, r = h(node.left), h(node.right)
            ans = max(ans, l + r)
            return max(l, r) + 1

        h(root)
        return ans

    def levelOrder(self, root: Optional[TreeNode]) -> List[List[int]]:
        """102. 二叉树的层序遍历
        思路：队列按层 BFS，每层按当前队列长度处理。
        """
        if not root:
            return []
        q = deque([root])
        ans = []
        while q:
            layer = []
            for _ in range(len(q)):
                n = q.popleft()
                layer.append(n.val)
                if n.left:
                    q.append(n.left)
                if n.right:
                    q.append(n.right)
            ans.append(layer)
        return ans

    def sortedArrayToBST(self, nums: List[int]) -> Optional[TreeNode]:
        """108. 将有序数组转换为二叉搜索树
        思路：每次取中点为根，递归构建左右子树保持平衡。
        """
        def build(l, r):
            if l > r:
                return None
            m = (l + r) // 2
            return TreeNode(nums[m], build(l, m - 1), build(m + 1, r))
        return build(0, len(nums) - 1)

    def isValidBST(self, root: Optional[TreeNode]) -> bool:
        """98. 验证二叉搜索树
        思路：中序遍历应严格递增，比较前驱值校验。
        """
        prev = [None]

        def dfs(node):
            if not node:
                return True
            if not dfs(node.left):
                return False
            if prev[0] is not None and node.val <= prev[0]:
                return False
            prev[0] = node.val
            return dfs(node.right)
        return dfs(root)

    def kthSmallest(self, root: Optional[TreeNode], k: int) -> int:
        """230. 二叉搜索树中第 K 小的元素
        思路：BST 中序有序，遍历到第 k 个节点即答案。
        """
        st = []
        while True:
            while root:
                st.append(root)
                root = root.left
            root = st.pop()
            k -= 1
            if k == 0:
                return root.val
            root = root.right

    def rightSideView(self, root: Optional[TreeNode]) -> List[int]:
        """199. 二叉树的右视图
        思路：层序遍历记录每层最后一个访问节点值。
        """
        if not root:
            return []
        q = deque([root])
        ans = []
        while q:
            for i in range(len(q)):
                node = q.popleft()
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
                if i == 0:
                    pass
            ans.append(node.val)
        return ans

    def flatten(self, root: Optional[TreeNode]) -> None:
        """114. 二叉树展开为链表
        思路：将左子树接到右边，再把原右子树挂到左子树最右节点。
        """
        cur = root
        while cur:
            if cur.left:
                p = cur.left
                while p.right:
                    p = p.right
                p.right = cur.right
                cur.right = cur.left
                cur.left = None
            cur = cur.right

    def buildTree(self, preorder: List[int], inorder: List[int]) -> Optional[TreeNode]:
        """105. 从前序与中序遍历序列构造二叉树
        思路：前序确定根，中序定位分割点，递归构建左右区间。
        """
        idx = {v: i for i, v in enumerate(inorder)}
        pre = 0

        def dfs(l, r):
            nonlocal pre
            if l > r:
                return None
            root = TreeNode(preorder[pre])
            pre += 1
            mid = idx[root.val]
            root.left = dfs(l, mid - 1)
            root.right = dfs(mid + 1, r)
            return root
        return dfs(0, len(inorder) - 1)

    def pathSum(self, root: Optional[TreeNode], targetSum: int) -> int:
        """437. 路径总和 III
        思路：前缀和 DFS，哈希记录路径和频次并在回溯时撤销。
        """
        cnt = defaultdict(int)
        cnt[0] = 1
        ans = 0

        def dfs(node, s):
            nonlocal ans
            if not node:
                return
            s += node.val
            ans += cnt[s - targetSum]
            cnt[s] += 1
            dfs(node.left, s)
            dfs(node.right, s)
            cnt[s] -= 1

        dfs(root, 0)
        return ans

    def lowestCommonAncestor(self, root: TreeNode, p: TreeNode, q: TreeNode) -> TreeNode:
        """236. 二叉树的最近公共祖先
        思路：递归在左右子树查找，若两侧均命中则当前为最近公共祖先。
        """
        if not root or root == p or root == q:
            return root
        l = self.lowestCommonAncestor(root.left, p, q) if root.left else None
        r = self.lowestCommonAncestor(root.right, p, q) if root.right else None
        if l and r:
            return root
        return l or r

    def maxPathSum(self, root: Optional[TreeNode]) -> int:
        """124. 二叉树中的最大路径和
        思路：DFS 返回单边最大贡献，同时尝试经过当前节点连接左右贡献。
        """
        ans = -10**9

        def dfs(node):
            nonlocal ans
            if not node:
                return 0
            l = max(dfs(node.left), 0)
            r = max(dfs(node.right), 0)
            ans = max(ans, node.val + l + r)
            return node.val + max(l, r)

        dfs(root)
        return ans

    # 图论/回溯/二分/栈/堆/贪心/DP
    def numIslands(self, grid: List[List[str]]) -> int:
        """200. 岛屿数量
        思路：遍历网格，遇陆地即 DFS 淹没整块并计数。
        """
        if not grid:
            return 0
        m, n = len(grid), len(grid[0])
        ans = 0

        def dfs(i, j):
            if i < 0 or i >= m or j < 0 or j >= n or grid[i][j] != "1":
                return
            grid[i][j] = "0"
            dfs(i + 1, j)
            dfs(i - 1, j)
            dfs(i, j + 1)
            dfs(i, j - 1)

        for i in range(m):
            for j in range(n):
                if grid[i][j] == "1":
                    ans += 1
                    dfs(i, j)
        return ans

    def orangesRotting(self, grid: List[List[int]]) -> int:
        """994. 腐烂的橘子
        思路：多源 BFS 同步扩散腐烂状态，层数即分钟数。
        """
        m, n = len(grid), len(grid[0])
        q = deque()
        fresh = 0
        for i in range(m):
            for j in range(n):
                if grid[i][j] == 2:
                    q.append((i, j))
                elif grid[i][j] == 1:
                    fresh += 1
        minutes = 0
        while q and fresh:
            for _ in range(len(q)):
                i, j = q.popleft()
                for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ni, nj = i + di, j + dj
                    if 0 <= ni < m and 0 <= nj < n and grid[ni][nj] == 1:
                        grid[ni][nj] = 2
                        fresh -= 1
                        q.append((ni, nj))
            minutes += 1
        return minutes if fresh == 0 else -1

    def canFinish(self, numCourses: int, prerequisites: List[List[int]]) -> bool:
        """207. 课程表
        思路：拓扑排序统计可出队课程数，等于总课程则可完成。
        """
        g = [[] for _ in range(numCourses)]
        indeg = [0] * numCourses
        for a, b in prerequisites:
            g[b].append(a)
            indeg[a] += 1
        q = deque(i for i, d in enumerate(indeg) if d == 0)
        cnt = 0
        while q:
            x = q.popleft()
            cnt += 1
            for y in g[x]:
                indeg[y] -= 1
                if indeg[y] == 0:
                    q.append(y)
        return cnt == numCourses

    def permute(self, nums: List[int]) -> List[List[int]]:
        """46. 全排列
        思路：回溯加 used 标记，逐层选择未使用元素。
        """
        ans = []
        used = [False] * len(nums)
        path = []

        def dfs():
            if len(path) == len(nums):
                ans.append(path[:])
                return
            for i, x in enumerate(nums):
                if used[i]:
                    continue
                used[i] = True
                path.append(x)
                dfs()
                path.pop()
                used[i] = False

        dfs()
        return ans

    def subsets(self, nums: List[int]) -> List[List[int]]:
        """78. 子集
        思路：迭代扩展现有子集，每轮把新元素追加到每个子集。
        """
        ans = [[]]
        for x in nums:
            ans += [a + [x] for a in ans]
        return ans

    def letterCombinations(self, digits: str) -> List[str]:
        """17. 电话号码的字母组合
        思路：按数字顺序做字符集合笛卡尔积扩展。
        """
        if not digits:
            return []
        mp = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl", "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}
        ans = [""]
        for d in digits:
            ans = [p + c for p in ans for c in mp[d]]
        return ans

    def combinationSum(self, candidates: List[int], target: int) -> List[List[int]]:
        """39. 组合总和
        思路：回溯枚举候选，允许重复使用当前下标并按剩余值剪枝。
        """
        candidates.sort()
        ans = []
        path = []

        def dfs(i, remain):
            if remain == 0:
                # 命中目标：记录当前组合
                ans.append(path[:])
                return
            for j in range(i, len(candidates)):
                # 候选已排序，超过剩余值可直接剪枝
                if candidates[j] > remain:
                    break
                # 选择当前数字（允许重复使用同一数字）
                path.append(candidates[j])
                dfs(j, remain - candidates[j])
                # 回溯，撤销本次选择
                path.pop()

        dfs(0, target)
        return ans

    def generateParenthesis(self, n: int) -> List[str]:
        """22. 括号生成
        思路：回溯控制左右括号数量，保证任意前缀合法。
        """
        ans = []

        def dfs(s, l, r):
            if len(s) == 2 * n:
                ans.append(s)
                return
            if l < n:
                dfs(s + "(", l + 1, r)
            if r < l:
                dfs(s + ")", l, r + 1)

        dfs("", 0, 0)
        return ans

    def exist(self, board: List[List[str]], word: str) -> bool:
        """79. 单词搜索
        思路：网格 DFS 回溯，临时标记已访问格避免重复使用。
        """
        m, n = len(board), len(board[0])

        def dfs(i, j, k):
            if k == len(word):
                return True
            if i < 0 or i >= m or j < 0 or j >= n or board[i][j] != word[k]:
                return False
            c = board[i][j]
            board[i][j] = "#"
            ok = dfs(i + 1, j, k + 1) or dfs(i - 1, j, k + 1) or dfs(i, j + 1, k + 1) or dfs(i, j - 1, k + 1)
            board[i][j] = c
            return ok
        for i in range(m):
            for j in range(n):
                if dfs(i, j, 0):
                    return True
        return False

    def partition(self, s: str) -> List[List[str]]:
        """131. 分割回文串
        思路：回溯枚举切分点，仅在当前子串为回文时继续。
        """
        ans = []
        path = []

        def dfs(i):
            if i == len(s):
                ans.append(path[:])
                return
            for j in range(i, len(s)):
                t = s[i : j + 1]
                if t == t[::-1]:
                    path.append(t)
                    dfs(j + 1)
                    path.pop()

        dfs(0)
        return ans

    def solveNQueens(self, n: int) -> List[List[str]]:
        """51. N 皇后
        思路：按行回溯，使用列与对角线集合剪枝。
        """
        cols, d1, d2 = set(), set(), set()
        board = [["."] * n for _ in range(n)]
        ans = []

        def dfs(r):
            if r == n:
                ans.append(["".join(row) for row in board])
                return
            for c in range(n):
                if c in cols or r - c in d1 or r + c in d2:
                    continue
                cols.add(c)
                d1.add(r - c)
                d2.add(r + c)
                board[r][c] = "Q"
                dfs(r + 1)
                board[r][c] = "."
                cols.remove(c)
                d1.remove(r - c)
                d2.remove(r + c)

        dfs(0)
        return ans

    def searchInsert(self, nums: List[int], target: int) -> int:
        """35. 搜索插入位置
        思路：使用二分返回目标最左插入位置。
        """
        return bisect_left(nums, target)

    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
        """74. 搜索二维矩阵
        思路：将二维矩阵映射为一维有序数组后二分查找。
        """
        m, n = len(matrix), len(matrix[0])
        l, r = 0, m * n - 1
        while l <= r:
            mid = (l + r) // 2
            x = matrix[mid // n][mid % n]
            if x == target:
                return True
            if x < target:
                l = mid + 1
            else:
                r = mid - 1
        return False

    def searchRange(self, nums: List[int], target: int) -> List[int]:
        """34. 在排序数组中查找元素的第一个和最后一个位置
        思路：两次二分分别求目标左边界与右边界。
        """
        l = bisect_left(nums, target)
        if l == len(nums) or nums[l] != target:
            return [-1, -1]
        r = bisect_left(nums, target + 1) - 1
        return [l, r]

    def search(self, nums: List[int], target: int) -> int:
        """33. 搜索旋转排序数组
        思路：二分时先判断哪半段有序，再决定去向。
        """
        l, r = 0, len(nums) - 1
        while l <= r:
            m = (l + r) // 2
            if nums[m] == target:
                return m
            if nums[l] <= nums[m]:
                if nums[l] <= target < nums[m]:
                    r = m - 1
                else:
                    l = m + 1
            else:
                if nums[m] < target <= nums[r]:
                    l = m + 1
                else:
                    r = m - 1
        return -1

    def findMin(self, nums: List[int]) -> int:
        """153. 寻找旋转排序数组中的最小值
        思路：二分比较中点与右端值，收缩到最小值区间。
        """
        l, r = 0, len(nums) - 1
        while l < r:
            m = (l + r) // 2
            if nums[m] > nums[r]:
                l = m + 1
            else:
                r = m
        return nums[l]

    def findMedianSortedArrays(self, nums1: List[int], nums2: List[int]) -> float:
        """4. 寻找两个正序数组的中位数
        思路：当前实现先合并排序，再按长度奇偶直接取中位数。
        """
        a = sorted(nums1 + nums2)
        n = len(a)
        if n % 2:
            return float(a[n // 2])
        return (a[n // 2 - 1] + a[n // 2]) / 2

    def isValid(self, s: str) -> bool:
        """20. 有效的括号
        思路：栈匹配括号，右括号必须对应栈顶左括号。
        """
        mp = {")": "(", "]": "[", "}": "{"}
        st = []
        for c in s:
            if c in "([{":
                st.append(c)
            elif not st or st.pop() != mp[c]:
                return False
        return not st

    def decodeString(self, s: str) -> str:
        """394. 字符串解码
        思路：栈保存进入括号前的字符串和倍数，遇 ] 时展开回填。
        """
        st = []
        num = 0
        cur = ""
        for c in s:
            if c.isdigit():
                num = num * 10 + int(c)
            elif c == "[":
                st.append((cur, num))
                cur, num = "", 0
            elif c == "]":
                pre, k = st.pop()
                cur = pre + cur * k
            else:
                cur += c
        return cur

    def dailyTemperatures(self, temperatures: List[int]) -> List[int]:
        """739. 每日温度
        思路：单调递减栈存下标，遇更高温度时结算等待天数。
        """
        ans = [0] * len(temperatures)
        st = []
        for i, t in enumerate(temperatures):
            while st and temperatures[st[-1]] < t:
                j = st.pop()
                ans[j] = i - j
            st.append(i)
        return ans

    def largestRectangleArea(self, heights: List[int]) -> int:
        """84. 柱状图中最大的矩形
        思路：单调递增栈，遇更矮柱子时弹栈并计算矩形面积。
        """
        st = []
        ans = 0
        for i, h in enumerate(heights + [0]):
            while st and heights[st[-1]] > h:
                H = heights[st.pop()]
                L = st[-1] + 1 if st else 0
                ans = max(ans, H * (i - L))
            st.append(i)
        return ans

    def findKthLargest(self, nums: List[int], k: int) -> int:
        """215. 数组中的第K个最大元素
        思路：调用 nlargest 取前 k 大，末位即第 k 大。
        """
        return heapq.nlargest(k, nums)[-1]

    def topKFrequent(self, nums: List[int], k: int) -> List[int]:
        """347. 前 K 个高频元素
        思路：Counter 计数后取 most_common(k)。
        """
        return [x for x, _ in Counter(nums).most_common(k)]

    def maxProfit(self, prices: List[int]) -> int:
        """121. 买卖股票的最佳时机
        思路：遍历维护历史最低价并更新最大利润。
        """
        mn = 10**9
        ans = 0
        for p in prices:
            mn = min(mn, p)
            ans = max(ans, p - mn)
        return ans

    def canJump(self, nums: List[int]) -> bool:
        """55. 跳跃游戏
        思路：贪心维护最远可达下标，若当前位置超出则失败。
        """
        far = 0
        for i, x in enumerate(nums):
            if i > far:
                return False
            far = max(far, i + x)
        return True

    def jump(self, nums: List[int]) -> int:
        """45. 跳跃游戏 II
        思路：按层贪心维护当前步边界与下一步最远边界。
        """
        step = end = far = 0
        for i in range(len(nums) - 1):
            far = max(far, i + nums[i])
            if i == end:
                step += 1
                end = far
        return step

    def partitionLabels(self, s: str) -> List[int]:
        """763. 划分字母区间
        思路：记录字符最后出现位置，扫描到当前段尾即切分。
        """
        last = {c: i for i, c in enumerate(s)}
        ans = []
        st = ed = 0
        for i, c in enumerate(s):
            ed = max(ed, last[c])
            if i == ed:
                ans.append(ed - st + 1)
                st = i + 1
        return ans

    def climbStairs(self, n: int) -> int:
        """70. 爬楼梯
        思路：斐波那契递推，使用两个变量滚动更新。
        """
        a, b = 1, 1
        for _ in range(n):
            a, b = b, a + b
        return a

    def generate(self, numRows: int) -> List[List[int]]:
        """118. 杨辉三角
        思路：逐行构造杨辉三角，中间值由上一行相邻两数相加。
        """
        ans = []
        for i in range(numRows):
            row = [1] * (i + 1)
            for j in range(1, i):
                row[j] = ans[i - 1][j - 1] + ans[i - 1][j]
            ans.append(row)
        return ans

    def rob(self, nums: List[int]) -> int:
        """198. 打家劫舍
        思路：滚动动态规划，维护抢当前与不抢当前的最优值。
        """
        a = b = 0
        for x in nums:
            a, b = b, max(b, a + x)
        return b

    def numSquares(self, n: int) -> int:
        """279. 完全平方数
        思路：完全背包动态规划，dp[i] 表示组成 i 的最少平方数个数。
        """
        dp = [0] + [10**9] * n
        sq = [i * i for i in range(1, int(n**0.5) + 1)]
        for i in range(1, n + 1):
            dp[i] = min(dp[i - x] + 1 for x in sq if x <= i)
        return dp[n]

    def coinChange(self, coins: List[int], amount: int) -> int:
        """322. 零钱兑换
        思路：完全背包动态规划，逐金额更新最少硬币数量。
        """
        dp = [amount + 1] * (amount + 1)
        dp[0] = 0
        for a in range(1, amount + 1):
            for c in coins:
                if c <= a:
                    dp[a] = min(dp[a], dp[a - c] + 1)
        return -1 if dp[amount] == amount + 1 else dp[amount]

    def wordBreak(self, s: str, wordDict: List[str]) -> bool:
        """139. 单词拆分
        思路：前缀 DP，存在可达切分点且后段在词典中则为真。
        """
        st = set(wordDict)
        dp = [False] * (len(s) + 1)
        dp[0] = True
        for i in range(1, len(s) + 1):
            for j in range(i):
                if dp[j] and s[j:i] in st:
                    dp[i] = True
                    break
        return dp[-1]

    def lengthOfLIS(self, nums: List[int]) -> int:
        """300. 最长递增子序列
        思路：贪心加二分维护 tails 数组，长度即 LIS 长度。
        """
        tails = []
        for x in nums:
            i = bisect_left(tails, x)
            if i == len(tails):
                tails.append(x)
            else:
                tails[i] = x
        return len(tails)

    def maxProduct(self, nums: List[int]) -> int:
        """152. 乘积最大子数组
        思路：同时维护当前位置最大乘积和最小乘积以处理负数翻转。
        """
        mx = mn = ans = nums[0]
        for x in nums[1:]:
            if x < 0:
                mx, mn = mn, mx
            mx = max(x, mx * x)
            mn = min(x, mn * x)
            ans = max(ans, mx)
        return ans

    def canPartition(self, nums: List[int]) -> bool:
        """416. 分割等和子集
        思路：转化为 0/1 背包，判断是否能凑到总和一半。
        """
        s = sum(nums)
        if s % 2:
            return False
        t = s // 2
        dp = [False] * (t + 1)
        dp[0] = True
        for x in nums:
            for j in range(t, x - 1, -1):
                dp[j] = dp[j] or dp[j - x]
        return dp[t]

    def longestValidParentheses(self, s: str) -> int:
        """32. 最长有效括号
        思路：栈存下标并设哨兵，利用下标差计算最长合法长度。
        """
        st = [-1]
        ans = 0
        for i, c in enumerate(s):
            if c == "(":
                st.append(i)
            else:
                st.pop()
                if not st:
                    st.append(i)
                else:
                    ans = max(ans, i - st[-1])
        return ans

    def uniquePaths(self, m: int, n: int) -> int:
        """62. 不同路径
        思路：一维 DP，当前位置路径数等于上方与左方之和。
        """
        dp = [1] * n
        for _ in range(m - 1):
            for j in range(1, n):
                dp[j] += dp[j - 1]
        return dp[-1]

    def minPathSum(self, grid: List[List[int]]) -> int:
        """64. 最小路径和
        思路：一维滚动 DP，当前位置取上方与左方较小值再加当前格。
        """
        m, n = len(grid), len(grid[0])
        dp = [10**9] * n
        dp[0] = 0
        for i in range(m):
            dp[0] += grid[i][0]
            for j in range(1, n):
                dp[j] = min(dp[j], dp[j - 1]) + grid[i][j]
        return dp[-1]

    def longestPalindrome(self, s: str) -> str:
        """5. 最长回文子串
        思路：以每个位置为中心做奇偶扩展，维护最长区间。
        """
        start = end = 0

        def expand(l, r):
            while l >= 0 and r < len(s) and s[l] == s[r]:
                l -= 1
                r += 1
            return l + 1, r - 1
        for i in range(len(s)):
            l1, r1 = expand(i, i)
            l2, r2 = expand(i, i + 1)
            if r1 - l1 > end - start:
                start, end = l1, r1
            if r2 - l2 > end - start:
                start, end = l2, r2
        return s[start : end + 1]

    def longestCommonSubsequence(self, text1: str, text2: str) -> int:
        """1143. 最长公共子序列
        思路：经典 LCS 动态规划，此实现用一维数组滚动优化。
        """
        m, n = len(text1), len(text2)
        dp = [0] * (n + 1)
        for i in range(1, m + 1):
            pre = 0
            for j in range(1, n + 1):
                cur = dp[j]
                if text1[i - 1] == text2[j - 1]:
                    dp[j] = pre + 1
                else:
                    dp[j] = max(dp[j], dp[j - 1])
                pre = cur
        return dp[n]

    def minDistance(self, word1: str, word2: str) -> int:
        """72. 编辑距离
        思路：编辑距离 DP，转移考虑插入、删除、替换三种操作。
        """
        m, n = len(word1), len(word2)
        dp = list(range(n + 1))
        for i in range(1, m + 1):
            pre = dp[0]
            dp[0] = i
            for j in range(1, n + 1):
                cur = dp[j]
                if word1[i - 1] == word2[j - 1]:
                    dp[j] = pre
                else:
                    dp[j] = 1 + min(pre, dp[j], dp[j - 1])
                pre = cur
        return dp[n]

    def singleNumber(self, nums: List[int]) -> int:
        """136. 只出现一次的数字
        思路：整体异或，成对数字抵消后剩唯一值。
        """
        x = 0
        for n in nums:
            x ^= n
        return x

    def majorityElement(self, nums: List[int]) -> int:
        """169. 多数元素
        思路：Boyer-Moore 投票法维护候选值与计数。
        """
        cand = cnt = 0
        for x in nums:
            if cnt == 0:
                cand = x
            cnt += 1 if x == cand else -1
        return cand

    def sortColors(self, nums: List[int]) -> None:
        """75. 颜色分类
        思路：荷兰国旗三指针原地划分 0、1、2 区间。
        """
        l, i, r = 0, 0, len(nums) - 1
        while i <= r:
            if nums[i] == 0:
                nums[l], nums[i] = nums[i], nums[l]
                l += 1
                i += 1
            elif nums[i] == 2:
                nums[i], nums[r] = nums[r], nums[i]
                r -= 1
            else:
                i += 1

    def nextPermutation(self, nums: List[int]) -> None:
        """31. 下一个排列
        思路：从右找下降位，交换后反转后缀得到下一个排列。
        """
        i = len(nums) - 2
        while i >= 0 and nums[i] >= nums[i + 1]:
            i -= 1
        if i >= 0:
            j = len(nums) - 1
            while nums[j] <= nums[i]:
                j -= 1
            nums[i], nums[j] = nums[j], nums[i]
        nums[i + 1 :] = reversed(nums[i + 1 :])

    def findDuplicate(self, nums: List[int]) -> int:
        """287. 寻找重复数
        思路：将数组视为链表，用快慢指针找环入口作为重复数。
        """
        s = f = nums[0]
        while True:
            s = nums[s]
            f = nums[nums[f]]
            if s == f:
                break
        s = nums[0]
        while s != f:
            s = nums[s]
            f = nums[f]
        return s


class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.od = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.od:
            return -1
        self.od.move_to_end(key)
        return self.od[key]

    def put(self, key: int, value: int) -> None:
        if key in self.od:
            self.od.move_to_end(key)
        self.od[key] = value
        if len(self.od) > self.cap:
            self.od.popitem(last=False)


class Trie:
    def __init__(self):
        self.root = {}
        self.end = "#"

    def insert(self, word: str) -> None:
        cur = self.root
        for c in word:
            cur = cur.setdefault(c, {})
        cur[self.end] = True

    def search(self, word: str) -> bool:
        cur = self.root
        for c in word:
            if c not in cur:
                return False
            cur = cur[c]
        return self.end in cur

    def startsWith(self, prefix: str) -> bool:
        cur = self.root
        for c in prefix:
            if c not in cur:
                return False
            cur = cur[c]
        return True


class MinStack:
    def __init__(self):
        self.st = []
        self.mn = []

    def push(self, val: int) -> None:
        self.st.append(val)
        self.mn.append(val if not self.mn else min(val, self.mn[-1]))

    def pop(self) -> None:
        self.st.pop()
        self.mn.pop()

    def top(self) -> int:
        return self.st[-1]

    def getMin(self) -> int:
        return self.mn[-1]


class MedianFinder:
    def __init__(self):
        self.low = []
        self.high = []

    def addNum(self, num: int) -> None:
        heapq.heappush(self.low, -num)
        heapq.heappush(self.high, -heapq.heappop(self.low))
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def findMedian(self) -> float:
        if len(self.low) > len(self.high):
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2.0
