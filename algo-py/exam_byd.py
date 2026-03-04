

PPD = '''
小红喜欢吃梨子。这里有n堆梨子，第i堆中有piles[i]根梨子。店主已经离开了，将在h小时后回来。
小红可以决定她吃梨子的速度k(单位:根小时)。每个小时，她将会选择一堆梨子，从中吃掉k根。如果这堆梨子少于k根，她将吃掉这堆的所有梨子，然后这一小时内不会再吃更多的梨子。
小红喜欢慢慢吃，但仍然想在店主回来前吃掉所有的梨子。
返回她可以在h小时内吃掉所有梨子的最小速度k(k为整数)
'''


def min_eating_speed(piles: list[int], h: int) -> int:
    """
    返回在 h 小时内吃完所有梨子的最小速度 k（整数）。
    每堆 piles[i] 根梨子，每小时最多吃 k 根（选一堆吃，不足 k 则吃完该堆即停）。
    """
    if not piles:
        return 0
    low, high = 1, max(piles)
    result = high

    def hours_needed(k: int) -> int:
        """速度为 k 时吃完所有堆所需总小时数。"""
        return sum((p + k - 1) // k for p in piles)

    while low <= high:
        mid = (low + high) // 2
        if hours_needed(mid) <= h:
            result = mid
            high = mid - 1
        else:
            low = mid + 1
    return result



    
print(min_eating_speed([3, 6, 7, 11], 8))   
