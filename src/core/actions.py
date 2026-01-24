import json
import os
import shutil
from urllib.parse import urlparse

from ..utils.fs import get_ignore_patterns
from ..utils.jsonc import load_jsonc


def delete_skill_dirs(target_dir, skill_names):
    errors = []
    for name in skill_names:
        try:
            shutil.rmtree(os.path.join(target_dir, name))
        except Exception as e:
            errors.append((name, str(e)))
    return errors


def import_skills_to_target(skills_dir, target_dir, selected_items):
    errors = []
    for item in selected_items:
        skill = item.get("rel_path", item["name"])
        src = os.path.join(skills_dir, skill)
        dst = os.path.join(target_dir, os.path.basename(skill))
        try:
            if os.path.exists(dst):
                shutil.rmtree(dst)

            ignore_func = None
            patterns = get_ignore_patterns(src)
            if patterns:
                ignore_func = shutil.ignore_patterns(*patterns)

            shutil.copytree(src, dst, ignore=ignore_func)
        except Exception as e:
            errors.append((skill, str(e)))
    return errors


def delete_mcp_servers(current_data, keys):
    servers = current_data.get("mcpServers", {})
    for k in keys:
        if k in servers:
            del servers[k]
    current_data["mcpServers"] = servers
    return current_data


def import_mcp_servers(current_data, source_mcp_file, keys):
    source_data = load_jsonc(source_mcp_file).get("mcpServers", {})
    if "mcpServers" not in current_data:
        current_data["mcpServers"] = {}
    for k in keys:
        if k in source_data:
            current_data["mcpServers"][k] = source_data[k]
    return current_data


def save_mcp_target(target_file, current_data):
    with open(target_file, "w", encoding="utf-8") as f:
        json.dump(current_data, f, indent=2, ensure_ascii=False)


def get_install_final_output_dir(github_url, target_dir):
    try:
        parsed = parse_github_tree_url(github_url)
        if parsed.get("error"):
            return None
        owner = parsed.get("owner")
        skill_name = parsed.get("skill_name")
        if not owner or not skill_name:
            return None
        return os.path.join(target_dir, owner, skill_name)
    except Exception:
        return None


def parse_github_tree_url(github_url):
    url = github_url.strip()
    if "://" not in url:
        url = "https://" + url.lstrip("/")

    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    if not host.endswith("github.com"):
        return {"error": "not_github"}

    try:
        segments = parsed.path.strip("/").split("/")
        owner = segments[0]
        repo = segments[1]
        if segments[2] != "tree":
            return {"error": "parse_failed"}
        branch = segments[3]
        folder_path = "/".join(segments[4:])
        skill_name = folder_path.split("/")[-1] if folder_path else ""
        return {
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "folder_path": folder_path,
            "skill_name": skill_name,
        }
    except Exception:
        return {"error": "parse_failed"}

