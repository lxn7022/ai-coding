// 合并 k 个有序链表
// 时间复杂度：O(N log k)，N 为节点总数，k 为链表个数
// 空间复杂度：O(log k)，分治递归栈深度
// 思路：分治法，将 [left, right] 分成两半递归合并，再合并两个有序链表

#include <vector>

struct ListNode {
    int val;
    ListNode* next;
    ListNode() : val(0), next(nullptr) {}
    ListNode(int x) : val(x), next(nullptr) {}
    ListNode(int x, ListNode* next) : val(x), next(next) {}
};

// 合并两个有序链表
ListNode* mergeTwoLists(ListNode* a, ListNode* b);

// 分治：合并 lists[left..right]
ListNode* mergeLists(std::vector<ListNode*>& lists, int left, int right);

ListNode* mergeKLists(std::vector<ListNode*>& lists);
