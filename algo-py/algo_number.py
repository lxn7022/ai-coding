def Sum(nums: list[int], target: int) -> tuple[int, int] | None:
    """
    两数之和：在数组 nums 中找出和为 target 的两个数的下标。

    Args:
        nums: 整数列表
        target: 目标和

    Returns:
        若存在则返回 (i, j)，满足 nums[i] + nums[j] == target；否则返回 None
    """
    nums_len = len(nums)

    for i in range(nums_len-1) :
        for j in range(i+1, nums_len):
            result = nums[i] + nums[j]
            if result == target:
                return (i,j)


def Sum2(nums: list[int], target: int) -> tuple[int, int] | None:
    """与 Sum 功能相同，使用哈希表，时间复杂度 O(n)。"""
    seen: dict[int, int] = {}  # 值 -> 下标
    for i, x in enumerate(nums):
        complement = target - x
        if complement in seen:
            return (seen[complement], i)
        seen[x] = i
        
if __name__ == "__main__":
    nums = [2, 7, 11, 15, 22]
    target = 18
    print(Sum(nums, target))
    print(Sum2(nums, target))
    
