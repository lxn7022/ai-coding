#include "algo_list.hpp"

// 合并两个有序链表
ListNode* mergeTwoLists(ListNode* a, ListNode* b) {
    if (!a) return b;
    if (!b) return a;
    if (a->val < b->val) {
        a->next = mergeTwoLists(a->next, b);
        return a;
    }
    b->next = mergeTwoLists(a, b->next);
    return b;
}

// 分治：合并 lists[left..right]
ListNode* mergeLists(std::vector<ListNode*>& lists, int left, int right) {
    if (left > right) return nullptr;
    if (left == right) return lists[left];
    int mid = left + (right - left) / 2;
    ListNode* l = mergeLists(lists, left, mid);
    ListNode* r = mergeLists(lists, mid + 1, right);
    return mergeTwoLists(l, r);
}

ListNode* mergeKLists(std::vector<ListNode*>& lists) {
    if (lists.empty()) return nullptr;
    return mergeLists(lists, 0, static_cast<int>(lists.size()) - 1);
}
