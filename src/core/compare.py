import os
import shutil

from ..utils.fs import calculate_dir_hash, get_ignore_patterns
from ..utils.jsonc import load_jsonc


def collect_target_skill_dirs(target_dir):
    if not os.path.exists(target_dir):
        return []
    try:
        return [
            i
            for i in os.listdir(target_dir)
            if os.path.isdir(os.path.join(target_dir, i))
        ]
    except Exception:
        return []


def collect_source_skill_rel_paths(skills_dir):
    if not os.path.exists(skills_dir):
        return []
    source_skills = []
    for root, dirs, files in os.walk(skills_dir):
        if "SKILL.md" in files:
            rel_path = os.path.relpath(root, skills_dir).replace("\\", "/")
            source_skills.append(rel_path)
    return source_skills


def build_skills_right_rows(skills_dir, target_dir):
    if not os.path.exists(skills_dir):
        return None, "源目录不存在，请在设置中配置"

    right_rows = []
    source_skills = collect_source_skill_rel_paths(skills_dir)

    for skill_rel_path in sorted(source_skills):
        s_path = os.path.join(skills_dir, skill_rel_path)
        t_path = os.path.join(target_dir, os.path.basename(skill_rel_path))

        parts = skill_rel_path.split("/")
        if len(parts) > 1:
            group_name = "/".join(parts[:-1])
            display_name = parts[-1]
        else:
            group_name = None
            display_name = parts[0]

        in_target = os.path.exists(t_path)

        status = "🆕 新增"
        is_diff = False

        if in_target:
            patterns = get_ignore_patterns(s_path)
            ignore_func = shutil.ignore_patterns(*patterns) if patterns else None

            if calculate_dir_hash(s_path, ignore_func) == calculate_dir_hash(t_path, ignore_func):
                status = "✅ 一致"
            else:
                status = "⚠️ 差异"
                is_diff = True

        right_rows.append(
            {
                "name": display_name,
                "rel_path": skill_rel_path,
                "status": status,
                "is_diff": is_diff,
                "s_path": s_path,
                "t_path": t_path,
                "group": group_name,
            }
        )

    return right_rows, None


def read_mcp_current_data(target_file):
    if not os.path.exists(target_file):
        return {}, []
    try:
        current_data = load_jsonc(target_file)
        left_items = sorted(current_data.get("mcpServers", {}).keys())
        return current_data, left_items
    except Exception:
        return {}, []


def build_mcp_right_rows(source_mcp_file, current_data):
    if not os.path.exists(source_mcp_file):
        return None, "源配置文件不存在"

    try:
        source_data = load_jsonc(source_mcp_file).get("mcpServers", {})
        target_servers = current_data.get("mcpServers", {})
    except Exception as e:
        return None, f"Error: {e}"

    right_rows = []
    for key in sorted(source_data.keys()):
        in_target = key in target_servers
        status = "🆕 新增"
        is_diff = False

        if in_target:
            if source_data[key] == target_servers[key]:
                status = "✅ 一致"
            else:
                status = "⚠️ 差异"
                is_diff = True

        right_rows.append(
            {
                "key": key,
                "status": status,
                "is_diff": is_diff,
                "source_val": source_data[key],
                "target_val": target_servers.get(key, {}),
            }
        )

    return right_rows, None

