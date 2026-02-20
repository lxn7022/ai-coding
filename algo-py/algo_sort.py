"""常用排序算法：冒泡、选择、插入、归并、快速排序。"""

def bubble_sort(arr: list[int]) -> list[int]:
    """写一个冒泡排序算法"""
    for i in range(len(arr)):
        for j in range(len(arr) - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

def selection_sort(arr: list[int]) -> list[int]:
    """写一个选择排序算法"""
    for i, _ in enumerate(arr):
        min_index = i
        for j in range(i + 1, len(arr)):
            if arr[j] < arr[min_index]:
                min_index = j
        arr[i], arr[min_index] = arr[min_index], arr[i]
    return arr

def insertion_sort(arr: list[int]) -> list[int]:
    """写一个插入排序算法"""
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j] 
            j -= 1
        arr[j + 1] = key
    return arr

def merge_sort(arr: list[int]) -> list[int]:
    """写一个归并排序算法"""
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left: list[int], right: list[int]) -> list[int]:
    """写一个合并两个有序列表的算法"""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def quick_sort(arr: list[int]) -> list[int]:
    """写一个快速排序算法
    Args:
        arr (list[int]): _description_

    Returns:
        list[int]: _description_
    """
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

if __name__ == "__main__":
    arr_test = [3, 6, 8, 10, 1, 2, 1]
    sort_funcs = [
        ("bubble_sort", bubble_sort),
        ("selection_sort", selection_sort),
        ("insertion_sort", insertion_sort),
        ("merge_sort", merge_sort),
        ("quick_sort", quick_sort),
    ]
    for name, func in sort_funcs:
        result = func(arr_test.copy())
        print(f"{name}: {result}")
