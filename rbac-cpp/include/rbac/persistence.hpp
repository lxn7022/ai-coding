#pragma once

#include "rbac/rbac_engine.hpp"
#include <string>

namespace rbac {

/// 简单文件持久化：将引擎状态保存/从文件加载（纯文本格式，便于调试）
class Persistence {
public:
    /// 保存到文件。格式：每行一条记录，以空格分隔的键值。
    static bool save(const RbacEngine& engine, const std::string& filepath);
    /// 从文件加载，会清空并覆盖当前引擎内容。
    static bool load(RbacEngine& engine, const std::string& filepath);
};

}  // namespace rbac
