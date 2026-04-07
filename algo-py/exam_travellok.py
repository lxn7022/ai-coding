

PRD = """
Twitter寻找整数
你得到一个存储在数组 arr中的从 1 到 n 的整数的排列，以及一个整数 k。数组的第 i 大元素是指将该数组按降序排序后的第 i 个元素。
对于数组的每个长度为 i 的前缀（其中 i 的范围是从 k 到 n），找到第 k 大的元素。
示例
n = 4
k = 2
arr = [4, 2, 1, 3]
找到每个长度 ≥ k 的前缀的第 2 大元素：
i = 2，arr = [4, 2] → 第 2 大的元素是 2
i = 3，arr = [4, 2, 1] → 第 2 大的元素是 2
i = 4，arr = [4, 2, 1, 3] → 第 2 大的元素是 3
返回数组 [2, 2, 3]。
函数描述
在编辑器中完成函数 getGreatestElements，参数如下：
int arr[n]：一个包含 n 个整数的排列
int k：要找到的元素的排名（第 k 大）
返回值
int[n - k + 1]：对应每个 i（范围在 [k, n]）的前缀的第 k 大元素的结果数组。
约束条件
1 ≤ n ≤ 2×10⁵
1 ≤ arr[i] ≤ n
1 ≤ k ≤ n

"""

def getGreatestElements(arr: list[int], k: int) -> list[int]:
    """
    对每个前缀 arr[:i] (i 从 k 到 n)，返回该前缀的第 k 大元素。

    思路：维护一个大小最多为 k 的最小堆，保存当前前缀中的“前 k 大”元素；
    当堆大小为 k 时，堆顶即第 k 大。

    复杂度：O(n log k)，空间 O(k)
    """
    import heapq

    n = len(arr)
    if k < 1 or k > n:
        return []

    heap: list[int] = []
    ans: list[int] = []
    for i, x in enumerate(arr, start=1):
        heapq.heappush(heap, x)
        if len(heap) > k:
            heapq.heappop(heap)
        if i >= k:
            ans.append(heap[0])
    return ans
