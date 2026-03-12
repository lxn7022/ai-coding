//前根遍历二叉树，返回一个列表
#include "algo_tree.hpp"
#include <vector>
#include <queue>
#include <string>
#include <algorithm>
#include <cmath>
#include <cstdio>

namespace {
template <typename T>
std::vector<T> vec_concat(std::vector<T> a, const std::vector<T>& b) {
    a.insert(a.end(), b.begin(), b.end());
    return a;
}
}  // namespace

//前根遍历二叉树，返回一个列表
std::vector<int> pre_order(TreeNode* root) {
    if (root == nullptr) return {};
    std::vector<int> r = {root->val};
    r = vec_concat(r, pre_order(root->left));
    r = vec_concat(r, pre_order(root->right));
    return r;
}

//中根遍历二叉树，返回一个列表
std::vector<int> in_order(TreeNode* root) {
    if (root == nullptr) return {};
    std::vector<int> r = in_order(root->left);
    r.push_back(root->val);
    r = vec_concat(r, in_order(root->right));
    return r;
}

//后根遍历二叉树，返回一个列表
std::vector<int> post_order(TreeNode* root) {
    if (root == nullptr) return {};
    std::vector<int> r = post_order(root->left);
    r = vec_concat(r, post_order(root->right));
    r.push_back(root->val);
    return r;
}

//层序遍历二叉树，返回一个列表
std::vector<int> level_order(TreeNode* root) {
    std::vector<int> result;
    if (root == nullptr) return result;
    std::queue<TreeNode*> q;
    q.push(root);
    while (!q.empty()) {
        TreeNode* node = q.front();
        q.pop();
        result.push_back(node->val);
        if (node->left) q.push(node->left);
        if (node->right) q.push(node->right);
    }
    return result;
}

//返回二叉树的最大深度，即二叉树的层数
int max_depth(TreeNode* root) {
    if (root == nullptr) return 0;
    return std::max(max_depth(root->left), max_depth(root->right)) + 1;
}

//返回二叉树的最大深度分支上的所有节点值（任选一条最深路径）
std::vector<int> max_depth_path(TreeNode* root) {
    if (root == nullptr) return {};
    std::vector<int> r = {root->val};
    r = vec_concat(r, max_depth_path(root->left));
    r = vec_concat(r, max_depth_path(root->right));
    return r;
}

//返回二叉树的节点个数
int num_nodes(TreeNode* root) {
    if (root == nullptr) return 0;
    return num_nodes(root->left) + num_nodes(root->right) + 1;
}

//返回二叉树的叶子节点个数
int num_leaves(TreeNode* root) {
    if (root == nullptr) return 0;
    if (root->left == nullptr && root->right == nullptr) return 1;
    return num_leaves(root->left) + num_leaves(root->right);    

}

//判断二叉树是否为有效的二叉搜索树，即中根遍历的节点值是递增的
bool is_valid_BST(TreeNode* root) {
    if (root == nullptr) return true;
    return is_valid_BST(root->left) && is_valid_BST(root->right);
}

//将有序列表转换为二叉搜索树
TreeNode* sorted_list_to_BST(std::vector<int> nums) {
    if (nums.empty()) return nullptr;
    size_t mid = nums.size() / 2;
    TreeNode* root = new TreeNode(nums[mid]);
    root->left = sorted_list_to_BST(std::vector<int>(nums.begin(), nums.begin() + mid));
    root->right = sorted_list_to_BST(std::vector<int>(nums.begin() + mid + 1, nums.end()));
    return root;
}

//将二叉树转换为有序列表
std::vector<int> BST_to_sorted_list(TreeNode* root) {
    if (root == nullptr) return {};
    std::vector<int> r = BST_to_sorted_list(root->left);
    r.push_back(root->val);
    r = vec_concat(r, BST_to_sorted_list(root->right));
    return r;
}

/*
打印二叉树, 直观显示出根节点与叶子节点之间的关系。输出示例:
           1
         /   \
        2     3
       / \   / \
      4   5 6   7
     / \
    8   9
*/
namespace {
void print_tree_compact(TreeNode* node, const std::string& prefix, bool is_left) {
    if (!node) return;
    printf("%s%s%d\n", prefix.c_str(), is_left ? "L-- " : "R-- ", node->val);
    std::string next = prefix + (is_left ? "|   " : "    ");
    print_tree_compact(node->left, next, true);
    print_tree_compact(node->right, next, false);
}
}  // namespace

void print_tree(TreeNode* root) {
    if (root == nullptr) return;
    int h = max_depth(root);
    const int max_width = 127;  // 超过则用缩进格式，避免控制台一行过长
    if ((1 << h) - 1 > max_width) {
        printf("[Tree too deep, using compact format]\n");
        print_tree_compact(root, "", false);
        return;
    }
    int width = (1 << h) - 1;
    int rows = 2 * h - 1;
    std::vector<std::string> grid(rows, std::string(width, ' '));

    std::queue<std::tuple<TreeNode*, int, int>> q;
    q.push({root, 0, 0});
    std::vector<std::tuple<TreeNode*, int, int>> nodes;
    while (!q.empty()) {
        auto [node, depth, pos] = q.front();
        q.pop();
        nodes.push_back({node, depth, pos});
        if (node->left) q.push({node->left, depth + 1, pos * 2});
        if (node->right) q.push({node->right, depth + 1, pos * 2 + 1});
    }

    auto col_at = [h](int depth, int pos) {
        return (2 * pos + 1) * (1 << (h - 1 - depth)) - 1;
    };

    for (const auto& [node, depth, pos] : nodes) {
        int c = col_at(depth, pos);
        std::string s = std::to_string(node->val);
        int len = static_cast<int>(s.size());
        int start = std::max(0, c - len / 2);
        for (int i = 0; i < len && start + i < width; ++i)
            grid[2 * depth][start + i] = s[i];
    }

    for (const auto& [node, depth, pos] : nodes) {
        if (2 * depth + 1 >= rows) continue;
        int col = col_at(depth, pos);
        if (node->left) {
            int col_left = col_at(depth + 1, pos * 2);
            int slash_pos = (col_left + col) / 2;
            if (slash_pos >= 0 && slash_pos < width)
                grid[2 * depth + 1][slash_pos] = '/';
        }
        if (node->right) {
            int col_right = col_at(depth + 1, pos * 2 + 1);
            int back_pos = (col + col_right) / 2;
            if (back_pos >= 0 && back_pos < width)
                grid[2 * depth + 1][back_pos] = '\\';
        }
    }

    for (const auto& line : grid)
        printf("%s\n", line.c_str());
}
