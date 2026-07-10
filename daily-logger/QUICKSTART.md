# 🚀 快速上手指南

## 1️⃣ 添加你的第一条记录

```bash
# 进入工具目录
cd daily-logger

# 添加一条简单的记录
./log add "完成了今天的第一个任务"
```

## 2️⃣ 带分类记录

```bash
# 记录工作相关
./log add "完成了项目报告" -c 工作

# 记录学习相关
./log add "学习了 Python 编程" -c 学习

# 记录生活相关
./log add "整理了房间" -c 生活
```

## 3️⃣ 带标签和时长记录

```bash
# 添加标签和时长
./log add "写周报" -c 工作 -t 周报,汇报 -d 30

# 多个标签
./log add "团队会议" -c 工作 -t 会议,项目讨论 -d 60
```

## 4️⃣ 查看记录

```bash
# 查看所有记录
./log list

# 查看最近 7 天
./log list -d 7

# 查看某个分类
./log list -c 工作
```

## 5️⃣ 查看统计

```bash
# 查看今日总结
./log today

# 查看总体统计
./log stats

# 查看本周统计
./log stats -d 7
```

## 6️⃣ 搜索记录

```bash
# 搜索关键词
./log search "项目"
./log search "学习"
```

## 7️⃣ 导出数据

```bash
# 导出为 JSON 文件
./log export json backup.json

# 导出为 CSV 文件（可以用 Excel 打开）
./log export csv backup.csv
```

## 💡 日常使用建议

### 每天早上
```bash
# 开始新的一天
./log add "开始新的一天" -c 生活 -t 日常
```

### 工作时
```bash
# 每完成一个任务就记录
./log add "完成了 XXX 功能开发" -c 工作 -t 开发 -d 120
```

### 学习时
```bash
# 记录学习内容
./log add "学习了 XXX 技术" -c 学习 -t 技术 -d 60
```

### 晚上回顾
```bash
# 查看今日总结
./log today

# 回顾本周
./log stats -d 7
```

## 📊 常用命令速查

| 命令 | 说明 |
|------|------|
| `./log add "内容"` | 添加记录 |
| `./log list` | 查看记录 |
| `./log today` | 今日总结 |
| `./log stats` | 统计信息 |
| `./log search "关键词"` | 搜索记录 |
| `./log categories` | 查看分类 |
| `./log export json file.json` | 导出数据 |

## 🎯 小技巧

1. **坚持记录**：每天记录 3-5 条，坚持一周就会养成习惯
2. **使用分类**：合理分类能帮你更好地分析时间分配
3. **添加时长**：记录时长可以帮你了解时间都花在哪里了
4. **定期回顾**：每周用 `./log stats -d 7` 回顾一下
5. **导出备份**：定期导出数据备份

---

开始记录吧！📝
