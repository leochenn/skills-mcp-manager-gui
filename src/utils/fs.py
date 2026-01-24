import hashlib
import os
import re


def get_skill_description(skill_dir):
    md_path = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(md_path):
        return "未找到 SKILL.md"
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
        lines = content.split("\n")
        desc_lines = []
        in_desc = False
        for line in lines:
            stripped = line.strip()
            if stripped == "---" and in_desc:
                break
            if stripped.startswith("description:"):
                in_desc = True
                val = line.split(":", 1)[1].strip()
                if val:
                    if (val.startswith('"') and val.endswith('"')) or (
                        val.startswith("'") and val.endswith("'")
                    ):
                        val = val[1:-1]
                    desc_lines.append(val)
                continue
            if in_desc:
                if not line.strip():
                    continue
                if re.match(r"^[a-zA-Z0-9_-]+:", line):
                    break
                desc_lines.append(stripped)
        if desc_lines:
            return " ".join(desc_lines)
        return "未找到 description 字段"
    except Exception as e:
        return f"读取错误: {e}"


def calculate_dir_hash(directory, ignore_func=None):
    if not os.path.exists(directory):
        return None
    sha256 = hashlib.sha256()
    for root, dirs, files in os.walk(directory):
        if ignore_func:
            ignored = ignore_func(root, dirs + files)
            dirs[:] = [d for d in dirs if d not in ignored]
            files[:] = [f for f in files if f not in ignored]

        dirs.sort()
        files.sort()
        for d in dirs:
            sha256.update(d.encode("utf-8"))
        for f in files:
            sha256.update(f.encode("utf-8"))
            file_path = os.path.join(root, f)
            try:
                with open(file_path, "rb") as f_obj:
                    while True:
                        data = f_obj.read(4096)
                        if not data:
                            break
                        sha256.update(data)
            except Exception:
                pass
    return sha256.hexdigest()


def is_text_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in [
        ".txt",
        ".py",
        ".md",
        ".json",
        ".js",
        ".html",
        ".css",
        ".xml",
        ".yaml",
        ".yml",
        ".bat",
        ".sh",
        ".ps1",
    ]


def get_ignore_patterns(src_dir):
    gitignore_path = os.path.join(src_dir, ".gitignore")
    patterns = []
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if line.endswith("/"):
                            line = line[:-1]
                        patterns.append(line)
        except Exception:
            pass
    return patterns

