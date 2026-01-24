import os
import json
import shutil
import sys
import re
import hashlib
import difflib
import base64
import time
import threading
import requests
import webbrowser
from io import BytesIO
import tkinter as tk
from tkinter import filedialog, messagebox

try:
    import customtkinter as ctk
    from PIL import Image
except ImportError:
    print("Please install customtkinter and pillow: pip install customtkinter pillow")
    sys.exit(1)

# --- Icons (Base64) ---
ICON_SETTINGS = "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAA2ElEQVR4nO2YQQ7EIAhFgcxBOZo3nUkXbppOR+GrY/pf0k0rCF9MURFCCCGEkOeiI5y6+/vbt1IKdE6dFfioRHR24OhETBYGj7DXmbU+Ym9oxOgumJZAMrZnXgKiZ/I61pPlE94DiIlRfm2k+kdA9emxG5pAi0pXQd8lklmF9ApkVSyr/wO9CqL3j8nmmGyOoR3+qml0N2q790LWa9Ci4DHmPO7qHWKFFKVapDQc4CdUQug6/otmrqqZ6UYjPPc8gFSzJEpy+15IBci2txIr74UIIYQQQiTOB2RshkzvoJmwAAAAAElFTkSuQmCC"
ICON_FOLDER = "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAAgUlEQVR4nO3UMQ7CQAwF0cl0XAzODBejhB5KsolG+JVbfK1t2TDGGOOfbZ8Pz/v19Wvo5fb4yl3FFaF7NOHUAo7kquCjpuDK8COKkLjtzAXc48rlJyBxEidxEidxEidxEidxEidxEidxEidxEidxEidxEidxEidxEufZHxhjjMGZ3uEpESCSxrPtAAAAAElFTkSuQmCC"
ICON_DELETE = "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAAbklEQVR4nO3T0QkCARDE0Jhq7MH67cFuzho8BIk3739hYAnMzMzM79zOHr4et+O7U+D+PD7eI3ESJ3Fy1Yi/EfX9RLR/9wGJkziJkziJkziJkziJkziJkziJkziJkziJkziJkziJ89cDZmZmLu0NFsoIOTpBOZcAAAAASUVORK5CYII="
ICON_IMPORT = "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAAqklEQVR4nO3Y3Q2DQAwDYON5OmBHyIDdp31HqigXR5XB3zMXwuV+IoCIiIj4n00e8fl6Hz5TD9l7CXOEOcIcYY4wR5gjzBHmCHOEOcIcYY4wt412nWfV+S51vQLClrgTz34JsTVaVYVaj9OvQPcjqjdes4RWk6h+BW++BzqzKdo/hNKvSeWvxOQeOJpd8QVITPiWpPr2xuQptE92IPlLHKPzJrrWiIiIq/gADssVPKWjctEAAAAASUVORK5CYII="
ICON_BACK = "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAAmUlEQVR4nO3V0Q3DMAhFUYwyqEdj00aeoHEK9nN1z7/RI4BiBgAAAPyt3vunsr6fHH647NDgZRNYGT51AquDp05gV/ihmXD4iGhlK7Tzq/+8QirhpyegFHx6Aorhpxp4clDyNxARTa0Rf/NIqQl/+1BlGi2jyLcDr2zUM4rsnIRnFdq1Up5dUOEu0ozbUP0BPnZ8AwAAALAyN6aiNoivubMEAAAAAElFTkSuQmCC"
ICON_SKILLS = "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAAXUlEQVR4nO3OQQ3CAADF0FJluEETbnA2LGwHsjT8d29SmJmZmflfj8vF63Pwa+/n6S+JkziJkziJkziJkziJkziJkziJkziJkziJkziJkziJkziJ8+6BmZmZGe7zBRSAAzItrymPAAAAAElFTkSuQmCC"
ICON_MCP = "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAAaUlEQVR4nO3WMQ6AMAxDUWNxgB6YkQPnBrCyIMRAi9X/9igZmrgSAAAAgFktvRq1rR1va2qvx/mscFY4K9z65RvuwQpnhbNmyYH2ox2oSz7Mc4VGKJI4wNKrEZ+5G/FXyKMHAAAAAKBRTnCNECThcd6KAAAAAElFTkSuQmCC"

# --- Configuration & Theme ---
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_CONFIG_FILE = os.path.join(PROJECT_ROOT, 'app_config.json')
HISTORY_FILE = os.path.join(PROJECT_ROOT, 'history.json')

COLORS = {
    "primary": "#0067c0",
    "primary_hover": "#005a9e",
    "text_link": ("#0067c0", "#66b2ff"), # Light/Dark
    "text_nested": ("#5c2d91", "#b4a0ff"), # Nested Skill Color (Purple)
    "success": "#107c10",
    "success_bg": ("#e6ffec", "#1e3a29"), # Badge BG
    "success_text": ("#107c10", "#00e676"), # Badge Text
    "warning": "#d83b01",
    "warning_bg": ("#ffebe9", "#3a1e1e"),
    "warning_text": ("#d83b01", "#ffaa44"),
    "danger": "#a80000",
    "bg_card": ("#ffffff", "#2b2b2b"),
    "item_card": ("#f8f9fa", "gray25"),
    "item_hover": ("#eef0f2", "gray30"),
    "text_sub": ("#606060", "#a0a0a0"),
    "neutral_bg": ("#f3f2f1", "gray35"),
    "neutral_text": ("#605e5c", "#c8c8c8")
}

# --- Helpers ---

def load_icon(b64_data, size=(20, 20), color=None):
    """Load icon from base64 string."""
    try:
        img_data = base64.b64decode(b64_data)
        image = Image.open(BytesIO(img_data))
        # Resize logic if needed, but CTkImage handles it well
        return ctk.CTkImage(light_image=image, dark_image=image, size=size)
    except Exception as e:
        print(f"Error loading icon: {e}")
        return None

