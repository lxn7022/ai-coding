/**
 * algo_tree 单元测试
 */
#include "algo_tree.hpp"
#include <gtest/gtest.h>
#include <vector>
#include <cstddef>
#include <cstdio>

namespace {

// 按层序数组建树：-1 表示 nullptr，用于完全二叉树形状
TreeNode* build_tree(const std::vector<int>& vals) {
    if (vals.empty() || vals[0] == -1) return nullptr;
    std::vector<TreeNode*> nodes(vals.size(), nullptr);
    for (size_t i = 0; i < vals.size(); ++i) {
        if (vals[i] == -1) continue;
        nodes[i] = new TreeNode(vals[i]);
        if (i > 0) {
            size_t p = (i - 1) / 2;
            if (nodes[p]) (i % 2 ? nodes[p]->left : nodes[p]->right) = nodes[i];
        }
    }
    return nodes.empty() ? nullptr : nodes[0];
}

// 释放整棵树
void free_tree(TreeNode* root) {
    if (!root) return;
    free_tree(root->left);
    free_tree(root->right);
    delete root;
}

}  // namespace

class AlgoTreeTest : public ::testing::Test {
protected:
    void TearDown() override {
        if (root_) free_tree(root_);
        root_ = nullptr;
    }
    TreeNode* root_ = nullptr;
};

TEST_F(AlgoTreeTest, PreOrder_Empty) {
    EXPECT_EQ(pre_order(nullptr), std::vector<int>{});
}

TEST_F(AlgoTreeTest, PreOrder_Single) {
    root_ = build_tree({1});
    EXPECT_EQ(pre_order(root_), std::vector<int>({1}));
}

TEST_F(AlgoTreeTest, PreOrder_Linear) {
    root_ = build_tree({1, 2, -1, 3});  // 1->2->3
    EXPECT_EQ(pre_order(root_), std::vector<int>({1, 2, 3}));
}

TEST_F(AlgoTreeTest, PreOrder_Full) {
    root_ = build_tree({1, 2, 3, 4, 5, 6, 7});
    EXPECT_EQ(pre_order(root_), std::vector<int>({1, 2, 4, 5, 3, 6, 7}));
}

TEST_F(AlgoTreeTest, InOrder_Empty) {
    EXPECT_EQ(in_order(nullptr), std::vector<int>{});
}

TEST_F(AlgoTreeTest, InOrder_Full) {
    root_ = build_tree({1, 2, 3, 4, 5, 6, 7});
    EXPECT_EQ(in_order(root_), std::vector<int>({4, 2, 5, 1, 6, 3, 7}));
}

TEST_F(AlgoTreeTest, PostOrder_Empty) {
    EXPECT_EQ(post_order(nullptr), std::vector<int>{});
}

TEST_F(AlgoTreeTest, PostOrder_Full) {
    root_ = build_tree({1, 2, 3, 4, 5, 6, 7});
    EXPECT_EQ(post_order(root_), std::vector<int>({4, 5, 2, 6, 7, 3, 1}));
}

TEST_F(AlgoTreeTest, LevelOrder_Empty) {
    EXPECT_EQ(level_order(nullptr), std::vector<int>{});
}

TEST_F(AlgoTreeTest, LevelOrder_Full) {
    root_ = build_tree({1, 2, 3, 4, 5, 6, 7});
    EXPECT_EQ(level_order(root_), std::vector<int>({1, 2, 3, 4, 5, 6, 7}));
}

TEST_F(AlgoTreeTest, MaxDepth_Empty) {
    EXPECT_EQ(max_depth(nullptr), 0);
}

TEST_F(AlgoTreeTest, MaxDepth_Single) {
    root_ = build_tree({1});
    EXPECT_EQ(max_depth(root_), 1);
}

TEST_F(AlgoTreeTest, MaxDepth_ThreeLevels) {
    root_ = build_tree({1, 2, 3, 4, 5, 6, 7});
    EXPECT_EQ(max_depth(root_), 3);
}

