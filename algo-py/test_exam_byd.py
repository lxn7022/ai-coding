"""exam_byd.py 的单元测试。"""
from exam_byd import min_eating_speed


class TestMinEatingSpeed:
    """min_eating_speed 函数测试类。"""

    def test_example_1(self):
        """经典用例：piles=[3,6,7,11], h=8 -> k=4。"""
        assert min_eating_speed([3, 6, 7, 11], 8) == 4

    def test_example_2(self):
        """h=5 时必须速度至少为最大堆。"""
        assert min_eating_speed([30, 11, 23, 4, 20], 5) == 30

    def test_example_3(self):
        """h=6 时最小速度为 23。"""
        assert min_eating_speed([30, 11, 23, 4, 20], 6) == 23

    def test_empty_piles(self):
        """空列表返回 0。"""
        assert min_eating_speed([], 8) == 0

    def test_single_pile_one_hour(self):
        """单堆且 h=1，速度必须等于该堆数量。"""
        assert min_eating_speed([10], 1) == 10

    def test_single_pile_two_hours(self):
        """单堆 h=2，最小速度为 ceil(堆/2)。"""
        assert min_eating_speed([5], 2) == 3

    def test_exactly_one_hour_per_pile(self):
        """h 等于堆数时，最小速度为 max(piles)。"""
        assert min_eating_speed([1, 2, 3, 4, 5], 5) == 5

    def test_large_h_implies_small_k(self):
        """h 很大时最小速度可为 1。"""
        assert min_eating_speed([1, 1, 1, 1], 10) == 1

    def test_two_piles(self):
        """两堆：[4, 8], h=4 -> k=4 即可 (1+2=3 小时)。"""
        assert min_eating_speed([4, 8], 4) == 4