class AppConfig:
    def __init__(self):
        self.skills_dir = os.path.join(PROJECT_ROOT, 'skills')
        self.mcp_settings_file = os.path.join(PROJECT_ROOT, 'mcp', 'settings.json')
        self.load()
    
    def load(self):
        if os.path.exists(APP_CONFIG_FILE):
            try:
                with open(APP_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.skills_dir = data.get('skills_dir', self.skills_dir)
                    self.mcp_settings_file = data.get('mcp_settings_file', self.mcp_settings_file)
            except:
                pass
    
    def save(self):
        try:
            data = {
                'skills_dir': self.skills_dir,
                'mcp_settings_file': self.mcp_settings_file
            }
            with open(APP_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise e

app_config = AppConfig()

def load_jsonc(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    pattern = r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"'
    regex = re.compile(pattern, re.DOTALL | re.MULTILINE)
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'): return ""
        return s
    json_str = regex.sub(replacer, content)
    return json.loads(json_str)

def get_skill_description(skill_dir):
    md_path = os.path.join(skill_dir, 'SKILL.md')
    if not os.path.exists(md_path): return "未找到 SKILL.md"
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        lines = content.split('\n')
        desc_lines = []
        in_desc = False
        for line in lines:
            stripped = line.strip()
            if stripped == '---' and in_desc: break
            if stripped.startswith('description:'):
                in_desc = True
                val = line.split(':', 1)[1].strip()
                if val:
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        val = val[1:-1]
                    desc_lines.append(val)
                continue
            if in_desc:
                if not line.strip(): continue
                if re.match(r'^[a-zA-Z0-9_-]+:', line): break
                desc_lines.append(stripped)
        if desc_lines: return " ".join(desc_lines)
        return "未找到 description 字段"
    except Exception as e:
        return f"读取错误: {e}"

def calculate_dir_hash(directory, ignore_func=None):
    if not os.path.exists(directory): return None
    sha256 = hashlib.sha256()
    for root, dirs, files in os.walk(directory):
        if ignore_func:
            ignored = ignore_func(root, dirs + files)
            dirs[:] = [d for d in dirs if d not in ignored]
            files[:] = [f for f in files if f not in ignored]
            
        dirs.sort()
        files.sort()
        for d in dirs: sha256.update(d.encode('utf-8'))
        for f in files:
            sha256.update(f.encode('utf-8'))
            file_path = os.path.join(root, f)
            try:
                with open(file_path, 'rb') as f_obj:
                    while True:
                        data = f_obj.read(4096)
                        if not data: break
                        sha256.update(data)
            except: pass
    return sha256.hexdigest()

def is_text_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in ['.txt', '.py', '.md', '.json', '.js', '.html', '.css', '.xml', '.yaml', '.yml', '.bat', '.sh', '.ps1']

def center_window(window, width, height):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

def show_message(parent, title, message):
    """Show a centered message dialog."""
    try:
        dialog = ctk.CTkToplevel(parent)
        dialog.title(title)
        dialog.transient(parent)
        dialog.grab_set()
        
        w, h = 300, 150
        center_window_relative(dialog, parent, w, h)
        
        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text=message, wraplength=260, font=("Segoe UI", 12)).pack(pady=(10, 20), expand=True)
        
        ctk.CTkButton(frame, text="确定", width=100, command=dialog.destroy).pack(pady=(0, 10))
        
        dialog.lift()
        dialog.focus_force()
        parent.wait_window(dialog)
    except Exception as e:
        messagebox.showinfo(title, message)

def center_window_relative(window, parent, width, height):
    """Center window relative to its parent."""
    window.update_idletasks()
    x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
    y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

def get_ignore_patterns(src_dir):
    """Read .gitignore and return patterns to ignore."""
    gitignore_path = os.path.join(src_dir, '.gitignore')
    patterns = []
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Remove trailing slash as shutil.ignore_patterns matches names
                        if line.endswith('/'):
                            line = line[:-1]
                        patterns.append(line)
        except Exception as e:
            print(f"Error reading .gitignore: {e}")
    return patterns

class GitHubDownloader:
    def __init__(self, log_callback):
        self.log_callback = log_callback
        self.stop_flag = False

    def download(self, github_url, output_dir):
        parts = github_url.strip("/").split("/")
        if "github.com" not in parts:
            self.log_callback("错误: 不是有效的 GitHub URL", "error")
            return False

        try:
            # https://github.com/{owner}/{repo}/tree/{branch}/{path}
            owner = parts[3]
            repo = parts[4]
            branch = parts[6]
            folder_path = "/".join(parts[7:])
            skill_name = folder_path.split("/")[-1]
        except IndexError:
             self.log_callback("错误: URL 格式解析失败，请确保包含 tree/{branch}/目录路径", "error")
             return False
        
        # New directory structure: TargetDir/Owner/SkillName
        # BUT: we need to support "collection" downloads.
        # Logic: 
        # 1. Start scanning from the given URL.
        # 2. If SKILL.md found in root -> It's a skill. Download to TargetDir/Owner/SkillName.
        # 3. If SKILL.md NOT found -> It might be a collection. Scan children.
        #    For each child dir that contains SKILL.md (directly or nested), hoist it to TargetDir/Owner/ChildName.
        
        # We need a new recursive discovery method that decides WHERE to download.
        # To avoid double request, we can use the first request to determine type.
        
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{folder_path}?ref={branch}"
        
        # Base destination for flattened skills (TargetDir/Owner)
        base_dest_dir = os.path.join(output_dir, owner)
        
        try:
            self.log_callback(f"正在分析目录结构: {owner}/{repo}/{folder_path}", "info")
            # Start the smart download process
            # We pass: 
            # - current_api_url: URL to scan
            # - base_dest_dir: Where 'hoisted' skills should end up (e.g. .../anthropics)
            # - current_rel_path: Relative path from the start of our download (for logging/logic)
            # - is_root: True for the first call
            
            self._smart_download(api_url, base_dest_dir, is_root=True, root_name=skill_name)
            
            # Record GitHub Address (record once for the parent URL)
            self._record_address(base_dest_dir, github_url)
            
            self.log_callback("所有下载任务完成！", "success")
            return True
        except Exception as e:
            self.log_callback(f"下载过程出错: {e}", "error")
            return False

    def _smart_download(self, api_url, base_dest_dir, is_root=False, root_name=None):
        """
        Entry point for smart download logic.
        is_root: True if this is the initial call.
        root_name: The name of the folder from the original URL (e.g. 'skill-creator' or 'skills').
        """
        # If is_root, we just call the recursive function with the root_name as current_dir_name.
        self._smart_download_recursive(api_url, base_dest_dir, current_dir_name=root_name)

    def _smart_download_recursive(self, api_url, base_dest_dir, current_dir_name=None):
        """
        api_url: URL to fetch items from.
        base_dest_dir: The 'Owner' directory (e.g., .../skills/anthropics).
        current_dir_name: The name of the current folder we are processing (e.g. 'skill-creator'). 
                          If None (Root), we try to derive or handled specially.
                          Actually, for Root, we might have a name from the original URL logic.
        """
        if self.stop_flag: return
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(api_url, headers=headers)
            if response.status_code != 200:
                self.log_callback(f"Error fetching {api_url}", "error")
                return

            items = response.json()
            if isinstance(items, dict) and items.get("type") == "file": items = [items]
            
            # Check if this is a Skill
            has_skill_md = any(item['name'].lower() == 'skill.md' for item in items)
            
            if has_skill_md:
                # IT IS A SKILL!
                # We should download it.
                # Target? 
                # If this was called from a recursion, 'current_dir_name' is the folder name.
                # We want to put it in base_dest_dir / current_dir_name.
                
                # Special Case: Root
                # If we are at root and it HAS skill.md, we download to base_dest_dir / root_name.
                # But we need to know root_name.
                
                if not current_dir_name:
                    # Fallback if name not provided (shouldn't happen with proper logic)
                    self.log_callback("Error: Skill found but name unknown", "error")
                    return

                target_path = os.path.join(base_dest_dir, current_dir_name)
                self.log_callback(f"发现 Skill: {current_dir_name}", "success")
                self.log_callback(f"目标路径: {target_path}", "info")
                
                if not os.path.exists(target_path):
                    os.makedirs(target_path)
                
                # Download content
                self._download_items(items, target_path)
                return # Done for this branch (it's a skill, we don't look deeper for other skills inside a skill)
            
            else:
                # NOT A SKILL (Collection or Intermediate)
                # Ignore files.
                # Dive into directories.
                # Important: When diving, we reset the "potential target name".
                # If we are in 'pdf2' (not skill), and we see 'pdf3', 
                # we call recurse with name='pdf3'.
                # The target will be base_dest_dir / pdf3.
                
                # But wait, what if Root (e.g. 'skill-creator') DOES NOT have skill.md?
                # Then we treat 'skill-creator' as a collection.
                # We look at children.
                
                # Handling Root Name:
                # The caller should pass the root name if it's the first call.
                # But if Root is a collection, we DON'T want to use Root name in the final path for children.
                # e.g. Root='skills' (collection). Child='pdf'. 
                # We want .../anthropics/pdf. NOT .../anthropics/skills/pdf.
                # So we simply ignore current_dir_name if it's not a skill!
                
                for item in items:
                    if self.stop_flag: return
                    if item['type'] == 'dir':
                        # Recurse
                        # We pass item['name'] as the new potential skill name
                        self._smart_download_recursive(item['url'], base_dest_dir, item['name'])
                        
        except Exception as e:
            self.log_callback(f"Error: {e}", "error")

    def _download_items(self, items, local_path):
        headers = {'User-Agent': 'Mozilla/5.0'}
        for item in items:
            if self.stop_flag: return
            
            name = item['name']
            path = os.path.join(local_path, name)
            
            if item['type'] == 'dir':
                if not os.path.exists(path): os.makedirs(path)
                # Standard recursive download for content INSIDE a skill
                self._download_recursive(item['url'], path, "")
            else:
                self.log_callback(f"⬇️  正在下载: {name}...", "file_start")
                resp = requests.get(item['download_url'], headers=headers)
                with open(path, "wb") as f: f.write(resp.content)
                self.log_callback(f"下载完成: {name}", "success")

    def _record_address(self, owner_dir, url):
        try:
            if not os.path.exists(owner_dir): os.makedirs(owner_dir) # Ensure owner dir exists
            file_path = os.path.join(owner_dir, "github_address.txt")
            existing_urls = []
            
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    existing_urls = [line.strip() for line in f.readlines() if line.strip()]
            
            # Clean URL (remove trailing slash)
            url = url.rstrip('/')
            
            # Logic: Merge and Deduplicate
            # 1. If new url is a child of any existing url -> Do nothing (Parent covers it).
            # 2. If new url is a parent of any existing urls -> Remove children, keep Parent.
            # 3. If new url is a sibling of any existing url (same parent) -> Merge to Parent.
            
            # To handle sibling merging, we need to detect "Sibling" relationship.
            # Sibling means: They share the same parent directory in the URL structure.
            # e.g. .../skills/art and .../skills/brand -> share .../skills.
            
            # Let's iterate and build a new list.
            new_list = []
            is_covered = False
            
            # Helper to check parent/child
            def is_parent_of(parent, child):
                return child.startswith(parent + '/')
            
            def get_parent_url(u):
                return u.rsplit('/', 1)[0]
                
            # First pass: Check if new URL is already covered by existing parents
            for ex in existing_urls:
                if ex == url or is_parent_of(ex, url):
                    is_covered = True
                    break
            
            if is_covered:
                # Already covered, no change needed.
                self.log_callback(f"地址已存在或被父级包含，跳过记录。", "info")
                return

            # Second pass: New URL is NOT covered. 
            # Check if New URL covers existing children (Reverse of 1).
            # And also check for SIBLINGS to merge up.
            
            # This is tricky because merging up might create a NEW parent that itself needs checking.
            # So let's add the new URL to the list, then run a "Optimization" pass until stable.
            
            current_urls = existing_urls + [url]
            
            has_changed = True
            while has_changed:
                has_changed = False
                optimized_urls = set()
                
                # Sort to process shorter (parents) first? Or just set?
                # List for iteration
                temp_list = sorted(list(set(current_urls)))
                
                # 1. Remove children if parent exists
                parents = set()
                for u in temp_list:
                    is_child = False
                    for other in temp_list:
                        if u != other and is_parent_of(other, u):
                            is_child = True
                            break
                    if not is_child:
                        parents.add(u)
                
                # Now 'parents' contains only top-level items from the current set.
                # 2. Check for Siblings among these 'parents'.
                # We group by their parent URL.
                
                groups = {}
                for u in parents:
                    p_url = get_parent_url(u)
                    if p_url not in groups: groups[p_url] = []
                    groups[p_url].append(u)
                    
                final_round_urls = []
                for p_url, children in groups.items():
                    # If we have 2 or more children of the same parent -> Merge to Parent
                    # UNLESS the parent itself is effectively the root (like github.com/anthropics/skills/tree/main).
                    # Actually, user said: ".../skills/art" and ".../skills/brand" -> ".../skills".
                    # So yes, merge.
                    
                    # But we need to be careful not to merge too high (e.g. github.com/anthropics).
                    # The user seems to imply merging skill folders.
                    # Let's assume merging is always safe if they share a parent in the 'tree' path.
                    # Typically URL: .../tree/{branch}/{path}
                    # We should only merge if the parent is still inside the 'tree/{branch}' structure.
                    
                    if len(children) > 1:
                        # Merge!
                        # The new candidate is p_url.
                        # But wait, p_url might be "github.com/.../tree/main". 
                        # That's fine.
                        final_round_urls.append(p_url)
                        has_changed = True # We changed structure (children -> parent)
                    else:
                        final_round_urls.append(children[0])
                
                if has_changed:
                    current_urls = final_round_urls
                else:
                    # No sibling merges happened. We are stable.
                    # 'parents' set from step 1 was already deduplicated.
                    current_urls = list(parents)

            # Write back if different
            current_urls.sort()
            existing_urls.sort()
            
            if current_urls != existing_urls:
                with open(file_path, "w", encoding="utf-8") as f:
                    for u in current_urls:
                        f.write(u + "\n")
                self.log_callback(f"地址记录已更新 (已合并/去重): {file_path}", "info")
            else:
                self.log_callback(f"地址记录无需更新。", "info")

        except Exception as e:
            self.log_callback(f"无法写入地址文件: {e}", "error")

    def _download_recursive(self, api_url, local_base_path, relative_path):
        if self.stop_flag: return

        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(api_url, headers=headers)
            if response.status_code != 200:
                self.log_callback(f"获取目录信息失败: {api_url} (代码: {response.status_code})", "error")
                return

            data = response.json()
            if isinstance(data, dict) and data.get("type") == "file":
                data = [data]

            for item in data:
                if self.stop_flag: return
                
                item_type = item["type"]
                item_name = item["name"]
                
                # logic to keep relative structure correct
                # We are downloading folder_path to output_dir.
                # If we are at root of download, we just put items in output_dir.
                # But wait, ai_studio_code.py logic:
                # current_local_path = os.path.join(local_base_path, item_name)
                # local_base_path starts as output_dir.
                
                current_local_path = os.path.join(local_base_path, item_name)

                if item_type == "dir":
                    if not os.path.exists(current_local_path):
                        os.makedirs(current_local_path)
                        self.log_callback(f"📁 创建目录: {item_name}", "dir")
                    
                    self._download_recursive(item["url"], current_local_path, "")
                
                elif item_type == "file":
                    download_url = item["download_url"]
                    self.log_callback(f"⬇️  正在下载: {item_name}...", "file_start")
                    
                    file_resp = requests.get(download_url, headers=headers)
                    with open(current_local_path, "wb") as f:
                        f.write(file_resp.content)
                        
                    self.log_callback(f"下载完成: {item_name}", "success")
                    # We can update the last log item or just append "Done"
                    # But for simplicity, I will just log start. 
                    # Actually, the user screenshot shows "... 完成" at the end of the line.
                    # Since I am using labels, I can't easily append to the same label unless I keep a reference.
                    # I will log "Done" as a separate update or just log once when done?
                    # The screenshot shows: "⬇️ 正在下载: file... 完成"
                    # I'll implement a way to update the last log or just log "Finished downloading file".
                    # Let's keep it simple: Log "Downloading...", then "Downloaded".
                    # Or try to match the screenshot: 
                    # I will modify the log callback to support updating the last line if needed, 
                    # or just print "Downloaded: {item_name}".
                    # For now, let's just log "Downloading..." then nothing if success, or "Done".
                    
        except Exception as e:
             raise e

# --- Data Management ---

class HistoryManager:
    def __init__(self):
        self.data = {"skills_dirs": [], "mcp_files": []}
        self.load()

    def load(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                
                # Migration: Normalize paths and deduplicate
                for key in ["skills_dirs", "mcp_files"]:
                    cleaned_list = []
                    seen_paths = set()
                    
                    # Collect all items, normalize paths
                    temp_items = []
                    for item in self.data.get(key, []):
                        p = ""
                        t = 0
                        if isinstance(item, str):
                            p = item
                        elif isinstance(item, dict) and "path" in item:
                            p = item["path"]
                            t = item.get("time", 0)
                            
                        if p:
                            # Normalize path separators
                            p = os.path.normpath(p)
                            temp_items.append({"path": p, "time": t})
                    
                    # Sort by time desc (newest first)
                    temp_items.sort(key=lambda x: x["time"], reverse=True)
                    
                    # Deduplicate keeping newest
                    for item in temp_items:
                        # Use normcase for case-insensitive comparison on Windows
                        norm_p = os.path.normcase(item["path"])
                        if norm_p not in seen_paths:
                            seen_paths.add(norm_p)
                            cleaned_list.append(item)
                            
                    self.data[key] = cleaned_list
            except: pass

    def save(self):
        try:
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
        except: pass

    def _add_path(self, key, path):
        path = os.path.normpath(path)
        # Remove existing (check with normcase)
        self.data[key] = [item for item in self.data[key] if os.path.normcase(item["path"]) != os.path.normcase(path)]
        # Add new with timestamp
        self.data[key].insert(0, {"path": path, "time": time.time()})
        # Sort by time desc
        self.data[key].sort(key=lambda x: x.get("time", 0), reverse=True)
        # Keep top 10
        self.data[key] = self.data[key][:10]
        self.save()

    def _remove_path(self, key, path):
        path = os.path.normpath(path)
        self.data[key] = [item for item in self.data[key] if os.path.normcase(item["path"]) != os.path.normcase(path)]
        self.save()

    def add_skills_dir(self, path): self._add_path("skills_dirs", path)
    def add_mcp_file(self, path): self._add_path("mcp_files", path)
    
    def get_skills_dirs(self): 
        return [item["path"] for item in self.data.get("skills_dirs", [])]
        
    def get_mcp_files(self): 
        return [item["path"] for item in self.data.get("mcp_files", [])]
        
    def remove_skills_dir(self, path): self._remove_path("skills_dirs", path)
    def remove_mcp_file(self, path): self._remove_path("mcp_files", path)

    def get_all_history(self):
        """Get all history items sorted by time."""
        skills = []
        for item in self.data.get("skills_dirs", []):
            skills.append({**item, "type": "skill"})
            
        mcp = []
        for item in self.data.get("mcp_files", []):
            mcp.append({**item, "type": "mcp"})
            
        all_items = skills + mcp
        # Sort by time desc
        all_items.sort(key=lambda x: x.get("time", 0), reverse=True)
        return all_items

# --- Custom UI Components ---

class ScrollableCheckBoxFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, item_list=None, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.command = command
        self.checkboxes = []
        if item_list:
            for item in item_list:
                self.add_item(item)

    def add_item(self, item, command=None):
        # Card Frame
        frame = ctk.CTkFrame(self, fg_color=COLORS["item_card"], corner_radius=6, height=40)
        frame.pack(fill="x", pady=4, padx=2)
        
        # Hover Effect
        def on_enter(e): frame.configure(fg_color=COLORS["item_hover"])
        def on_leave(e): frame.configure(fg_color=COLORS["item_card"])
        frame.bind("<Enter>", on_enter)
        frame.bind("<Leave>", on_leave)
        
        # Checkbox
        checkbox = ctk.CTkCheckBox(frame, text="", width=24, checkbox_width=20, checkbox_height=20)
        checkbox.pack(side="left", padx=(10, 10), pady=10)
        checkbox.bind("<Enter>", on_enter)
        checkbox.bind("<Leave>", on_leave)
        
        # Click Logic for Frame (Toggle Checkbox)
        def toggle_check(e):
            if checkbox.get(): checkbox.deselect()
            else: checkbox.select()
        
        frame.bind("<Button-1>", toggle_check)
        
        if command:
            # Clickable label
            btn = ctk.CTkButton(frame, text=item, anchor="w", fg_color="transparent", text_color=COLORS["primary"], 
                              command=command, height=24, hover_color=COLORS["item_hover"], font=("Segoe UI", 13, "bold"))
            btn.pack(side="left", fill="x", expand=True, padx=5)
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
        else:
            lbl = ctk.CTkLabel(frame, text=item, anchor="w", font=("Segoe UI", 13, "bold"))
            lbl.pack(side="left", fill="x", expand=True, padx=5)
            lbl.bind("<Enter>", on_enter)
            lbl.bind("<Leave>", on_leave)
            lbl.bind("<Button-1>", toggle_check)
            
        self.checkboxes.append({"checkbox": checkbox, "value": item})

    def remove_item(self, item):
        for i, cb in enumerate(self.checkboxes):
            if cb["value"] == item:
                cb["checkbox"].master.destroy() # Destroy the frame
                self.checkboxes.pop(i)
                return

    def get_checked_items(self):
        return [cb["value"] for cb in self.checkboxes if cb["checkbox"].get() == 1]
    
    def clear(self):
        for cb in self.checkboxes:
            cb["checkbox"].master.destroy()
        self.checkboxes = []
    
    def set_message(self, message):
        self.clear()
        ctk.CTkLabel(self, text=message, text_color="gray").pack(pady=20)


class CompareListFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, skills_dir=None, **kwargs):
        super().__init__(master, **kwargs)
        self.rows = []
        self.groups = {}
        self.skills_dir = skills_dir

    def add_header(self, columns):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 5))
        for text, width in columns:
            ctk.CTkLabel(header_frame, text=text, width=width * 10, font=("Segoe UI", 12, "bold"), anchor="w").pack(side="left", padx=5)
        
    def add_group(self, name):
        if name in self.groups: return self.groups[name]
        
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", pady=(10, 2))
        
        # Header Row Frame
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x")
        
        # 1. Toggle Arrow
        arrow_btn = ctk.CTkButton(header_frame, text="▼", width=24, anchor="center", 
                                fg_color="transparent", text_color=("gray50", "gray70"), 
                                font=("Segoe UI", 11, "bold"),
                                hover_color=("gray90", "gray25"), height=24,
                                command=lambda n=name: self.toggle_group(n))
        arrow_btn.pack(side="left")

        # 2. Name (Link or Label)
        url = None
        if self.skills_dir:
            url_file = os.path.join(self.skills_dir, name, "github_address.txt")
            if os.path.exists(url_file):
                try:
                    with open(url_file, "r", encoding="utf-8") as f:
                        url = f.readline().strip()
                except: pass
        
        if url:
            # Use Label instead of Button to avoid focus border/shadow issues completely
            name_label = ctk.CTkLabel(header_frame, text=name, anchor="w", 
                                    text_color=COLORS["primary"],
                                    font=("Segoe UI", 11, "bold", "underline"))
            
            def on_enter(e): name_label.configure(text_color=COLORS["text_link"], cursor="hand2")
            def on_leave(e): name_label.configure(text_color=COLORS["primary"], cursor="")
            
            name_label.bind("<Enter>", on_enter)
            name_label.bind("<Leave>", on_leave)
            name_label.bind("<Button-1>", lambda e, u=url: webbrowser.open(u))
            name_label.pack(side="left", padx=(0, 5))
            
        else:
            # Non-link label
            name_label = ctk.CTkLabel(header_frame, text=name, anchor="w", 
                                    text_color=("gray50", "gray70"),
                                    font=("Segoe UI", 11, "bold"))
            
            # Allow clicking label to toggle too, for convenience
            name_label.bind("<Button-1>", lambda e, n=name: self.toggle_group(n))
            name_label.pack(side="left", padx=(0, 5))

        # 3. Spacer (Right Area - Toggle)
        # Use Frame instead of Button to avoid focus/hover artifacts
        spacer_frame = ctk.CTkFrame(header_frame, fg_color="transparent", height=24)
        spacer_frame.pack(side="left", fill="x", expand=True)
        
        # Bind click to toggle
        def on_spacer_enter(e): spacer_frame.configure(fg_color=("gray90", "gray25"))
        def on_spacer_leave(e): spacer_frame.configure(fg_color="transparent")
        
        spacer_frame.bind("<Enter>", on_spacer_enter)
        spacer_frame.bind("<Leave>", on_spacer_leave)
        spacer_frame.bind("<Button-1>", lambda e, n=name: self.toggle_group(n))
        
        content = ctk.CTkFrame(container, fg_color="transparent")
        content.pack(fill="x", padx=(10, 0))
        
        self.groups[name] = {"container": container, "arrow_btn": arrow_btn, "content": content, "expanded": True}
        return self.groups[name]

    def toggle_group(self, name):
        group = self.groups.get(name)
        if not group: return
        
        if group["expanded"]:
            group["content"].pack_forget()
            group["arrow_btn"].configure(text="▶")
            group["expanded"] = False
        else:
            group["content"].pack(fill="x", padx=(10, 0))
            group["arrow_btn"].configure(text="▼")
            group["expanded"] = True

    def expand_all(self):
        for name in self.groups:
            group = self.groups[name]
            if not group["expanded"]:
                group["content"].pack(fill="x", padx=(10, 0))
                group["arrow_btn"].configure(text="▼")
                group["expanded"] = True
                
    def collapse_all(self):
        for name in self.groups:
            group = self.groups[name]
            if group["expanded"]:
                group["content"].pack_forget()
                group["arrow_btn"].configure(text="▶")
                group["expanded"] = False

    def add_row(self, data, can_check=True, default_check=False, status_color=None, diff_command=None, name_command=None, group=None):
        parent = self
        if group:
            g = self.add_group(group)
            parent = g["content"]
            
        # Card Frame
        row_frame = ctk.CTkFrame(parent, fg_color=COLORS["item_card"], corner_radius=6, height=40)
        row_frame.pack(fill="x", pady=4, padx=2)
        
        # Hover Effect
        def on_enter(e): row_frame.configure(fg_color=COLORS["item_hover"])
        def on_leave(e): row_frame.configure(fg_color=COLORS["item_card"])
        row_frame.bind("<Enter>", on_enter)
        row_frame.bind("<Leave>", on_leave)
        
        # Checkbox
        checkbox = ctk.CTkCheckBox(row_frame, text="", width=24, checkbox_width=20, checkbox_height=20)
        if default_check: checkbox.select()
        if not can_check: checkbox.configure(state="disabled")
        checkbox.pack(side="left", padx=(10, 10), pady=10)
        checkbox.bind("<Enter>", on_enter)
        checkbox.bind("<Leave>", on_leave)
        
        # Click Logic for Frame (Toggle Checkbox)
        def toggle_check(e):
            if can_check:
                if checkbox.get(): checkbox.deselect()
                else: checkbox.select()
        
        row_frame.bind("<Button-1>", toggle_check)
        
        # Status Badge (Pack Right)
        status_text = data.get('status', '')
        # Clean status text
        status_clean = status_text.replace("✅ ", "").replace("🆕 ", "").replace("⚠️ ", "").strip()
        
        badge_bg = "gray"
        badge_text = "white"
        
        if "一致" in status_text:
            badge_bg = COLORS["neutral_bg"]
            badge_text = COLORS["neutral_text"]
            status_clean = "一致"
        elif "新增" in status_text:
            badge_bg = COLORS["success_bg"]
            badge_text = COLORS["success_text"]
            status_clean = "新增"
        elif "差异" in status_text:
            badge_bg = COLORS["warning_bg"]
            badge_text = COLORS["warning_text"]
            status_clean = "差异"
            
        status_frame = ctk.CTkFrame(row_frame, fg_color=badge_bg, corner_radius=10, height=24)
        status_frame.pack(side="right", padx=(5, 10))
        status_frame.bind("<Enter>", on_enter)
        status_frame.bind("<Leave>", on_leave)
        status_frame.bind("<Button-1>", toggle_check)
        
        ctk.CTkLabel(status_frame, text=f" {status_clean} ", text_color=badge_text, font=("Segoe UI", 11, "bold")).pack(padx=8, pady=2)
        
        # Ensure label inside badge passes click to frame logic
        for child in status_frame.winfo_children():
            child.bind("<Button-1>", toggle_check)

        # Action Button (Pack Right - Left of Status)
        if diff_command:
            diff_btn = ctk.CTkButton(row_frame, text="👁️", width=30, height=24, command=diff_command, 
                                   fg_color="transparent", hover_color=("gray80", "gray40"), 
                                   text_color=COLORS["text_sub"], font=("Segoe UI", 14))
            diff_btn.pack(side="right", padx=5)
            diff_btn.bind("<Enter>", on_enter)
            diff_btn.bind("<Leave>", on_leave)

        # Name (Pack Left - Fill Remaining)
        name_color = COLORS["text_nested"] if group else COLORS["text_link"]
        
        if name_command:
            # Use Label instead of Button to avoid occupying full width
            lbl = ctk.CTkLabel(row_frame, text=data['name'], anchor="w", 
                             text_color=name_color, font=("Segoe UI", 13, "bold"))
            lbl.pack(side="left", padx=5) # No expand/fill
            
            # Bind events
            lbl.bind("<Enter>", on_enter)
            lbl.bind("<Leave>", on_leave)
            lbl.bind("<Button-1>", lambda e: name_command())
            
            # Add hand cursor to indicate clickable link
            try: lbl.configure(cursor="hand2")
            except: pass
        else:
            lbl = ctk.CTkLabel(row_frame, text=data['name'], anchor="w", font=("Segoe UI", 13, "bold"), text_color=name_color)
            lbl.pack(side="left", padx=5, fill="x", expand=True)
            lbl.bind("<Enter>", on_enter)
            lbl.bind("<Leave>", on_leave)
            lbl.bind("<Button-1>", toggle_check)
            
        self.rows.append({"checkbox": checkbox, "data": data})

    def get_checked_items(self):
        return [row["data"] for row in self.rows if row["checkbox"].get() == 1]
    
    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.rows = []
        self.groups = {}
        
    def set_message(self, message):
        self.clear()
        ctk.CTkLabel(self, text=message, text_color="gray").pack(pady=20)


