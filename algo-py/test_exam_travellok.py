"""exam_travellok 模块的单测：前缀第 k 大元素。"""

import random

import pytest

from exam_travellok import getGreatestElements


def brute_kth_largest_prefix(arr: list[int], k: int) -> list[int]:
    """小规模暴力：对每个前缀排序取第 k 大。"""
    out: list[int] = []
    for i in range(k, len(arr) + 1):
        prefix = sorted(arr[:i], reverse=True)
        out.append(prefix[k - 1])
    return out


class TestGetGreatestElements:
    def test_example(self):
        assert getGreatestElements([4, 2, 1, 3], 2) == [2, 2, 3]

    def test_ascending_permutation(self):
        # arr = [1..n] 时，前缀 [1..i] 的第 k 大为 i-k+1
        n = 10
        arr = list(range(1, n + 1))
        k = 3
        assert getGreatestElements(arr, k) == [i - k + 1 for i in range(k, n + 1)]

    def test_descending_permutation(self):
        # arr = [n..1] 时，随着前缀变长，只会追加更小值，第 k 大恒定不变
        n = 12
        arr = list(range(n, 0, -1))
        k = 5
        assert getGreatestElements(arr, k) == [n - k + 1] * (n - k + 1)

    def test_k_equals_1_is_prefix_max(self):
        arr = [4, 2, 1, 3]
        assert getGreatestElements(arr, 1) == [4, 4, 4, 4]

    def test_k_equals_n_is_min_of_whole_array(self):
        arr = [4, 2, 1, 3]
        assert getGreatestElements(arr, len(arr)) == [1]

    @pytest.mark.parametrize(
        "arr,k",
        [
            ([1], 1),
            ([2, 1], 1),
            ([2, 1], 2),
            ([3, 1, 2], 2),
            ([5, 1, 4, 2, 3], 3),
        ],
    )
    def test_matches_bruteforce_small(self, arr, k):
        assert getGreatestElements(arr, k) == brute_kth_largest_prefix(arr, k)

    def test_random_permutations_against_bruteforce(self):
        rnd = random.Random(20260318)
        for n in range(2, 60):
            base = list(range(1, n + 1))
            # 同一个 n 多做几次 shuffle，扩大覆盖
            for _ in range(5):
                arr = base[:]
                rnd.shuffle(arr)
                # 同一个排列上多测几个 k
                for k in {1, n, rnd.randint(1, n), rnd.randint(1, n)}:
                    assert getGreatestElements(arr, k) == brute_kth_largest_prefix(arr, k)

    def test_monotonicity_over_prefixes(self):
        # 性质：随着前缀变长，第 k 大元素不应变小（单调不减）
        rnd = random.Random(20260318)
        n = 5000
        arr = list(range(1, n + 1))
        rnd.shuffle(arr)
        k = 200
        out = getGreatestElements(arr, k)
        assert len(out) == n - k + 1
        assert all(out[i] <= out[i + 1] for i in range(len(out) - 1))

    def test_rank_condition_each_prefix(self):
        # 对每个前缀 i，返回值 x 应满足：
        # - 前缀中严格大于 x 的元素数量 < k
        # - 前缀中大于等于 x 的元素数量 >= k
        rnd = random.Random(20260318)
        n = 200
        arr = list(range(1, n + 1))
        rnd.shuffle(arr)
        k = 37
        out = getGreatestElements(arr, k)
        for idx, x in enumerate(out, start=k):
            prefix = arr[:idx]
            gt = sum(1 for v in prefix if v > x)
            ge = sum(1 for v in prefix if v >= x)
            assert gt < k
            assert ge >= k

    def test_invalid_k_returns_empty(self):
        assert getGreatestElements([1, 2, 3], 0) == []
        assert getGreatestElements([1, 2, 3], 4) == []
