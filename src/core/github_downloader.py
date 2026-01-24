import os

import requests


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
            owner = parts[3]
            repo = parts[4]
            branch = parts[6]
            folder_path = "/".join(parts[7:])
            skill_name = folder_path.split("/")[-1]
        except IndexError:
            self.log_callback("错误: URL 格式解析失败，请确保包含 tree/{branch}/目录路径", "error")
            return False

        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{folder_path}?ref={branch}"
        base_dest_dir = os.path.join(output_dir, owner)

        try:
            self.log_callback(f"正在分析目录结构: {owner}/{repo}/{folder_path}", "info")
            self._smart_download(api_url, base_dest_dir, is_root=True, root_name=skill_name)
            self._record_address(base_dest_dir, github_url)
            self.log_callback("所有下载任务完成！", "success")
            return True
        except Exception as e:
            self.log_callback(f"下载过程出错: {e}", "error")
            return False

    def _smart_download(self, api_url, base_dest_dir, is_root=False, root_name=None):
        self._smart_download_recursive(api_url, base_dest_dir, current_dir_name=root_name)

    def _smart_download_recursive(self, api_url, base_dest_dir, current_dir_name=None):
        if self.stop_flag:
            return

        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(api_url, headers=headers)
            if response.status_code != 200:
                self.log_callback(f"Error fetching {api_url}", "error")
                return

            items = response.json()
            if isinstance(items, dict) and items.get("type") == "file":
                items = [items]

            has_skill_md = any(item["name"].lower() == "skill.md" for item in items)

            if has_skill_md:
                if not current_dir_name:
                    self.log_callback("Error: Skill found but name unknown", "error")
                    return

                target_path = os.path.join(base_dest_dir, current_dir_name)
                self.log_callback(f"发现 Skill: {current_dir_name}", "success")
                self.log_callback(f"目标路径: {target_path}", "info")

                if not os.path.exists(target_path):
                    os.makedirs(target_path)

                self._download_items(items, target_path)
                return

            for item in items:
                if self.stop_flag:
                    return
                if item["type"] == "dir":
                    self._smart_download_recursive(item["url"], base_dest_dir, item["name"])

        except Exception as e:
            self.log_callback(f"Error: {e}", "error")

    def _download_items(self, items, local_path):
        headers = {"User-Agent": "Mozilla/5.0"}
        for item in items:
            if self.stop_flag:
                return

            name = item["name"]
            path = os.path.join(local_path, name)

            if item["type"] == "dir":
                if not os.path.exists(path):
                    os.makedirs(path)
                self._download_recursive(item["url"], path, "")
            else:
                self.log_callback(f"⬇️  正在下载: {name}...", "file_start")
                resp = requests.get(item["download_url"], headers=headers)
                with open(path, "wb") as f:
                    f.write(resp.content)
                self.log_callback(f"下载完成: {name}", "success")

    def _record_address(self, owner_dir, url):
        try:
            if not os.path.exists(owner_dir):
                os.makedirs(owner_dir)
            file_path = os.path.join(owner_dir, "github_address.txt")
            existing_urls = []

            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    existing_urls = [line.strip() for line in f.readlines() if line.strip()]

            url = url.rstrip("/")

            def is_parent_of(parent, child):
                return child.startswith(parent + "/")

            def get_parent_url(u):
                return u.rsplit("/", 1)[0]

            is_covered = False
            for ex in existing_urls:
                if ex == url or is_parent_of(ex, url):
                    is_covered = True
                    break

            if is_covered:
                self.log_callback("地址已存在或被父级包含，跳过记录。", "info")
                return

            current_urls = existing_urls + [url]

            has_changed = True
            while has_changed:
                has_changed = False
                temp_list = sorted(list(set(current_urls)))

                parents = set()
                for u in temp_list:
                    is_child = False
                    for other in temp_list:
                        if u != other and is_parent_of(other, u):
                            is_child = True
                            break
                    if not is_child:
                        parents.add(u)

                groups = {}
                for u in parents:
                    p_url = get_parent_url(u)
                    groups.setdefault(p_url, []).append(u)

                final_round_urls = []
                for p_url, children in groups.items():
                    if len(children) > 1:
                        final_round_urls.append(p_url)
                        has_changed = True
                    else:
                        final_round_urls.append(children[0])

                if has_changed:
                    current_urls = final_round_urls
                else:
                    current_urls = list(parents)

            current_urls.sort()
            existing_urls.sort()

            if current_urls != existing_urls:
                with open(file_path, "w", encoding="utf-8") as f:
                    for u in current_urls:
                        f.write(u + "\n")
                self.log_callback(f"地址记录已更新 (已合并/去重): {file_path}", "info")
            else:
                self.log_callback("地址记录无需更新。", "info")

        except Exception as e:
            self.log_callback(f"无法写入地址文件: {e}", "error")

    def _download_recursive(self, api_url, local_base_path, relative_path):
        if self.stop_flag:
            return

        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(api_url, headers=headers)
        if response.status_code != 200:
            self.log_callback(
                f"获取目录信息失败: {api_url} (代码: {response.status_code})",
                "error",
            )
            return

        data = response.json()
        if isinstance(data, dict) and data.get("type") == "file":
            data = [data]

        for item in data:
            if self.stop_flag:
                return

            item_type = item["type"]
            item_name = item["name"]
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