class DiffViewerDialog(ctk.CTkToplevel):
    def __init__(self, parent, skill_name, source_path, target_path):
        super().__init__(parent)
        self.title(f"差异对比: {skill_name}")
        center_window_relative(self, parent, 1000, 800)
        self.transient(parent)
        self.grab_set()
        self.lift()
        self.focus_force()
        
        self.source_path = source_path
        self.target_path = target_path
        
        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)
        
        # Left: File List
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.lbl_files = ctk.CTkLabel(self.left_frame, text="变动文件", font=("Segoe UI", 14, "bold"))
        self.lbl_files.pack(pady=5)
        
        self.file_list = ctk.CTkScrollableFrame(self.left_frame)
        self.file_list.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Right: Content
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        ctk.CTkLabel(self.right_frame, text="内容对比", font=("Segoe UI", 14, "bold")).pack(pady=5)
        
        self.text_area = ctk.CTkTextbox(self.right_frame, font=("Consolas", 12), wrap="none")
        self.text_area.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.configure_tags()
        self.analyze_files()

    def configure_tags(self):
        try:
            mode = self.text_area._get_appearance_mode()
            text_widget = self.text_area._textbox
            if mode == "light":
                 text_widget.tag_config("diff_add", foreground="#00a000", background="#e6ffec")
                 text_widget.tag_config("diff_remove", foreground="#d00000", background="#ffebe9")
                 text_widget.tag_config("diff_info", foreground="#0000ff")
                 text_widget.tag_config("diff_header_remove", foreground="#d00000")
                 text_widget.tag_config("diff_header_add", foreground="#00a000")
            else:
                 text_widget.tag_config("diff_add", foreground="#4caf50")
                 text_widget.tag_config("diff_remove", foreground="#f44336")
                 text_widget.tag_config("diff_info", foreground="#2196f3")
                 text_widget.tag_config("diff_header_remove", foreground="#f44336")
                 text_widget.tag_config("diff_header_add", foreground="#4caf50")
        except: pass

    def analyze_files(self):
        self.diff_files = []
        
        # Setup ignore function based on source .gitignore
        patterns = get_ignore_patterns(self.source_path)
        ignore_func = shutil.ignore_patterns(*patterns) if patterns else None
        
        def walk_with_ignore(path):
            for root, dirs, files in os.walk(path):
                if ignore_func:
                    ignored = ignore_func(root, dirs + files)
                    dirs[:] = [d for d in dirs if d not in ignored]
                    files[:] = [f for f in files if f not in ignored]
                yield root, dirs, files
        
        for root, _, files in walk_with_ignore(self.source_path):
            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), self.source_path)
                tgt_f = os.path.join(self.target_path, rel_path)
                src_f = os.path.join(self.source_path, rel_path)
                
                if not os.path.exists(tgt_f):
                    self.diff_files.append((rel_path, "New"))
                elif self.is_different(src_f, tgt_f):
                    self.diff_files.append((rel_path, "Modified"))
                    
        for root, _, files in walk_with_ignore(self.target_path):
            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), self.target_path)
                if not os.path.exists(os.path.join(self.source_path, rel_path)):
                     self.diff_files.append((rel_path, "Deleted"))

        self.diff_files.sort(key=lambda x: x[0])
        self.lbl_files.configure(text=f"变动文件 ({len(self.diff_files)})")
        
        for f, status in self.diff_files:
            btn = ctk.CTkButton(self.file_list, text=f"[{status}] {f}", anchor="w", fg_color="transparent", 
                              text_color=COLORS["text_sub"], hover_color=("gray90", "gray20"),
                              command=lambda f=f, s=status: self.show_file_diff(f, s))
            btn.pack(fill="x", pady=1)

    def is_different(self, f1, f2):
        try:
            with open(f1, 'rb') as a, open(f2, 'rb') as b:
                return a.read() != b.read()
        except: return True

    def show_file_diff(self, rel_path, status):
        self.text_area.delete('1.0', 'end')
        self.text_area.insert('end', f"File: {rel_path} ({status})\n\n")
        
        if not is_text_file(rel_path):
            self.text_area.insert('end', "[Binary or unsupported text file diff]\n")
            return

        src_f = os.path.join(self.source_path, rel_path)
        tgt_f = os.path.join(self.target_path, rel_path)
        
        try:
            src_lines = []
            if os.path.exists(src_f):
                with open(src_f, 'r', encoding='utf-8', errors='ignore') as f: src_lines = f.readlines()
            
            tgt_lines = []
            if os.path.exists(tgt_f):
                with open(tgt_f, 'r', encoding='utf-8', errors='ignore') as f: tgt_lines = f.readlines()
            
            diff = difflib.unified_diff(tgt_lines, src_lines, fromfile='Target', tofile='Source')
            
            for line in diff:
                tag = None
                if line.startswith('---'):
                    tag = 'diff_header_remove'
                elif line.startswith('+++'):
                    tag = 'diff_header_add'
                elif line.startswith('@@'):
                    tag = 'diff_info'
                elif line.startswith('+'):
                    tag = 'diff_add'
                elif line.startswith('-'):
                    tag = 'diff_remove'
                
                if tag:
                    self.text_area.insert('end', line, tag)
                else:
                    self.text_area.insert('end', line)
        except Exception as e:
            self.text_area.insert('end', f"Error: {e}\n")


class TextDiffDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, text_source, text_target):
        super().__init__(parent)
        self.title(title)
        center_window_relative(self, parent, 900, 700)
        self.transient(parent)
        self.grab_set()
        self.lift()
        self.focus_force()
        
        self.text_area = ctk.CTkTextbox(self, font=("Consolas", 12), wrap="none")
        self.text_area.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.show_diff(text_source, text_target)

    def show_diff(self, source, target):
        self.configure_tags()
        try:
            src_lines = source.splitlines(keepends=True)
            tgt_lines = target.splitlines(keepends=True)
            diff = difflib.unified_diff(tgt_lines, src_lines, fromfile='Target', tofile='Source')
            for line in diff:
                tag = None
                if line.startswith('---'):
                    tag = 'diff_header_remove'
                elif line.startswith('+++'):
                    tag = 'diff_header_add'
                elif line.startswith('@@'):
                    tag = 'diff_info'
                elif line.startswith('+'):
                    tag = 'diff_add'
                elif line.startswith('-'):
                    tag = 'diff_remove'
                
                if tag:
                    self.text_area.insert('end', line, tag)
                else:
                    self.text_area.insert('end', line)
        except Exception as e:
            self.text_area.insert('end', f"Error: {e}")

    def configure_tags(self):
        try:
            mode = self.text_area._get_appearance_mode()
            text_widget = self.text_area._textbox
            if mode == "light":
                 text_widget.tag_config("diff_add", foreground="#00a000", background="#e6ffec")
                 text_widget.tag_config("diff_remove", foreground="#d00000", background="#ffebe9")
                 text_widget.tag_config("diff_info", foreground="#0000ff")
                 text_widget.tag_config("diff_header_remove", foreground="#d00000")
                 text_widget.tag_config("diff_header_add", foreground="#00a000")
            else:
                 text_widget.tag_config("diff_add", foreground="#4caf50")
                 text_widget.tag_config("diff_remove", foreground="#f44336")
                 text_widget.tag_config("diff_info", foreground="#2196f3")
                 text_widget.tag_config("diff_header_remove", foreground="#f44336")
                 text_widget.tag_config("diff_header_add", foreground="#4caf50")
        except: pass

