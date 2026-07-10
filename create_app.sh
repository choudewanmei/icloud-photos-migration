#!/bin/bash

# 创建 Automator 应用
echo "创建 macOS 应用..."

# 使用 osascript 创建应用
osascript <<'APPLESCRIPT'
tell application "Automator"
    activate
end tell

set appPath to (path to desktop as text) & "iCloud照片迁移助手.app"

tell application "Finder"
    if exists file appPath then
        delete file appPath
    end if
end tell

tell application "Automator"
    set newDoc to make new document with properties {workflow type:application}
end tell

tell application "System Events"
    tell process "Automator"
        -- 等待 Automator 打开
        delay 2
        
        -- 获取窗口
        set frontWindow to front window
        
        -- 添加"运行 Shell 脚本"动作
        keystroke "f" using {command down, shift down}
        delay 1
        keystroke "运行 Shell 脚本"
        delay 1
        keystroke return
        delay 1
        
        -- 输入脚本
        keystroke "cd /Users/louise/Documents/iCloud照片迁移助手 && python3 main.py"
        delay 1
        
        -- 保存应用
        keystroke "s" using {command down}
        delay 1
        keystroke "iCloud照片迁移助手"
        delay 1
        keystroke return
        delay 1
    end tell
end tell
APPLESCRIPT

echo "✅ 应用创建完成"
