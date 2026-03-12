// 二叉树相关算法声明
#ifndef ALGO_TREE_HPP
#define ALGO_TREE_HPP

#include <vector>

struct TreeNode {
    int val;
    TreeNode* left;
    TreeNode* right;
    TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
};

std::vector<int> pre_order(TreeNode* root);
std::vector<int> in_order(TreeNode* root);
std::vector<int> post_order(TreeNode* root);
std::vector<int> level_order(TreeNode* root);
int max_depth(TreeNode* root);
std::vector<int> max_depth_path(TreeNode* root);
int num_nodes(TreeNode* root);
int num_leaves(TreeNode* root);
bool is_valid_BST(TreeNode* root);
TreeNode* sorted_list_to_BST(std::vector<int> nums);
std::vector<int> BST_to_sorted_list(TreeNode* root);
void print_tree(TreeNode* root);

#endif