class DescriptionDialog(ctk.CTkToplevel):
    def __init__(self, parent, title, content):
        super().__init__(parent)
        self.title(title)
        center_window_relative(self, parent, 600, 400)
        self.transient(parent)
        self.grab_set()
        self.lift()
        self.focus_force()
        
        self.textbox = ctk.CTkTextbox(self, wrap="word", font=("Segoe UI", 12))
        self.textbox.pack(fill="both", expand=True, padx=20, pady=20)
        self.textbox.insert("1.0", content)
        self.textbox.configure(state="disabled")

# --- Pages ---

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("设置")
        center_window_relative(self, parent, 600, 350)
        self.transient(parent)
        self.grab_set()
        self.lift()
        self.focus_force()
        
        self.skills_var = tk.StringVar(value=app_config.skills_dir)
        self.mcp_var = tk.StringVar(value=app_config.mcp_settings_file)
        
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="默认 Skills 仓库目录:", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        f1 = ctk.CTkFrame(frame, fg_color="transparent")
        f1.pack(fill="x", pady=(5, 15))
        ctk.CTkEntry(f1, textvariable=self.skills_var).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(f1, text="浏览", width=60, command=self.browse_skills, fg_color=COLORS["primary"]).pack(side="left", padx=(5,0))
        
        ctk.CTkLabel(frame, text="默认 MCP 配置文件:", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        f2 = ctk.CTkFrame(frame, fg_color="transparent")
        f2.pack(fill="x", pady=(5, 15))
        ctk.CTkEntry(f2, textvariable=self.mcp_var).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(f2, text="浏览", width=60, command=self.browse_mcp, fg_color=COLORS["primary"]).pack(side="left", padx=(5,0))
        
        ctk.CTkButton(frame, text="保存设置", command=self.save, fg_color=COLORS["primary"]).pack(side="right", pady=20)
        
    def browse_skills(self):
        path = filedialog.askdirectory(initialdir=self.skills_var.get())
        if path: self.skills_var.set(path)
        
    def browse_mcp(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path: self.mcp_var.set(path)
        
    def save(self):
        app_config.skills_dir = self.skills_var.get()
        app_config.mcp_settings_file = self.mcp_var.get()
        app_config.save()
        self.destroy()

class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        # Icons
        self.icon_skills = load_icon(ICON_FOLDER, size=(24, 24))
        self.icon_mcp = load_icon(ICON_MCP, size=(24, 24))
        self.icon_install = load_icon(ICON_IMPORT, size=(24, 24))
        self.icon_settings = load_icon(ICON_SETTINGS, size=(20, 20))
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=40, pady=30)
        
        ctk.CTkLabel(header, text="Gemini Skills & MCP Manager", font=("Segoe UI", 24, "bold"), text_color=COLORS["primary"]).pack(side="left")
        ctk.CTkButton(header, text="", image=self.icon_settings, width=40, height=40, fg_color="transparent", hover_color=("gray90", "gray20"), command=self.open_settings).pack(side="right")
        
        # Dashboard Cards
        dash_frame = ctk.CTkFrame(self, fg_color="transparent")
        dash_frame.pack(fill="x", padx=40, pady=20)
        
        self.create_dash_card(dash_frame, "Skills 管理", "管理和同步 AI Skills", self.icon_skills, self.on_manage_skills).pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.create_dash_card(dash_frame, "安装 Skills", "从 GitHub 下载 Skills", self.icon_install, self.on_install_skills).pack(side="left", fill="x", expand=True, padx=5)
        self.create_dash_card(dash_frame, "MCP 管理", "管理 MCP 服务器配置", self.icon_mcp, self.on_manage_mcp).pack(side="left", fill="x", expand=True, padx=(5, 0))
        
        # Recent History
        ctk.CTkLabel(self, text="最近使用的项目", font=("Segoe UI", 16, "bold"), anchor="w").pack(fill="x", padx=40, pady=(30, 10))
        
        self.history_frame = ctk.CTkScrollableFrame(self, fg_color=("white", "gray20"), corner_radius=10, height=300)
        self.history_frame.pack(fill="both", expand=True, padx=40, pady=(0, 40))
        
        self.refresh_history()
        
    def create_dash_card(self, parent, title, subtitle, icon, command):
        frame = ctk.CTkFrame(parent, fg_color=("white", "gray20"), corner_radius=10, border_width=1, border_color=("gray90", "gray30"))
        
        def on_click(e): command()
        frame.bind("<Button-1>", on_click)
        
        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.pack(expand=True, fill="both", padx=20, pady=20)
        content.bind("<Button-1>", on_click)
        
        widgets = [frame, content]
        
        if icon:
            lbl_icon = ctk.CTkLabel(content, text="", image=icon)
            lbl_icon.pack(side="left", padx=(0, 15))
            lbl_icon.bind("<Button-1>", on_click)
            widgets.append(lbl_icon)
            
        text_frame = ctk.CTkFrame(content, fg_color="transparent")
        text_frame.pack(side="left", fill="y")
        text_frame.bind("<Button-1>", on_click)
        widgets.append(text_frame)
        
        l1 = ctk.CTkLabel(text_frame, text=title, font=("Segoe UI", 16, "bold"), text_color=COLORS["primary"], anchor="w")
        l1.pack(anchor="w")
        l1.bind("<Button-1>", on_click)
        widgets.append(l1)
        
        l2 = ctk.CTkLabel(text_frame, text=subtitle, font=("Segoe UI", 12), text_color="gray", anchor="w")
        l2.pack(anchor="w")
        l2.bind("<Button-1>", on_click)
        widgets.append(l2)
        
        # Arrow icon
        arrow = ctk.CTkLabel(content, text=">", font=("Segoe UI", 16, "bold"), text_color="gray")
        arrow.pack(side="right")
        arrow.bind("<Button-1>", on_click)
        widgets.append(arrow)

        # Enhanced Hover Logic
        def on_enter(e):
            frame.configure(border_color=COLORS["primary"])
            
        def on_leave(e):
            try:
                x, y = frame.winfo_pointerxy()
                widget_x = frame.winfo_rootx()
                widget_y = frame.winfo_rooty()
                if not (widget_x <= x <= widget_x + frame.winfo_width() and 
                        widget_y <= y <= widget_y + frame.winfo_height()):
                    frame.configure(border_color=("gray90", "gray30"))
            except: pass

        for w in widgets:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
        
        return frame

    def refresh_history(self):
        for widget in self.history_frame.winfo_children(): widget.destroy()
        
        icon_folder = load_icon(ICON_FOLDER, size=(20, 20))
        icon_file = load_icon(ICON_MCP, size=(20, 20))
        icon_del = load_icon(ICON_DELETE, size=(16, 16))
        
        def add_item(path, type_name, icon, command, delete_command):
            row = ctk.CTkFrame(self.history_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            # Content Frame (clickable)
            content_frame = ctk.CTkFrame(row, fg_color="transparent")
            content_frame.pack(side="left", fill="x", expand=True)
            
            # Icon
            lbl_icon = ctk.CTkLabel(content_frame, text="", image=icon)
            lbl_icon.pack(side="left", padx=(0, 10))
            
            # Text Frame
            text_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="x", expand=True)
            
            # Name
            lbl_name = ctk.CTkLabel(text_frame, text=os.path.basename(path), anchor="w", 
                                  font=("Segoe UI", 12, "bold"), text_color=("black", "white"))
            lbl_name.pack(anchor="w")
            
            # Path
            lbl_path = ctk.CTkLabel(text_frame, text=path, anchor="w", 
                                  font=("Segoe UI", 10), text_color="gray")
            lbl_path.pack(anchor="w")

            # Click events
            def on_click(e): command()
            def on_enter(e): 
                row.configure(fg_color=("gray90", "gray25"))
                content_frame.configure(fg_color=("gray90", "gray25"))
            def on_leave(e): 
                row.configure(fg_color="transparent")
                content_frame.configure(fg_color="transparent")

            for w in [row, content_frame, lbl_icon, text_frame, lbl_name, lbl_path]:
                w.bind("<Button-1>", on_click)
                w.bind("<Enter>", on_enter)
                w.bind("<Leave>", on_leave)

            # Delete
            del_btn = ctk.CTkButton(row, text="", image=icon_del, width=30, height=30, fg_color="transparent", hover_color=("mistyrose", "darkred"), command=delete_command)
            del_btn.pack(side="right", padx=5)

        all_items = self.controller.history_manager.get_all_history()
        
        for item in all_items:
            path = item["path"]
            if item["type"] == "skill":
                add_item(path, "Skill", icon_folder, lambda p=path: self.open_skill_path(p), lambda p=path: self.del_skill(p))
            else:
                add_item(path, "MCP", icon_file, lambda p=path: self.open_mcp_path(p), lambda p=path: self.del_mcp(p))
            
        if not all_items:
            ctk.CTkLabel(self.history_frame, text="暂无历史记录", text_color="gray").pack(pady=20)

    def open_settings(self): SettingsDialog(self)
    
    def on_manage_skills(self):
        path = filedialog.askdirectory(title="选择 Skills 目标目录")
        if path: self.controller.show_skills_page(path)

    def on_install_skills(self):
        self.controller.show_install_skills_page()

    def on_manage_mcp(self):
        path = filedialog.askopenfilename(title="选择 settings.json", filetypes=[("JSON", "*.json")])
        if path: self.controller.show_mcp_page(path)
        
    def open_skill_path(self, path):
        if os.path.exists(path): self.controller.show_skills_page(path)
        else: messagebox.showerror("错误", "目录不存在")
        
    def open_mcp_path(self, path):
        if os.path.exists(path): self.controller.show_mcp_page(path)
        else: messagebox.showerror("错误", "文件不存在")
        
    def del_skill(self, path):
        self.controller.history_manager.remove_skills_dir(path)
        self.refresh_history()
        
    def del_mcp(self, path):
        self.controller.history_manager.remove_mcp_file(path)
        self.refresh_history()

class SkillsManagerPage(ctk.CTkFrame):
    def __init__(self, parent, controller, target_dir):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.target_dir = target_dir
        
        # Icons
        self.icon_back = load_icon(ICON_BACK, size=(16, 16))
        self.icon_import = load_icon(ICON_IMPORT, size=(16, 16))
        self.icon_del = load_icon(ICON_DELETE, size=(16, 16))

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(header, text=" 返回", image=self.icon_back, command=controller.show_home, width=80, fg_color="transparent", border_width=1, text_color=("black", "white")).pack(side="left")
        
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", padx=20)
        ctk.CTkLabel(title_box, text="管理 Skills", font=("Segoe UI", 20, "bold"), text_color=COLORS["primary"]).pack(anchor="w")
        ctk.CTkLabel(title_box, text=target_dir, font=("Segoe UI", 12), text_color="gray").pack(anchor="w")

        # Content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Left
        left_card = ctk.CTkFrame(content, fg_color=("white", "gray20"), corner_radius=10)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(left_card, text="📂 当前项目 (本地)", font=("Segoe UI", 14, "bold")).pack(pady=10, padx=10, anchor="w")
        self.left_list = ScrollableCheckBoxFrame(left_card)
        self.left_list.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkButton(left_card, text=" 删除选中", image=self.icon_del, fg_color=COLORS["danger"], hover_color="#800000", command=self.delete_selected).pack(fill="x", padx=10, pady=10)
        
        # Right
        right_card = ctk.CTkFrame(content, fg_color=("white", "gray20"), corner_radius=10)
        right_card.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        right_header = ctk.CTkFrame(right_card, fg_color="transparent")
        right_header.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(right_header, text="☁️ 可用 Skills (源)", font=("Segoe UI", 14, "bold")).pack(side="left")
        
        self.right_list = CompareListFrame(right_card, skills_dir=app_config.skills_dir)
        self.right_list.pack(fill="both", expand=True, padx=10, pady=5)
        self.right_list.add_header([("选择", 4), ("名称", 15), ("状态", 8), ("操作", 5)])
        
        # Add Expand/Collapse buttons
        ctk.CTkButton(right_header, text="全部展开", width=60, height=20, font=("Segoe UI", 10), 
                      fg_color="transparent", border_width=1, text_color="gray", 
                      command=self.right_list.expand_all).pack(side="right", padx=5)
        ctk.CTkButton(right_header, text="全部折叠", width=60, height=20, font=("Segoe UI", 10), 
                      fg_color="transparent", border_width=1, text_color="gray", 
                      command=self.right_list.collapse_all).pack(side="right", padx=5)
        
        ctk.CTkButton(right_card, text=" 导入 / 更新选中", image=self.icon_import, fg_color=COLORS["primary"], command=self.import_selected).pack(fill="x", padx=10, pady=10)
        
        self.after(100, self.refresh_all)

    def refresh_all(self):
        self.controller.show_loading("正在加载 Skills...")
        threading.Thread(target=self._refresh_thread, daemon=True).start()

    def _refresh_thread(self):
        try:
            # Left Data
            target_skills = []
            if os.path.exists(self.target_dir):
                try:
                    target_skills = [i for i in os.listdir(self.target_dir) if os.path.isdir(os.path.join(self.target_dir, i))]
                except: pass
            
            # Right Data
            right_rows = []
            error_msg = None
            
            if not os.path.exists(app_config.skills_dir):
                error_msg = "源目录不存在，请在设置中配置"
            else:
                source_skills = []
                for root, dirs, files in os.walk(app_config.skills_dir):
                    if 'SKILL.md' in files:
                        rel_path = os.path.relpath(root, app_config.skills_dir).replace("\\", "/")
                        source_skills.append(rel_path)
                
                for skill_rel_path in sorted(source_skills):
                    s_path = os.path.join(app_config.skills_dir, skill_rel_path)
                    # Use basename to flatten directory structure in target
                    t_path = os.path.join(self.target_dir, os.path.basename(skill_rel_path))
                    
                    # Determine Group and Display Name
                    parts = skill_rel_path.split("/")
                    if len(parts) > 1:
                        group_name = "/".join(parts[:-1])
                        display_name = parts[-1]
                    else:
                        group_name = None
                        display_name = parts[0]

                    in_target = os.path.exists(t_path)
                    
                    status = "🆕 新增"
                    color = COLORS["success"]
                    is_diff = False
                    
                    if in_target:
                        # Get ignore patterns for hash calculation
                        patterns = get_ignore_patterns(s_path)
                        ignore_func = shutil.ignore_patterns(*patterns) if patterns else None
                        
                        if calculate_dir_hash(s_path, ignore_func) == calculate_dir_hash(t_path, ignore_func):
                            status = "✅ 一致"
                            color = "gray"
                        else:
                            status = "⚠️ 差异"
                            color = COLORS["warning"]
                            is_diff = True
                    
                    right_rows.append({
                        "name": display_name,
                        "rel_path": skill_rel_path,
                        "status": status,
                        "color": color,
                        "is_diff": is_diff,
                        "s_path": s_path,
                        "t_path": t_path,
                        "group": group_name
                    })
            
            self.after(0, lambda: self._update_ui(target_skills, right_rows, error_msg))
            
        except Exception as e:
            self.after(0, lambda: self.controller.hide_loading())
            print(f"Error in refresh thread: {e}")

    def _update_ui(self, target_skills, right_rows, error_msg):
        self.left_list.clear()
        self.right_list.clear()
        
        # Left
        for s in target_skills: self.left_list.add_item(s)
        
        # Right
        if error_msg:
            self.right_list.set_message(error_msg)
        else:
            for row in right_rows:
                diff_cmd = None
                if row["is_diff"]:
                    # Capture variables carefully in lambda
                    diff_cmd = lambda s=row["name"], sp=row["s_path"], tp=row["t_path"]: DiffViewerDialog(self, s, sp, tp)
                
                self.right_list.add_row(
                    {"name": row["name"], "rel_path": row["rel_path"], "status": row["status"]},
                    status_color=row["color"],
                    diff_command=diff_cmd,
                    name_command=lambda s=row["name"], sp=row["s_path"]: DescriptionDialog(self, f"Skill: {s}", get_skill_description(sp)),
                    group=row["group"]
                )
        
        self.controller.hide_loading()

    def delete_selected(self):
        items = self.left_list.get_checked_items()
        if not items: return
        if not messagebox.askyesno("确认", f"删除 {len(items)} 个 Skills？"): return
        for item in items:
            try: shutil.rmtree(os.path.join(self.target_dir, item))
            except Exception as e: print(e)
        self.refresh_all()

    def import_selected(self):
        items = self.right_list.get_checked_items()
        if not items: return
        for item in items:
            skill = item.get('rel_path', item['name'])
            src = os.path.join(app_config.skills_dir, skill)
            # Use basename to flatten directory structure in target
            dst = os.path.join(self.target_dir, os.path.basename(skill))
            try:
                if os.path.exists(dst): shutil.rmtree(dst)
                
                # Check for .gitignore and use it
                ignore_func = None
                patterns = get_ignore_patterns(src)
                if patterns:
                    ignore_func = shutil.ignore_patterns(*patterns)
                    
                shutil.copytree(src, dst, ignore=ignore_func)
            except Exception as e: messagebox.showerror("Error", str(e))
        self.refresh_all()
        show_message(self, "完成", "导入完成")

class MCPManagerPage(ctk.CTkFrame):
    def __init__(self, parent, controller, target_file):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.target_file = target_file
        
        self.icon_back = load_icon(ICON_BACK, size=(16, 16))
        self.icon_import = load_icon(ICON_IMPORT, size=(16, 16))
        self.icon_del = load_icon(ICON_DELETE, size=(16, 16))
        
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(header, text=" 返回", image=self.icon_back, command=controller.show_home, width=80, fg_color="transparent", border_width=1, text_color=("black", "white")).pack(side="left")
        
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", padx=20)
        ctk.CTkLabel(title_box, text="管理 MCP", font=("Segoe UI", 20, "bold"), text_color=COLORS["primary"]).pack(anchor="w")
        ctk.CTkLabel(title_box, text=target_file, font=("Segoe UI", 12), text_color="gray").pack(anchor="w")
        
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        left_card = ctk.CTkFrame(content, fg_color=("white", "gray20"), corner_radius=10)
        left_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ctk.CTkLabel(left_card, text="📂 当前配置 (本地)", font=("Segoe UI", 14, "bold")).pack(pady=10, padx=10, anchor="w")
        self.left_list = ScrollableCheckBoxFrame(left_card)
        self.left_list.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkButton(left_card, text=" 删除选中", image=self.icon_del, fg_color=COLORS["danger"], hover_color="#800000", command=self.delete_selected).pack(fill="x", padx=10, pady=10)
        
        right_card = ctk.CTkFrame(content, fg_color=("white", "gray20"), corner_radius=10)
        right_card.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        ctk.CTkLabel(right_card, text="☁️ 可用配置 (源)", font=("Segoe UI", 14, "bold")).pack(pady=10, padx=10, anchor="w")
        self.right_list = CompareListFrame(right_card)
        self.right_list.pack(fill="both", expand=True, padx=10, pady=5)
        self.right_list.add_header([("选择", 4), ("MCP ID", 15), ("状态", 8), ("操作", 5)])
        
        ctk.CTkButton(right_card, text=" 导入 / 更新选中", image=self.icon_import, fg_color=COLORS["primary"], command=self.import_selected).pack(fill="x", padx=10, pady=10)
        
        self.after(100, self.refresh_all)

    def refresh_all(self):
        self.controller.show_loading("正在加载 MCP 配置...")
        threading.Thread(target=self._refresh_thread, daemon=True).start()

    def _refresh_thread(self):
        try:
            current_data = {}
            left_items = []
            
            if os.path.exists(self.target_file):
                try:
                    current_data = load_jsonc(self.target_file)
                    left_items = sorted(current_data.get('mcpServers', {}).keys())
                except: pass
            
            right_rows = []
            error_msg = None
            
            if not os.path.exists(app_config.mcp_settings_file):
                error_msg = "源配置文件不存在"
            else:
                try:
                    source_data = load_jsonc(app_config.mcp_settings_file).get('mcpServers', {})
                    target_servers = current_data.get('mcpServers', {})
                    
                    for key in sorted(source_data.keys()):
                        in_target = key in target_servers
                        status = "🆕 新增"
                        color = COLORS["success"]
                        is_diff = False
                        
                        if in_target:
                            if source_data[key] == target_servers[key]:
                                status = "✅ 一致"
                                color = "gray"
                            else:
                                status = "⚠️ 差异"
                                color = COLORS["warning"]
                                is_diff = True
                        
                        right_rows.append({
                            "key": key,
                            "status": status,
                            "color": color,
                            "is_diff": is_diff,
                            "source_val": source_data[key],
                            "target_val": target_servers.get(key, {})
                        })
                except Exception as e:
                    error_msg = f"Error: {e}"
            
            self.after(0, lambda: self._update_ui(current_data, left_items, right_rows, error_msg))
            
        except Exception as e:
             self.after(0, lambda: self.controller.hide_loading())
             print(f"Error in refresh thread: {e}")

    def _update_ui(self, current_data, left_items, right_rows, error_msg):
        self.current_data = current_data
        self.left_list.clear()
        self.right_list.clear()
        
        for k in left_items: self.left_list.add_item(k)
        
        if error_msg:
             self.right_list.set_message(error_msg)
        else:
             for row in right_rows:
                diff_cmd = None
                if row["is_diff"]:
                    diff_cmd = lambda k=row["key"], s=row["source_val"], t=row["target_val"]: \
                        TextDiffDialog(self, f"Diff: {k}", json.dumps(s, indent=2), json.dumps(t, indent=2))
                
                self.right_list.add_row(
                    {"name": row["key"], "status": row["status"]},
                    status_color=row["color"],
                    diff_command=diff_cmd,
                    name_command=lambda k=row["key"], v=row["source_val"]: DescriptionDialog(self, k, json.dumps(v, indent=2))
                )
        
        self.controller.hide_loading()

    def delete_selected(self):
        items = self.left_list.get_checked_items()
        if not items: return
        if not messagebox.askyesno("Confirm", "Delete selected?"): return
        servers = self.current_data.get('mcpServers', {})
        for i in items:
            if i in servers: del servers[i]
        self.current_data['mcpServers'] = servers
        self.save_target()
        self.refresh_all()
        
    def import_selected(self):
        items = self.right_list.get_checked_items()
        if not items: return
        source_data = load_jsonc(app_config.mcp_settings_file).get('mcpServers', {})
        if 'mcpServers' not in self.current_data: self.current_data['mcpServers'] = {}
        for item in items:
            key = item['name']
            if key in source_data: self.current_data['mcpServers'][key] = source_data[key]
        self.save_target()
        self.refresh_all()
        show_message(self, "Done", "Imported.")

    def save_target(self):
        with open(self.target_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_data, f, indent=2, ensure_ascii=False)

class InstallSkillsPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        
        self.icon_back = load_icon(ICON_BACK, size=(16, 16))
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        ctk.CTkButton(header, text=" 返回", image=self.icon_back, command=controller.show_home, width=80, fg_color="transparent", border_width=1, text_color=("black", "white")).pack(side="left")
        ctk.CTkLabel(header, text="安装 Skills", font=("Segoe UI", 20, "bold"), text_color=COLORS["primary"]).pack(side="left", padx=20)

        # Content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Input Area
        input_frame = ctk.CTkFrame(content, fg_color=("white", "gray20"), corner_radius=10)
        input_frame.pack(fill="x", pady=(0, 10))
        
        # URL
        ctk.CTkLabel(input_frame, text="GitHub 目录链接:", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=20, pady=(20, 5))
        self.url_entry = ctk.CTkEntry(input_frame, placeholder_text="例如: https://github.com/langgenius/dify/tree/main/.agents/skills")
        self.url_entry.pack(fill="x", padx=20, pady=(0, 15))
        
        # Target Dir
        ctk.CTkLabel(input_frame, text="安装目标目录:", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=20, pady=(5, 5))
        dir_box = ctk.CTkFrame(input_frame, fg_color="transparent")
        dir_box.pack(fill="x", padx=20, pady=(0, 20))
        
        self.target_var = tk.StringVar(value=app_config.skills_dir)
        ctk.CTkEntry(dir_box, textvariable=self.target_var).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(dir_box, text="浏览", width=60, command=self.browse_target, fg_color=COLORS["primary"]).pack(side="left", padx=(5,0))
        
        # Action
        self.btn_install = ctk.CTkButton(input_frame, text="开始安装", command=self.start_install, fg_color=COLORS["primary"], height=40, font=("Segoe UI", 14, "bold"))
        self.btn_install.pack(fill="x", padx=20, pady=(0, 20))

        # Logs
        log_frame = ctk.CTkFrame(content, fg_color=("white", "gray20"), corner_radius=10)
        log_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(log_frame, text="安装进度", font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 5))
        
        self.log_area = ctk.CTkScrollableFrame(log_frame, fg_color="transparent")
        self.log_area.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
    def browse_target(self):
        path = filedialog.askdirectory(initialdir=self.target_var.get())
        if path: self.target_var.set(path)
        
    def log(self, text, type="info"):
        self.after(0, lambda: self._add_log_item(text, type))
        
    def _add_log_item(self, text, type):
        row = ctk.CTkFrame(self.log_area, fg_color="transparent")
        row.pack(fill="x", pady=0) # Compact packing
        
        color = None # Default color (usually black/white depending on mode)
        icon = ""
        if type == "error": color = COLORS["danger"]; icon = "❌ "
        elif type == "success": color = COLORS["success"]; icon = "✅ "
        elif type == "dir": color = COLORS["primary"]; icon = "📁 "
        elif type == "file_start": icon = "⬇️ "
        
        # If color is explicitly set to None, don't pass text_color arg to let CTk handle it
        kwargs = {"text": icon + text, "anchor": "w", "font": ("Consolas", 12)}
        if color:
            kwargs["text_color"] = color
            
        ctk.CTkLabel(row, **kwargs).pack(fill="x")
        
        self.update_idletasks()
        try:
            self.log_area._parent_canvas.yview_moveto(1.0)
        except: pass

    def start_install(self):
        if hasattr(self, "is_installing") and self.is_installing:
            # Stop logic
            if self.downloader:
                self.downloader.stop_flag = True
                self.log("正在停止下载...", "warning")
                self.btn_install.configure(state="disabled", text="正在停止...")
            return

        url = self.url_entry.get().strip()
        target = self.target_var.get().strip()
        
        if not url: return messagebox.showerror("错误", "请输入 GitHub 链接")
        if not target: return messagebox.showerror("错误", "请选择目标目录")
        
        # Pre-check for duplicate directory
        try:
            parts = url.strip("/").split("/")
            if "github.com" in parts:
                owner = parts[3]
                folder_path = "/".join(parts[7:])
                skill_name = folder_path.split("/")[-1]
                
                final_output_dir = os.path.join(target, owner, skill_name)
                
                if os.path.exists(final_output_dir):
                    if not messagebox.askyesno("确认覆盖", f"目标目录已存在，是否覆盖？\n\n{final_output_dir}"):
                        return
        except: pass # Let downloader handle parsing errors
        
        if not os.path.exists(target):
            try: os.makedirs(target)
            except Exception as e: return messagebox.showerror("错误", f"无法创建目录: {e}")
            
        self.is_installing = True
        self.btn_install.configure(state="normal", text="停止安装", fg_color=COLORS["warning"], hover_color="#b33000")
        
        for widget in self.log_area.winfo_children(): widget.destroy()
        
        threading.Thread(target=self._run_install, args=(url, target), daemon=True).start()
        
    def _run_install(self, url, target):
        self.downloader = GitHubDownloader(self.log)
        success = self.downloader.download(url, target)
        self.is_installing = False
        self.downloader = None
        
        if success:
            self.after(0, lambda: self._install_finished("success"))
        else:
            self.after(0, lambda: self._install_finished("error"))

    def _install_finished(self, status):
        if status == "success":
            self.btn_install.configure(state="normal", text="已安装", fg_color=COLORS["primary"])
        else:
            self.btn_install.configure(state="normal", text="重试安装", fg_color=COLORS["primary"])