TEST_F(AlgoTreeTest, NumNodes_Empty) {
    EXPECT_EQ(num_nodes(nullptr), 0);
}

TEST_F(AlgoTreeTest, NumNodes_Full) {
    root_ = build_tree({1, 2, 3, 4, 5, 6, 7});
    EXPECT_EQ(num_nodes(root_), 7);
}

TEST_F(AlgoTreeTest, NumLeaves_Empty) {
    EXPECT_EQ(num_leaves(nullptr), 0);
}

TEST_F(AlgoTreeTest, NumLeaves_Single) {
    root_ = build_tree({1});
    EXPECT_EQ(num_leaves(root_), 1);
}

TEST_F(AlgoTreeTest, NumLeaves_Full) {
    root_ = build_tree({1, 2, 3, 4, 5, 6, 7});
    EXPECT_EQ(num_leaves(root_), 4);
}

TEST_F(AlgoTreeTest, SortedListToBST_Empty) {
    TreeNode* r = sorted_list_to_BST({});
    EXPECT_EQ(r, nullptr);
}

TEST_F(AlgoTreeTest, SortedListToBST_One) {
    root_ = sorted_list_to_BST({1});
    ASSERT_NE(root_, nullptr);
    EXPECT_EQ(root_->val, 1);
    EXPECT_EQ(in_order(root_), std::vector<int>({1}));
}

TEST_F(AlgoTreeTest, SortedListToBST_Three) {
    root_ = sorted_list_to_BST({1, 2, 3});
    ASSERT_NE(root_, nullptr);
    EXPECT_EQ(in_order(root_), std::vector<int>({1, 2, 3}));
}

TEST_F(AlgoTreeTest, BSTToSortedList_Empty) {
    EXPECT_EQ(BST_to_sorted_list(nullptr), std::vector<int>{});
}

TEST_F(AlgoTreeTest, BSTToSortedList_RoundTrip) {
    root_ = sorted_list_to_BST({1, 2, 3, 4, 5});
    EXPECT_EQ(BST_to_sorted_list(root_), std::vector<int>({1, 2, 3, 4, 5}));
}

TEST_F(AlgoTreeTest, PrintTree_Empty) {
    testing::internal::CaptureStdout();
    print_tree(nullptr);
    std::string out = testing::internal::GetCapturedStdout();
    printf("[PrintTree_Empty]\n%s", out.c_str());
    EXPECT_TRUE(out.empty());
}

TEST_F(AlgoTreeTest, PrintTree_SingleNode) {
    root_ = build_tree({1});
    testing::internal::CaptureStdout();
    print_tree(root_);
    std::string out = testing::internal::GetCapturedStdout();
    printf("[PrintTree_SingleNode]\n%s", out.c_str());
    EXPECT_TRUE(out.find('1') != std::string::npos);
}

TEST_F(AlgoTreeTest, PrintTree_TwoLevels) {
    root_ = build_tree({1, 2, 3});
    testing::internal::CaptureStdout();
    print_tree(root_);
    std::string out = testing::internal::GetCapturedStdout();
    printf("[PrintTree_TwoLevels]\n%s", out.c_str());
    EXPECT_TRUE(out.find('1') != std::string::npos);
    EXPECT_TRUE(out.find('2') != std::string::npos);
    EXPECT_TRUE(out.find('3') != std::string::npos);
    EXPECT_TRUE(out.find('/') != std::string::npos);
    EXPECT_TRUE(out.find('\\') != std::string::npos);
}

TEST_F(AlgoTreeTest, PrintTree_ThreeLevels) {
    root_ = build_tree({1, 2, 3, 4, 5, 6, 7});
    testing::internal::CaptureStdout();
    print_tree(root_);
    std::string out = testing::internal::GetCapturedStdout();
    printf("[PrintTree_ThreeLevels]\n%s", out.c_str());
    for (int v = 1; v <= 7; ++v)
        EXPECT_TRUE(out.find(static_cast<char>('0' + v)) != std::string::npos) << "missing node " << v;
    EXPECT_GT(out.size(), 0u);
}



