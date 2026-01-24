@echo off
:: 切换到工作目录
cd /d "E:\leo-github\skills-mcp-manager-gui"

:: 使用 start 命令启动 pythonw (无窗口模式)
:: 第一个空引号 "" 是必须的，代表窗口标题为空
:: 这样启动后，pythonw 会作为独立进程运行
start "" ".venv\Scripts\pythonw.exe" backup/skills_manager.py

:: 退出当前的 cmd 窗口
exit