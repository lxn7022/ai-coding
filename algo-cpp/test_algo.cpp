#include "algo_tree.hpp"
#include <cstdio>
#include <vector>
#include <numeric>
#include <random>
#include <algorithm>
#ifdef _WIN32
#include <windows.h>
#endif

static void free_tree(TreeNode* root) {
    if (!root) return;
    free_tree(root->left);
    free_tree(root->right);
    delete root;
}

// BST 插入：递归插入到空位
static void bst_insert(TreeNode*& root, int val) {
    if (!root) {
        root = new TreeNode(val);
        return;
    }
    if (val < root->val)
        bst_insert(root->left, val);
    else
        bst_insert(root->right, val);
}


void test_print_tree(int n) {
    if (n <= 0) return;

    // 随机 n 个整数（取值范围 10–1000）
    std::random_device rd;
    std::mt19937 g(rd());
    std::uniform_int_distribution<int> dist(10, 1000);
    std::vector<int> vals;
    vals.reserve(static_cast<size_t>(n));
    for (int i = 0; i < n; ++i) {
        vals.push_back(dist(g));
    }
    std::sort(vals.begin(), vals.end());

    // 用有序序列构建平衡二叉搜索树
    TreeNode* root = sorted_list_to_BST(vals);

    // 打印并释放
    print_tree(root);
    free_tree(root);
}


int main(int argc, char** argv) {
    (void)argc;
    (void)argv;

#ifdef _WIN32
    SetConsoleOutputCP(65001);
    SetConsoleCP(65001);
#endif

    test_print_tree(20);

    return 0;
}


