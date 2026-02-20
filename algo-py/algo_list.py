from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ListNode:
    """单链表节点：val 为节点值，next 指向下一节点。"""

    val: int
    next: ListNode | None = None


def add_two_number(l1,l2,carry):
    if l1 is None and l2 is None and carry == 0:
        return None
    val1 = l1.val if l1 else 0
    val2 = l2.val if l2 else 0
    total = val1 + val2 + carry
    carry = total // 10
    return ListNode(total % 10, add_two_number(l1.next if l1 else None, l2.next if l2 else None, carry))


def print_list(l: ListNode | None):
    while l:
        print(l.val, end=" -> ")
        l = l.next
    print("None")
    


@dataclass
class ListNode:
    """单链表节点：val 为节点值，next 指向下一节点。"""

    val: int
    next: ListNode | None = None


def merge_k_lists(lists: list[ListNode | None]) -> ListNode | None:
    """合并k个有序链表（分治 + 两两合并）。

    时间复杂度: O(N log k)，N 为所有链表节点总数，k 为链表个数（分治共 log k 层，每层总代价 O(N)）。
    空间复杂度: O(log k)，分治递归栈深度。
    """
    if not lists:
        return None
    return merge_lists(lists, 0, len(lists) - 1)

def merge_lists(lists: list[ListNode | None], left: int, right: int) -> ListNode | None:
    """合并两个有序链表"""
    if left > right:
        return None
    if left == right:
        return lists[left]
    mid = (left + right) // 2
    left_head = merge_lists(lists, left, mid)
    right_head = merge_lists(lists, mid + 1, right)
    return merge_two_lists(left_head, right_head)

def merge_two_lists(list1: ListNode | None, list2: ListNode | None) -> ListNode | None:
    """合并两个有序链表"""
    if list1 is None:
        return list2
    if list2 is None:
        return list1
    if list1.val < list2.val:
        list1.next = merge_two_lists(list1.next, list2)
        return list1
    list2.next = merge_two_lists(list1, list2.next)
    return list2


def merge_k_lists_pythonic(lists: list[ListNode | None]) -> ListNode | None:
    """合并k个有序链表（用 append + sort 实现）。

    时间复杂度: O(N log N)，N 为所有链表节点总数（收集 O(N) + 排序 O(N log N) + 重链 O(N)）。
    空间复杂度: O(N)，用于存放 N 个节点的列表。
    """
    vals: list[ListNode] = []
    for head in lists:
        while head:
            nxt = head.next
            vals.append(head)
            head = nxt
    vals.sort(key=lambda node: node.val)
    dummy = ListNode(0)
    cur = dummy
    for node in vals:
        node.next = None
        cur.next = node
        cur = node
    return dummy.next


def print_list(head: ListNode | None) -> None:
    """按 head -> ... -> None 格式打印链表"""
    while head:
        print(head.val, end=" -> ")
        head = head.next
    print("None")


def _list_from_vals(vals: list[int]) -> ListNode | None:
    """由有序数组构造链表（不修改原数组）"""
    dummy = ListNode(0)
    cur = dummy
    for v in vals:
        cur.next = ListNode(v)
        cur = cur.next
    return dummy.next


def _copy_lists(lists: list[ListNode | None]) -> list[ListNode | None]:
    """深拷贝每条链表，用于压测时保证输入一致、互不干扰"""
    out: list[ListNode | None] = []
    for head in lists:
        dummy = ListNode(0)
        cur = dummy
        while head:
            cur.next = ListNode(head.val)
            cur = cur.next
            head = head.next
        out.append(dummy.next)
    return out


def _benchmark(k: int, n_per_list: int, rounds: int = 5) -> None:
    """压测: k 条链表，每条约 n_per_list 个节点，共 rounds 轮取平均。"""
    import random
    import time
    # 生成 k 条有序链表（每条 n_per_list 个随机数并排序）
    def gen_lists() -> list[ListNode | None]:
        return [
            _list_from_vals(sorted(random.randint(1, 10000) for _ in range(n_per_list)))
            for _ in range(k)
        ]
    base = gen_lists()
    n_total = k * n_per_list

    # merge_k_lists 会修改节点 next，每轮需用拷贝
    times1: list[float] = []
    for _ in range(rounds):
        lists1 = _copy_lists(base)
        t0 = time.perf_counter()
        merge_k_lists(lists1)
        times1.append(time.perf_counter() - t0)
    avg1 = sum(times1) / len(times1)

    times2: list[float] = []
    for _ in range(rounds):
        lists2 = _copy_lists(base)
        t0 = time.perf_counter()
        merge_k_lists_pythonic(lists2)
        times2.append(time.perf_counter() - t0)
    avg2 = sum(times2) / len(times2)

    print(f"k={k}, 每条约{n_per_list}节点, N≈{n_total}, {rounds}轮平均:")
    print(f"  merge_k_lists(分治):     {avg1:.4f}s")
    print(f"  merge_k_lists_pythonic:   {avg2:.4f}s")
    print()

    

if __name__ == "__main__":
    l1 = ListNode(2, ListNode(4, ListNode(3)))
    l2 = ListNode(5, ListNode(6, ListNode(4)))
    result = add_two_number(l1, l2, 0)
    print_list(result)

    lists = [ListNode(1, ListNode(4, ListNode(5))), ListNode(1, ListNode(3, ListNode(4))), ListNode(2, ListNode(6))]
    result = merge_k_lists(lists)
    print_list(result)

    lists2 = [ListNode(1, ListNode(4, ListNode(5))), ListNode(1, ListNode(3, ListNode(4))), ListNode(2, ListNode(6))]
    result2 = merge_k_lists_pythonic(lists2)
    print_list(result2)

    print("\n======== 性能压测 ========")
    # 规模不宜过大，否则 merge_two_lists 递归会超栈
    _benchmark(k=10, n_per_list=40, rounds=5)
    _benchmark(k=20, n_per_list=25, rounds=5)
    _benchmark(k=30, n_per_list=20, rounds=3)    