class LoadingOverlay(ctk.CTkToplevel):
    def __init__(self, master, message="正在加载..."):
        super().__init__(master)
        
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.transient(master)
        
        # Use solid colors, slight alpha for overlay effect
        self.configure(fg_color=("gray95", "gray10")) 
        self.attributes('-alpha', 0.9)
        
        self.center_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self.spinner = ctk.CTkProgressBar(self.center_frame, width=200, mode="indeterminate")
        self.spinner.pack(pady=20)
        self.spinner.start()
        
        self.label = ctk.CTkLabel(self.center_frame, text=message, font=("Segoe UI", 16))
        self.label.pack()

    def set_message(self, text):
        self.label.configure(text=text)

class SkillsManagerAppV3(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Gemini Skills & MCP Manager")
        center_window(self, 1000, 750)
        
        self.history_manager = HistoryManager()
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        self.current_frame = None
        self.loading_overlay = None
        
        self.show_home()
        
    def show_loading(self, message="正在加载..."):
        if self.loading_overlay:
            self.loading_overlay.destroy()
        
        self.loading_overlay = LoadingOverlay(self, message)
        
        # Position the overlay to cover the main window
        self.update_idletasks()
        x = self.winfo_rootx()
        y = self.winfo_rooty()
        w = self.winfo_width()
        h = self.winfo_height()
        self.loading_overlay.geometry(f"{w}x{h}+{x}+{y}")
        
        self.loading_overlay.lift()
        self.update() 

    def hide_loading(self):
        if self.loading_overlay:
            self.loading_overlay.destroy()
            self.loading_overlay = None

    def show_home(self): self._switch(HomePage(self.container, self))
    
    def show_install_skills_page(self):
        self._switch(InstallSkillsPage(self.container, self))

    def show_skills_page(self, path):
        self.history_manager.add_skills_dir(path)
        # Defer loading to the page itself
        self._switch(SkillsManagerPage(self.container, self, path))
        
    def show_mcp_page(self, path):
        self.history_manager.add_mcp_file(path)
        self._switch(MCPManagerPage(self.container, self, path))
        
    def _switch(self, frame):
        if self.current_frame: self.current_frame.destroy()
        self.current_frame = frame
        self.current_frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = SkillsManagerAppV3()
    app.mainloop()
