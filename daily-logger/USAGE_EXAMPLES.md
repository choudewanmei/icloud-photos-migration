# 📚 使用示例大全

## 场景 1: 工作日记录

### 早上开始工作
```bash
./log add "开始工作，查看邮件" -c 工作 -t 日常 -d 15
```

### 完成任务
```bash
./log add "完成了用户登录功能开发" -c 工作 -t 开发,功能 -d 120
./log add "修复了支付模块的 bug" -c 工作 -t bug修复 -d 60
```

### 会议
```bash
./log add "项目进度会议" -c 工作 -t 会议 -d 45
```

### 下班前回顾
```bash
./log today
```

## 场景 2: 学习记录

### 学习新技能
```bash
./log add "学习 Python 爬虫技术" -c 学习 -t Python,爬虫 -d 90
./log add "阅读《深入理解计算机系统》第3章" -c 学习 -t 阅读,计算机 -d 60
```

### 在线课程
```bash
./log add "完成了 Coursera 机器学习课程第5周" -c 学习 -t 在线课程,机器学习 -d 120
```

### 技术博客
```bash
./log add "写了一篇关于 Docker 的技术博客" -c 创作 -t 博客,Docker -d 90
```

## 场景 3: 生活记录

### 运动健身
```bash
./log add "晨跑 5 公里" -c 运动 -t 跑步 -d 30
./log add "健身房力量训练" -c 运动 -t 健身 -d 60
```

### 家务
```bash
./log add "打扫房间" -c 生活 -t 家务 -d 45
./log add "做饭 - 红烧排骨" -c 生活 -t 做饭 -d 60
```

### 社交活动
```bash
./log add "和朋友聚餐" -c 社交 -t 聚餐 -d 120
./log add "参加技术沙龙" -c 社交 -t 技术交流 -d 180
```

## 场景 4: 项目管理

### 项目阶段记录
```bash
# 需求分析阶段
./log add "完成需求文档编写" -c 工作 -t 项目A,需求 -d 180

# 设计阶段
./log add "完成数据库设计" -c 工作 -t 项目A,设计 -d 120

# 开发阶段
./log add "完成用户模块开发" -c 工作 -t 项目A,开发 -d 240

# 测试阶段
./log add "完成单元测试编写" -c 工作 -t 项目A,测试 -d 120
```

## 场景 5: 个人成长

### 阅读
```bash
./log add "阅读《原则》第一部分" -c 学习 -t 阅读,商业 -d 60
./log add "阅读《人类简史》" -c 学习 -t 阅读,历史 -d 90
```

### 技能提升
```bash
./log add "练习英语听力" -c 学习 -t 英语 -d 30
./log add "学习演讲技巧" -c 学习 -t 软技能 -d 45
```

## 📊 数据分析示例

### 查看本周时间分配
```bash
./log stats -d 7
```

### 查看某个项目的时间投入
```bash
./log search "项目A"
```

### 查看学习时间占比
```bash
./log list -c 学习 -d 30
```

### 导出月度报告
```bash
./log export csv 月度报告.csv -d 30
```

## 🎯 高效使用技巧

### 1. 建立记录习惯
- 每完成一个任务就记录，不要等到一天结束
- 使用手机备忘录临时记录，晚上统一录入

### 2. 合理分类
- 保持分类简洁，不要超过 8 个
- 可以根据个人需求调整分类

### 3. 标签的妙用
- 用标签标记项目：`-t 项目A`
- 用标签标记类型：`-t 会议,讨论`
- 用标签标记优先级：`-t 紧急,重要`

### 4. 时长记录
- 记录实际花费的时间，而不是预估
- 可以用番茄钟来辅助计时

### 5. 定期回顾
- 每天：`./log today`
- 每周：`./log stats -d 7`
- 每月：`./log stats -d 30`

## 📈 进阶用法

### 批量添加（使用 shell 脚本）
```bash
#!/bin/bash
# batch_add.sh

records=(
    "完成需求分析|工作|需求,项目|120"
    "编写技术方案|工作|设计,项目|90"
    "代码评审|工作|评审|60"
)

for record in "${records[@]}"; do
    IFS='|' read -r content category tags duration <<< "$record"
    ./log add "$content" -c "$category" -t "$tags" -d "$duration"
done
```

### 定期备份脚本
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d)
./log export json "backup_${DATE}.json"
./log export csv "backup_${DATE}.csv"
```

---

💡 **记住**：工具的价值在于持续使用。从今天开始记录吧！
