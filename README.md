# Gemini Skills & MCP Manager

## 简介
这是一个专为 Gemini 和 AI 开发者设计的图形化管理工具，旨在简化 Skills 目录和 MCP (Model Context Protocol) 配置文件的管理与同步工作。通过直观的 GUI 界面，您可以轻松地在本地项目和源仓库之间对比、导入和更新配置。

## 主要功能

*   **Skills 管理**：
    *   可视化浏览本地和源 Skills 目录。
    *   状态监测：自动检测“新增”、“一致”或“有差异”的 Skill。
    *   差异对比：内置 Diff 查看器，详细展示文件变更。
    *   批量操作：支持批量导入、更新和删除 Skills。
*   **MCP 管理**：
    *   解析并管理 MCP `settings.json` 配置文件。
    *   服务器维度的配置对比与同步。
    *   JSON 格式化预览。
*   **用户体验**：
    *   **历史记录**：自动记录最近打开的路径，按时间排序，支持一键快速访问。
    *   **异步加载**：耗时操作后台执行，配合加载遮罩，界面流畅不卡顿。
    *   **现代化 UI**：基于 CustomTkinter 构建，支持明/暗主题自适应。

## 环境依赖

*   操作系统：Windows 10 / 11 (推荐)
*   Python 版本：Python 3.8 或更高版本

## 安装与启动

1.  **准备环境**
    确保您的电脑已安装 Python。可以在终端输入 `python --version` 检查。

2.  **下载项目**
    下载本发布包并解压到任意目录。

3.  **安装依赖**
    在解压后的目录中打开终端（CMD 或 PowerShell），运行以下命令安装必要的库：
    ```bash
    pip install -r requirements.txt
    ```
    *(如果下载速度慢，可使用国内镜像源：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`)*

4.  **启动应用**
    *   **方式一（推荐）**：直接双击运行目录下的 `run.bat` 文件。
    *   **方式二**：在终端中运行 `python skills_manager.py`。

## 使用手册

### 1. 初始化设置
首次启动后，建议先进行全局配置：
1.  点击主界面右上角的 **⚙️ 设置** 图标。
2.  **默认 Skills 仓库目录**：指向您存放所有原始 Skills 的公共/共享仓库目录。
3.  **默认 MCP 配置文件**：指向包含标准 MCP 服务器配置的源 `settings.json` 文件。
4.  点击保存。

### 2. 管理 Skills
1.  在首页点击 **📂 Skills 管理** 卡片。
2.  选择您当前项目的 Skills 目录（通常是项目根目录下的 `skills` 文件夹）。
3.  **界面说明**：
    *   **左侧列表**：当前项目已有的 Skills。
    *   **右侧列表**：源仓库中可用的 Skills。
4.  **操作**：
    *   右侧列表会用颜色标记状态（绿色=新增，灰色=一致，橙色=有差异）。
    *   点击“⚠️ 差异”按钮可查看具体代码变动。
    *   勾选右侧需要的 Skills，点击底部的 **导入 / 更新选中** 按钮即可同步到本地。

### 3. 管理 MCP 配置
1.  在首页点击 **🔌 MCP 管理** 卡片。
2.  选择您当前需要配置的 `settings.json` 文件（通常位于 `%APPDATA%\Code\User\globalStorage\rooveterinaryinc.roo-cline\settings\cline_mcp_settings.json` 或类似位置）。
3.  **操作**：
    *   逻辑与 Skills 管理类似，支持对比 JSON 配置差异并同步。

## 常见问题

*   **Q: 启动时报错 `ModuleNotFoundError`？**
    *   A: 请检查是否已成功执行 `pip install -r requirements.txt`。
*   **Q: 界面显示乱码？**
    *   A: 本工具默认使用 UTF-8 编码，请确保您的系统语言设置支持中文，且相关文件也是 UTF-8 编码。

---
*版本：v4.0 (Release)*
