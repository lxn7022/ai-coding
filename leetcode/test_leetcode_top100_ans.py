import os
import sys
import unittest

sys.path.append(os.path.dirname(__file__))

from leetcode_top100_ans import (
    LRUCache,
    ListNode,
    MedianFinder,
    MinStack,
    Node,
    Solution,
    TreeNode,
    Trie,
)


def build_list(vals):
    d = ListNode()
    c = d
    for v in vals:
        c.next = ListNode(v)
        c = c.next
    return d.next


def to_list(head):
    out = []
    while head:
        out.append(head.val)
        head = head.next
    return out


class TestLeetCodeTop100(unittest.TestCase):
    def test_top100_core(self):
        s = Solution()
        self.assertEqual(s.twoSum([2, 7, 11, 15], 9), [0, 1])
        self.assertEqual(sorted([sorted(g) for g in s.groupAnagrams(["eat", "tea", "tan", "ate", "nat", "bat"])]), sorted([["ate", "eat", "tea"], ["nat", "tan"], ["bat"]]))
        self.assertEqual(s.longestConsecutive([100, 4, 200, 1, 3, 2]), 4)

        arr = [0, 1, 0, 3, 12]
        s.moveZeroes(arr)
        self.assertEqual(arr, [1, 3, 12, 0, 0])
        self.assertEqual(s.maxArea([1, 8, 6, 2, 5, 4, 8, 3, 7]), 49)
        self.assertEqual(sorted(s.threeSum([-1, 0, 1, 2, -1, -4])), [[-1, -1, 2], [-1, 0, 1]])
        self.assertEqual(s.trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]), 6)

        self.assertEqual(s.lengthOfLongestSubstring("abcabcbb"), 3)
        self.assertEqual(s.findAnagrams("cbaebabacd", "abc"), [0, 6])
        self.assertEqual(s.subarraySum([1, 1, 1], 2), 2)
        self.assertEqual(s.maxSlidingWindow([1, 3, -1, -3, 5, 3, 6, 7], 3), [3, 3, 5, 5, 6, 7])
        self.assertEqual(s.minWindow("ADOBECODEBANC", "ABC"), "BANC")

        self.assertEqual(s.maxSubArray([-2, 1, -3, 4, -1, 2, 1, -5, 4]), 6)
        self.assertEqual(s.merge([[1, 3], [2, 6], [8, 10], [15, 18]]), [[1, 6], [8, 10], [15, 18]])
        arr = [1, 2, 3, 4, 5, 6, 7]
        s.rotateArray(arr, 3)
        self.assertEqual(arr, [5, 6, 7, 1, 2, 3, 4])
        self.assertEqual(s.productExceptSelf([1, 2, 3, 4]), [24, 12, 8, 6])
        self.assertEqual(s.firstMissingPositive([3, 4, -1, 1]), 2)
        m = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
        s.setZeroes(m)
        self.assertEqual(m, [[1, 0, 1], [0, 0, 0], [1, 0, 1]])
        self.assertEqual(s.spiralOrder([[1, 2, 3], [4, 5, 6], [7, 8, 9]]), [1, 2, 3, 6, 9, 8, 7, 4, 5])
        m = [[1, 2], [3, 4]]
        s.rotateImage(m)
        self.assertEqual(m, [[3, 1], [4, 2]])
        self.assertTrue(s.searchMatrixII([[1, 4, 7], [2, 5, 8], [3, 6, 9]], 6))

        inter = build_list([8, 4, 5])
        a = ListNode(4, ListNode(1, inter))
        b = ListNode(5, ListNode(0, ListNode(1, inter)))
        self.assertIs(s.getIntersectionNode(a, b), inter)
        self.assertEqual(to_list(s.reverseList(build_list([1, 2, 3]))), [3, 2, 1])
        self.assertTrue(s.isPalindrome(build_list([1, 2, 2, 1])))
        cyc = build_list([3, 2, 0, -4])
        cyc.next.next.next.next = cyc.next
        self.assertTrue(s.hasCycle(cyc))
        self.assertEqual(s.detectCycle(cyc).val, 2)
        self.assertEqual(to_list(s.mergeTwoLists(build_list([1, 2, 4]), build_list([1, 3, 4]))), [1, 1, 2, 3, 4, 4])
        self.assertEqual(to_list(s.addTwoNumbers(build_list([2, 4, 3]), build_list([5, 6, 4]))), [7, 0, 8])
        self.assertEqual(to_list(s.removeNthFromEnd(build_list([1, 2, 3, 4, 5]), 2)), [1, 2, 3, 5])
        self.assertEqual(to_list(s.swapPairs(build_list([1, 2, 3, 4]))), [2, 1, 4, 3])
        self.assertEqual(to_list(s.reverseKGroup(build_list([1, 2, 3, 4, 5]), 2)), [2, 1, 4, 3, 5])
        n1 = Node(7)
        n2 = Node(13)
        n1.next = n2
        n2.random = n1
        cp = s.copyRandomList(n1)
        self.assertEqual(cp.val, 7)
        self.assertEqual(cp.next.random.val, 7)
        self.assertEqual(to_list(s.sortList(build_list([4, 2, 1, 3]))), [1, 2, 3, 4])
        self.assertEqual(to_list(s.mergeKLists([build_list([1, 4, 5]), build_list([1, 3, 4]), build_list([2, 6])])), [1, 1, 2, 3, 4, 4, 5, 6])

        root = TreeNode(1, None, TreeNode(2, TreeNode(3)))
        self.assertEqual(s.inorderTraversal(root), [1, 3, 2])
        self.assertEqual(s.maxDepth(TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))), 3)
        inv = s.invertTree(TreeNode(2, TreeNode(1), TreeNode(3)))
        self.assertEqual([inv.val, inv.left.val, inv.right.val], [2, 3, 1])
        self.assertTrue(s.isSymmetric(TreeNode(1, TreeNode(2, TreeNode(3), TreeNode(4)), TreeNode(2, TreeNode(4), TreeNode(3)))))
        self.assertEqual(s.diameterOfBinaryTree(TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3))), 3)
        self.assertEqual(s.levelOrder(TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))), [[3], [9, 20], [15, 7]])
        bst = s.sortedArrayToBST([-10, -3, 0, 5, 9])
        self.assertTrue(s.isValidBST(bst))
        self.assertEqual(s.kthSmallest(TreeNode(3, TreeNode(1, None, TreeNode(2)), TreeNode(4)), 1), 1)
        self.assertEqual(s.rightSideView(TreeNode(1, TreeNode(2, None, TreeNode(5)), TreeNode(3, None, TreeNode(4)))), [1, 3, 4])
        flat = TreeNode(1, TreeNode(2, TreeNode(3), TreeNode(4)), TreeNode(5, None, TreeNode(6)))
        s.flatten(flat)
        vals = []
        while flat:
            vals.append(flat.val)
            self.assertIsNone(flat.left)
            flat = flat.right
        self.assertEqual(vals, [1, 2, 3, 4, 5, 6])
        bt = s.buildTree([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])
        self.assertEqual(bt.val, 3)
        self.assertEqual(s.pathSum(TreeNode(10, TreeNode(5, TreeNode(3, TreeNode(3), TreeNode(-2)), TreeNode(2, None, TreeNode(1))), TreeNode(-3, None, TreeNode(11))), 8), 3)
        lca_root = TreeNode(3)
        lca_root.left = TreeNode(5)
        lca_root.right = TreeNode(1)
        self.assertEqual(s.lowestCommonAncestor(lca_root, lca_root.left, lca_root.right).val, 3)
        self.assertEqual(s.maxPathSum(TreeNode(-10, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))), 42)

        self.assertEqual(s.numIslands([list("11110"), list("11010"), list("11000"), list("00000")]), 1)
        self.assertEqual(s.orangesRotting([[2, 1, 1], [1, 1, 0], [0, 1, 1]]), 4)
        self.assertTrue(s.canFinish(2, [[1, 0]]))
        tr = Trie()
        tr.insert("apple")
        self.assertTrue(tr.search("apple"))
        self.assertTrue(tr.startsWith("app"))
        self.assertFalse(tr.search("app"))

        self.assertEqual(sorted(s.permute([1, 2, 3])), sorted([[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]))
        self.assertEqual(sorted(s.subsets([1, 2])), sorted([[], [1], [2], [1, 2]]))
        self.assertEqual(sorted(s.letterCombinations("23")), sorted(["ad", "ae", "af", "bd", "be", "bf", "cd", "ce", "cf"]))
        self.assertEqual(sorted(s.combinationSum([2, 3, 6, 7], 7)), sorted([[2, 2, 3], [7]]))
        self.assertEqual(sorted(s.generateParenthesis(3)), sorted(["((()))", "(()())", "(())()", "()(())", "()()()"]))
        self.assertTrue(s.exist([["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "ABCCED"))
        self.assertEqual(sorted(s.partition("aab")), sorted([["a", "a", "b"], ["aa", "b"]]))
        self.assertEqual(len(s.solveNQueens(4)), 2)

        self.assertEqual(s.searchInsert([1, 3, 5, 6], 5), 2)
        self.assertTrue(s.searchMatrix([[1, 3, 5], [7, 9, 11]], 9))
        self.assertEqual(s.searchRange([5, 7, 7, 8, 8, 10], 8), [3, 4])
        self.assertEqual(s.search([4, 5, 6, 7, 0, 1, 2], 0), 4)
        self.assertEqual(s.findMin([3, 4, 5, 1, 2]), 1)
        self.assertEqual(s.findMedianSortedArrays([1, 3], [2]), 2.0)

        self.assertTrue(s.isValid("()[]{}"))
        ms = MinStack()
        ms.push(-2)
        ms.push(0)
        ms.push(-3)
        self.assertEqual(ms.getMin(), -3)
        ms.pop()
        self.assertEqual(ms.top(), 0)
        self.assertEqual(ms.getMin(), -2)
        self.assertEqual(s.decodeString("3[a2[c]]"), "accaccacc")
        self.assertEqual(s.dailyTemperatures([73, 74, 75, 71, 69, 72, 76, 73]), [1, 1, 4, 2, 1, 1, 0, 0])
        self.assertEqual(s.largestRectangleArea([2, 1, 5, 6, 2, 3]), 10)

        self.assertEqual(s.findKthLargest([3, 2, 1, 5, 6, 4], 2), 5)
        self.assertEqual(set(s.topKFrequent([1, 1, 1, 2, 2, 3], 2)), {1, 2})
        mf = MedianFinder()
        mf.addNum(1)
        mf.addNum(2)
        self.assertEqual(mf.findMedian(), 1.5)
        mf.addNum(3)
        self.assertEqual(mf.findMedian(), 2.0)

        self.assertEqual(s.maxProfit([7, 1, 5, 3, 6, 4]), 5)
        self.assertTrue(s.canJump([2, 3, 1, 1, 4]))
        self.assertEqual(s.jump([2, 3, 1, 1, 4]), 2)
        self.assertEqual(s.partitionLabels("ababcbacadefegdehijhklij"), [9, 7, 8])

        self.assertEqual(s.climbStairs(3), 3)
        self.assertEqual(s.generate(5)[-1], [1, 4, 6, 4, 1])
        self.assertEqual(s.rob([2, 7, 9, 3, 1]), 12)
        self.assertEqual(s.numSquares(12), 3)
        self.assertEqual(s.coinChange([1, 2, 5], 11), 3)
        self.assertTrue(s.wordBreak("leetcode", ["leet", "code"]))
        self.assertEqual(s.lengthOfLIS([10, 9, 2, 5, 3, 7, 101, 18]), 4)
        self.assertEqual(s.maxProduct([2, 3, -2, 4]), 6)
        self.assertTrue(s.canPartition([1, 5, 11, 5]))
        self.assertEqual(s.longestValidParentheses(")()())"), 4)

        self.assertEqual(s.uniquePaths(3, 7), 28)
        self.assertEqual(s.minPathSum([[1, 3, 1], [1, 5, 1], [4, 2, 1]]), 7)
        self.assertIn(s.longestPalindrome("babad"), ("bab", "aba"))
        self.assertEqual(s.longestCommonSubsequence("abcde", "ace"), 3)
        self.assertEqual(s.minDistance("horse", "ros"), 3)

        self.assertEqual(s.singleNumber([4, 1, 2, 1, 2]), 4)
        self.assertEqual(s.majorityElement([2, 2, 1, 1, 1, 2, 2]), 2)
        arr = [2, 0, 2, 1, 1, 0]
        s.sortColors(arr)
        self.assertEqual(arr, [0, 0, 1, 1, 2, 2])
        arr = [1, 2, 3]
        s.nextPermutation(arr)
        self.assertEqual(arr, [1, 3, 2])
        self.assertEqual(s.findDuplicate([1, 3, 4, 2, 2]), 2)

        lru = LRUCache(2)
        lru.put(1, 1)
        lru.put(2, 2)
        self.assertEqual(lru.get(1), 1)
        lru.put(3, 3)
        self.assertEqual(lru.get(2), -1)

    def test_branch_coverage_boost(self):
        s = Solution()
        self.assertEqual(s.twoSum([1, 2, 3], 100), [])
        self.assertEqual(s.threeSum([1, 2, -2, -1]), [])
        self.assertEqual(s.findAnagrams("ab", "abc"), [])
        self.assertEqual(s.merge([[1, 4], [4, 5]]), [[1, 5]])
        self.assertEqual(s.findMin([1, 2, 3, 4]), 1)
        self.assertFalse(s.searchMatrixII([], 1))
        self.assertFalse(s.searchMatrixII([[]], 1))
        self.assertFalse(s.searchMatrix([[1, 3, 5], [7, 9, 11]], 8))
        self.assertEqual(s.searchRange([1, 2, 3], 4), [-1, -1])
        self.assertEqual(s.search([4, 5, 6, 7, 0, 1, 2], 3), -1)
        self.assertEqual(s.findMedianSortedArrays([1, 2], [3, 4]), 2.5)
        self.assertFalse(s.isValid("([)]"))
        self.assertEqual(s.decodeString("abc3[cd]xyz"), "abccdcdcdxyz")
        self.assertFalse(s.canJump([3, 2, 1, 0, 4]))
        self.assertEqual(s.letterCombinations(""), [])
        self.assertEqual(s.longestValidParentheses(""), 0)
        self.assertEqual(s.longestValidParentheses("(()"), 2)
        arr = [3, 2, 1]
        s.nextPermutation(arr)
        self.assertEqual(arr, [1, 2, 3])
        m = [[0, 1], [1, 1]]
        s.setZeroes(m)
        self.assertEqual(m, [[0, 0], [0, 1]])
        self.assertFalse(s.hasCycle(build_list([1, 2, 3])))
        self.assertIsNone(s.detectCycle(build_list([1, 2, 3])))
        self.assertFalse(s.isSymmetric(TreeNode(1, TreeNode(2), TreeNode(3))))
        self.assertFalse(s.isValidBST(TreeNode(5, TreeNode(1), TreeNode(4, TreeNode(3), TreeNode(6)))))
        self.assertIsNone(s.lowestCommonAncestor(TreeNode(1), TreeNode(2), TreeNode(3)))
        self.assertEqual(s.maxArea([1, 1]), 1)
        self.assertEqual(s.numIslands([list("000"), list("000")]), 0)
        self.assertEqual(s.numIslands([]), 0)
        self.assertEqual(s.rightSideView(None), [])
        self.assertEqual(s.levelOrder(None), [])
        self.assertIsNone(s.copyRandomList(None))
        self.assertEqual(s.kthSmallest(TreeNode(1, None, TreeNode(2)), 2), 2)
        self.assertFalse(s.exist([["A", "B"], ["C", "D"]], "ABCD"))
        self.assertEqual(s.longestPalindrome("cbbd"), "bb")
        self.assertFalse(s.canPartition([1, 2, 5]))
        self.assertEqual(s.search([6, 7, 0, 1, 2, 4, 5], 4), 5)
        self.assertEqual(s.search([6, 7, 0, 1, 2, 4, 5], 8), -1)
        self.assertTrue(s.searchMatrix([[1]], 1))
        self.assertEqual(s.searchRange([2, 2, 2], 2), [0, 2])
        arr = [1, 5, 1]
        s.nextPermutation(arr)
        self.assertEqual(arr, [5, 1, 1])

        tr = Trie()
        tr.insert("app")
        self.assertFalse(tr.search("apple"))
        self.assertFalse(tr.startsWith("b"))

        lru = LRUCache(1)
        lru.put(1, 1)
        lru.put(1, 2)
        self.assertEqual(lru.get(1), 2)


if __name__ == "__main__":
    unittest.main()
