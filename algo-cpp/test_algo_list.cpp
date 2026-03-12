/**
 * mergeKLists / mergeTwoLists 单元测试
 */
#include "algo_list.hpp"
#include <gtest/gtest.h>
#include <vector>
#include <cstddef>

namespace {

// 用数组创建链表，调用方负责后续释放
ListNode* makeList(const std::vector<int>& vals) {
    if (vals.empty()) return nullptr;
    ListNode* head = new ListNode(vals[0]);
    ListNode* cur = head;
    for (size_t i = 1; i < vals.size(); ++i) {
        cur->next = new ListNode(vals[i]);
        cur = cur->next;
    }
    return head;
}

// 将链表转成数组便于比较
std::vector<int> listToVec(ListNode* head) {
    std::vector<int> out;
    for (; head; head = head->next) out.push_back(head->val);
    return out;
}

// 释放整条链表
void freeList(ListNode* head) {
    while (head) {
        ListNode* next = head->next;
        delete head;
        head = next;
    }
}

// 仅清空 vector；节点已并入 mergeKLists 的返回值，由 freeList(out) 统一释放
void clearLists(std::vector<ListNode*>& lists) {
    lists.clear();
}

} // namespace

TEST(MergeTwoLists, EmptyLeft) {
    ListNode* b = makeList({1, 2, 3});
    ListNode* out = mergeTwoLists(nullptr, b);
    EXPECT_EQ(listToVec(out), std::vector<int>({1, 2, 3}));
    freeList(out);
}

TEST(MergeTwoLists, EmptyRight) {
    ListNode* a = makeList({1, 2, 3});
    ListNode* out = mergeTwoLists(a, nullptr);
    EXPECT_EQ(listToVec(out), std::vector<int>({1, 2, 3}));
    freeList(out);
}

TEST(MergeTwoLists, BothEmpty) {
    ListNode* out = mergeTwoLists(nullptr, nullptr);
    EXPECT_TRUE(out == nullptr);
}

TEST(MergeTwoLists, TwoNonEmpty) {
    ListNode* a = makeList({1, 3, 5});
    ListNode* b = makeList({2, 4, 6});
    ListNode* out = mergeTwoLists(a, b);
    EXPECT_EQ(listToVec(out), std::vector<int>({1, 2, 3, 4, 5, 6}));
    freeList(out);
}

TEST(MergeTwoLists, OneLonger) {
    ListNode* a = makeList({1, 2});
    ListNode* b = makeList({3, 4, 5, 6});
    ListNode* out = mergeTwoLists(a, b);
    EXPECT_EQ(listToVec(out), std::vector<int>({1, 2, 3, 4, 5, 6}));
    freeList(out);
}

TEST(MergeKLists, EmptyInput) {
    std::vector<ListNode*> lists;
    ListNode* out = mergeKLists(lists);
    EXPECT_EQ(out, nullptr);
}

TEST(MergeKLists, SingleList) {
    std::vector<ListNode*> lists = { makeList({1, 2, 3}) };
    ListNode* out = mergeKLists(lists);
    EXPECT_EQ(listToVec(out), std::vector<int>({1, 2, 3}));
    freeList(out);
    clearLists(lists);
}

TEST(MergeKLists, SingleEmptyList) {
    std::vector<ListNode*> lists = { nullptr };
    ListNode* out = mergeKLists(lists);
    EXPECT_EQ(out, nullptr);
}

TEST(MergeKLists, TwoLists) {
    std::vector<ListNode*> lists = {
        makeList({1, 4, 7}),
        makeList({2, 5, 8})
    };
    ListNode* out = mergeKLists(lists);
    EXPECT_EQ(listToVec(out), std::vector<int>({1, 2, 4, 5, 7, 8}));
    freeList(out);
    clearLists(lists);
}

TEST(MergeKLists, ThreeLists) {
    std::vector<ListNode*> lists = {
        makeList({1, 4}),
        makeList({2, 5}),
        makeList({3, 6})
    };
    ListNode* out = mergeKLists(lists);
    EXPECT_EQ(listToVec(out), std::vector<int>({1, 2, 3, 4, 5, 6}));
    freeList(out);
    clearLists(lists);
}

TEST(MergeKLists, KLists_AllSameLength) {
    std::vector<ListNode*> lists = {
        makeList({1, 5, 9}),
        makeList({2, 6, 10}),
        makeList({3, 7, 11}),
        makeList({4, 8, 12})
    };
    ListNode* out = mergeKLists(lists);
    EXPECT_EQ(listToVec(out), std::vector<int>({1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}));
    freeList(out);
    clearLists(lists);
}

TEST(MergeKLists, WithEmptySublist) {
    std::vector<ListNode*> lists = {
        makeList({1, 3}),
        nullptr,
        makeList({2, 4})
    };
    ListNode* out = mergeKLists(lists);
    EXPECT_EQ(listToVec(out), std::vector<int>({1, 2, 3, 4}));
    freeList(out);
    clearLists(lists);
}

TEST(MergeKLists, SingleElementLists) {
    std::vector<ListNode*> lists = {
        makeList({3}),
        makeList({1}),
        makeList({2})
    };
    ListNode* out = mergeKLists(lists);
    EXPECT_EQ(listToVec(out), std::vector<int>({1, 2, 3}));
    freeList(out);
    clearLists(lists);
}
