#include "rbac/persistence.hpp"
#include <fstream>
#include <sstream>

namespace rbac {

namespace {

const char kSep = '\t';

std::string escape(const std::string& s) {
    std::string out;
    for (char c : s) {
        if (c == '\t') out += "\\t";
        else if (c == '\n') out += "\\n";
        else if (c == '\\') out += "\\\\";
        else out += c;
    }
    return out;
}

std::string unescape(const std::string& s) {
    std::string out;
    for (size_t i = 0; i < s.size(); ++i) {
        if (s[i] == '\\' && i + 1 < s.size()) {
            if (s[i + 1] == 't') { out += '\t'; ++i; }
            else if (s[i + 1] == 'n') { out += '\n'; ++i; }
            else if (s[i + 1] == '\\') { out += '\\'; ++i; }
            else out += s[i];
        } else {
            out += s[i];
        }
    }
    return out;
}

void splitByTab(const std::string& line, std::vector<std::string>& parts) {
    parts.clear();
    std::string cur;
    for (size_t i = 0; i <= line.size(); ++i) {
        if (i == line.size() || line[i] == kSep) {
            parts.push_back(unescape(cur));
            cur.clear();
        } else {
            cur += line[i];
        }
    }
}

}  // namespace

bool Persistence::save(const RbacEngine& engine, const std::string& filepath) {
    std::ofstream ofs(filepath);
    if (!ofs) return false;

    for (const auto& u : engine.listUsers())
        ofs << "USER" << kSep << escape(u.id) << kSep << escape(u.name) << "\n";

    for (const auto& r : engine.listRoles())
        ofs << "ROLE" << kSep << escape(r.id) << kSep << escape(r.name)
            << kSep << escape(r.description) << "\n";

    for (const auto& p : engine.listPermissions())
        ofs << "PERM" << kSep << escape(p.id) << kSep << escape(p.name)
            << kSep << escape(p.description) << "\n";

    for (const auto& u : engine.listUsers()) {
        for (const auto& roleId : engine.getRolesForUser(u.id))
            ofs << "UR" << kSep << escape(u.id) << kSep << escape(roleId) << "\n";
    }

    for (const auto& r : engine.listRoles()) {
        for (const auto& permId : engine.getPermissionsForRole(r.id))
            ofs << "RP" << kSep << escape(r.id) << kSep << escape(permId) << "\n";
    }

    return !!ofs;
}

bool Persistence::load(RbacEngine& engine, const std::string& filepath) {
    std::ifstream ifs(filepath);
    if (!ifs) return false;

    std::string line;
    std::vector<std::string> parts;

    while (std::getline(ifs, line)) {
        if (line.empty()) continue;
        splitByTab(line, parts);
        if (parts.empty()) continue;

        if (parts[0] == "USER" && parts.size() >= 3)
            engine.addUser(parts[1], parts[2]);
        else if (parts[0] == "ROLE" && parts.size() >= 3)
            engine.addRole(parts[1], parts[2], parts.size() >= 4 ? parts[3] : "");
        else if (parts[0] == "PERM" && parts.size() >= 2)
            engine.addPermission(parts[1], parts.size() >= 3 ? parts[2] : "",
                                parts.size() >= 4 ? parts[3] : "");
        else if (parts[0] == "UR" && parts.size() >= 3)
            engine.assignRoleToUser(parts[1], parts[2]);
        else if (parts[0] == "RP" && parts.size() >= 3)
            engine.assignPermissionToRole(parts[1], parts[2]);
    }

    return true;
}

}  // namespace rbac
