#!/usr/bin/env python3
"""
增强版每日记录工具
支持：记录活动、分类管理、统计分析、数据导出、时间追踪
"""

import sqlite3
import argparse
import sys
import json
import csv
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from collections import defaultdict

class EnhancedDailyLogger:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path.cwd() / "daily_logger.db"
        self.db_path = Path(db_path)
        self.init_db()
    
    def init_db(self):
        """初始化数据库，创建所有必要的表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 主记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                content TEXT NOT NULL,
                category TEXT,
                tags TEXT,
                duration_minutes INTEGER,
                priority INTEGER DEFAULT 0,
                date DATE DEFAULT (date('now'))
            )
        ''')
        
        # 分类表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                color TEXT,
                icon TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 标签表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 插入默认分类
        default_categories = [
            ('工作', '#FF6B6B', '💼'),
            ('学习', '#4ECDC4', '📚'),
            ('生活', '#45B7D1', '🏠'),
            ('运动', '#96CEB4', '🏃'),
            ('娱乐', '#FFEAA7', '🎮'),
            ('社交', '#DDA0DD', '👥'),
            ('创作', '#98D8C8', '🎨'),
            ('其他', '#95A5A6', '📌')
        ]
        
        for name, color, icon in default_categories:
            cursor.execute(
                'INSERT OR IGNORE INTO categories (name, color, icon) VALUES (?, ?, ?)',
                (name, color, icon)
            )
        
        conn.commit()
        conn.close()
    
    def add_entry(self, content, category=None, tags=None, duration=None, priority=0):
        """添加新记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 处理标签
        tags_str = ','.join(tags) if tags else None
        
        # 确保分类存在
        if category:
            cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))
        
        # 确保标签存在
        if tags:
            for tag in tags:
                cursor.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (tag,))
        
        cursor.execute('''
            INSERT INTO daily_log (content, category, tags, duration_minutes, priority, date)
            VALUES (?, ?, ?, ?, ?, date('now'))
        ''', (content, category, tags_str, duration, priority))
        
        entry_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return entry_id
    
    def get_entries(self, days=None, category=None, tag=None, limit=50):
        """获取记录列表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT id, timestamp, content, category, tags, duration_minutes, priority, date
            FROM daily_log WHERE 1=1
        '''
        params = []
        
        if days:
            query += " AND date >= date('now', ?)"
            params.append(f"-{days} days")
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if tag:
            query += " AND tags LIKE ?"
            params.append(f'%{tag}%')
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        entries = []
        for row in cursor.fetchall():
            entries.append({
                'id': row[0],
                'timestamp': row[1],
                'content': row[2],
                'category': row[3],
                'tags': row[4].split(',') if row[4] else [],
                'duration': row[5],
                'priority': row[6],
                'date': row[7]
            })
        
        conn.close()
        return entries
    
    def get_categories(self):
        """获取所有分类"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, color, icon FROM categories ORDER BY name")
        categories = [{'name': row[0], 'color': row[1], 'icon': row[2]} for row in cursor.fetchall()]
        conn.close()
        return categories
    
    def get_stats(self, days=None):
        """获取详细统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 基础条件
        date_filter = ""
        params = []
        if days:
            date_filter = " AND date >= date('now', ?)"
            params = [f"-{days} days"]
        
        # 总记录数
        cursor.execute(f"SELECT COUNT(*) FROM daily_log WHERE 1=1{date_filter}", params)
        total = cursor.fetchone()[0]
        
        # 总时长
        cursor.execute(f"SELECT SUM(duration_minutes) FROM daily_log WHERE 1=1{date_filter}", params)
        total_duration = cursor.fetchone()[0] or 0
        
        # 按分类统计
        cursor.execute(f'''
            SELECT category, COUNT(*) as count, SUM(duration_minutes) as duration
            FROM daily_log 
            WHERE category IS NOT NULL{date_filter}
            GROUP BY category 
            ORDER BY count DESC
        ''', params)
        category_stats = [{'name': row[0], 'count': row[1], 'duration': row[2] or 0} 
                         for row in cursor.fetchall()]
        
        # 最近7天每天的记录数
        cursor.execute('''
            SELECT date, COUNT(*) as count, SUM(duration_minutes) as duration
            FROM daily_log 
            WHERE date >= date('now', '-7 days')
            GROUP BY date 
            ORDER BY date DESC
        ''')
        daily_stats = [{'date': row[0], 'count': row[1], 'duration': row[2] or 0} 
                      for row in cursor.fetchall()]
        
        # 本周统计
        cursor.execute('''
            SELECT COUNT(*) FROM daily_log 
            WHERE date >= date('now', 'weekday 0', '-7 days')
        ''')
        this_week = cursor.fetchone()[0]
        
        # 本月统计
        cursor.execute('''
            SELECT COUNT(*) FROM daily_log 
            WHERE date >= date('now', 'start of month')
        ''')
        this_month = cursor.fetchone()[0]
        
        # 热门标签
        cursor.execute(f'''
            SELECT tags, COUNT(*) as count 
            FROM daily_log 
            WHERE tags IS NOT NULL{date_filter}
            GROUP BY tags
            ORDER BY count DESC
            LIMIT 10
        ''', params)
        tag_stats = []
        for row in cursor.fetchall():
            for tag in row[0].split(','):
                if tag:
                    tag_stats.append({'tag': tag, 'count': row[1]})
        
        conn.close()
        
        return {
            'total': total,
            'total_duration': total_duration,
            'category_stats': category_stats,
            'daily_stats': daily_stats,
            'this_week': this_week,
            'this_month': this_month,
            'tag_stats': tag_stats[:10]
        }
    
    def delete_entry(self, entry_id):
        """删除记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM daily_log WHERE id = ?", (entry_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
    
    def search_entries(self, keyword):
        """搜索记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, timestamp, content, category, tags, duration_minutes, priority, date
            FROM daily_log 
            WHERE content LIKE ? OR tags LIKE ?
            ORDER BY timestamp DESC 
            LIMIT 50
        ''', (f'%{keyword}%', f'%{keyword}%'))
        
        entries = []
        for row in cursor.fetchall():
            entries.append({
                'id': row[0],
                'timestamp': row[1],
                'content': row[2],
                'category': row[3],
                'tags': row[4].split(',') if row[4] else [],
                'duration': row[5],
                'priority': row[6],
                'date': row[7]
            })
        
        conn.close()
        return entries
    
    def export_to_json(self, output_path, days=None):
        """导出为JSON格式"""
        entries = self.get_entries(days=days, limit=10000)
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'total_entries': len(entries),
            'entries': entries
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return len(entries)
    
    def export_to_csv(self, output_path, days=None):
        """导出为CSV格式"""
        entries = self.get_entries(days=days, limit=10000)
        
        with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', '日期', '时间', '内容', '分类', '标签', '时长(分钟)', '优先级'])
            
            for entry in entries:
                writer.writerow([
                    entry['id'],
                    entry['date'],
                    entry['timestamp'],
                    entry['content'],
                    entry['category'] or '',
                    ','.join(entry['tags']),
                    entry['duration'] or '',
                    entry['priority']
                ])
        
        return len(entries)
    
    def get_today_summary(self):
        """获取今日总结"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 今日记录数
        cursor.execute("SELECT COUNT(*) FROM daily_log WHERE date = date('now')")
        today_count = cursor.fetchone()[0]
        
        # 今日总时长
        cursor.execute("SELECT SUM(duration_minutes) FROM daily_log WHERE date = date('now')")
        today_duration = cursor.fetchone()[0] or 0
        
        # 今日分类分布
        cursor.execute('''
            SELECT category, COUNT(*) as count
            FROM daily_log 
            WHERE date = date('now') AND category IS NOT NULL
            GROUP BY category
        ''')
        today_categories = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 今日所有记录
        cursor.execute('''
            SELECT id, timestamp, content, category, duration_minutes
            FROM daily_log 
            WHERE date = date('now')
            ORDER BY timestamp DESC
        ''')
        today_entries = [
            {'id': row[0], 'time': row[1], 'content': row[2], 
             'category': row[3], 'duration': row[4]}
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        return {
            'count': today_count,
            'duration': today_duration,
            'categories': today_categories,
            'entries': today_entries
        }

def format_duration(minutes):
    """格式化时长"""
    if not minutes:
        return ""
    if minutes < 60:
        return f"{minutes}分钟"
    hours = minutes // 60
    mins = minutes % 60
    if mins:
        return f"{hours}小时{mins}分钟"
    return f"{hours}小时"

def print_entry(entry, show_details=True):
    """打印单条记录"""
    tags_str = f" #{' #'.join(entry['tags'])}" if entry['tags'] else ""
    duration_str = f" ⏱{format_duration(entry['duration'])}" if entry.get('duration') else ""
    priority_str = " ⭐" if entry.get('priority', 0) > 0 else ""
    
    print(f"  [{entry['id']}] {entry['content']}{tags_str}{duration_str}{priority_str}")
    if entry.get('category'):
        print(f"        📂 {entry['category']} | 📅 {entry['date']}")

def main():
    parser = argparse.ArgumentParser(
        description="📝 增强版每日记录工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s add "完成了项目报告" -c 工作 -t 项目,汇报 -d 60
  %(prog)s list -d 7 -c 工作
  %(prog)s stats -d 30
  %(prog)s today
  %(prog)s search "项目"
  %(prog)s export json backup.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 添加记录
    add_parser = subparsers.add_parser('add', help='添加新记录')
    add_parser.add_argument('content', help='记录内容')
    add_parser.add_argument('-c', '--category', help='分类 (如: 工作, 学习, 生活)')
    add_parser.add_argument('-t', '--tags', help='标签，用逗号分隔 (如: 项目,汇报)')
    add_parser.add_argument('-d', '--duration', type=int, help='时长(分钟)')
    add_parser.add_argument('-p', '--priority', type=int, choices=[0, 1], default=0, help='优先级 (0=普通, 1=重要)')
    
    # 查看记录
    list_parser = subparsers.add_parser('list', help='查看记录')
    list_parser.add_argument('-d', '--days', type=int, help='显示最近几天的记录')
    list_parser.add_argument('-c', '--category', help='按分类筛选')
    list_parser.add_argument('-t', '--tag', help='按标签筛选')
    list_parser.add_argument('-n', '--limit', type=int, default=20, help='显示数量限制')
    
    # 统计信息
    stats_parser = subparsers.add_parser('stats', help='查看统计信息')
    stats_parser.add_argument('-d', '--days', type=int, help='统计最近几天')
    
    # 今日总结
    today_parser = subparsers.add_parser('today', help='查看今日总结')
    
    # 分类管理
    cat_parser = subparsers.add_parser('categories', help='查看所有分类')
    
    # 删除记录
    delete_parser = subparsers.add_parser('delete', help='删除记录')
    delete_parser.add_argument('id', type=int, help='记录ID')
    
    # 搜索记录
    search_parser = subparsers.add_parser('search', help='搜索记录')
    search_parser.add_argument('keyword', help='搜索关键词')
    
    # 导出数据
    export_parser = subparsers.add_parser('export', help='导出数据')
    export_parser.add_argument('format', choices=['json', 'csv'], help='导出格式')
    export_parser.add_argument('output', help='输出文件路径')
    export_parser.add_argument('-d', '--days', type=int, help='导出最近几天的数据')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    logger = EnhancedDailyLogger()
    
    if args.command == 'add':
        tags = args.tags.split(',') if args.tags else None
        entry_id = logger.add_entry(
            args.content, 
            category=args.category, 
            tags=tags,
            duration=args.duration,
            priority=args.priority
        )
        print(f"✅ 记录已添加 (ID: {entry_id})")
        print(f"   📝 {args.content}")
        if args.category:
            print(f"   📂 分类: {args.category}")
        if tags:
            print(f"   🏷️ 标签: {', '.join(tags)}")
        if args.duration:
            print(f"   ⏱️ 时长: {format_duration(args.duration)}")
    
    elif args.command == 'list':
        entries = logger.get_entries(
            days=args.days,
            category=args.category,
            tag=args.tag,
            limit=args.limit
        )
        
        if not entries:
            print("📝 没有找到记录")
            return
        
        print(f"📝 找到 {len(entries)} 条记录:")
        print("-" * 60)
        for entry in entries:
            print_entry(entry)
            print()
    
    elif args.command == 'stats':
        stats = logger.get_stats(days=args.days)
        
        print("📊 统计信息")
        print("=" * 50)
        print(f"📈 总记录数: {stats['total']}")
        print(f"⏱️  总时长: {format_duration(stats['total_duration'])}")
        print(f"📅 本周记录: {stats['this_week']}")
        print(f"📆 本月记录: {stats['this_month']}")
        
        if stats['category_stats']:
            print("\n📂 分类统计:")
            print("-" * 40)
            for cat in stats['category_stats']:
                duration_str = f" ({format_duration(cat['duration'])})" if cat['duration'] else ""
                print(f"  {cat['name']}: {cat['count']} 条{duration_str}")
        
        if stats['daily_stats']:
            print("\n📅 最近7天:")
            print("-" * 40)
            for day in stats['daily_stats']:
                duration_str = f" ({format_duration(day['duration'])})" if day['duration'] else ""
                print(f"  {day['date']}: {day['count']} 条{duration_str}")
        
        if stats['tag_stats']:
            print("\n🏷️ 热门标签:")
            print("-" * 40)
            for tag in stats['tag_stats'][:5]:
                print(f"  #{tag['tag']}: {tag['count']} 次")
    
    elif args.command == 'today':
        summary = logger.get_today_summary()
        
        print("📋 今日总结")
        print("=" * 50)
        print(f"📊 记录数: {summary['count']}")
        print(f"⏱️  总时长: {format_duration(summary['duration'])}")
        
        if summary['categories']:
            print("\n📂 分类分布:")
            for cat, count in summary['categories'].items():
                print(f"  {cat}: {count} 条")
        
        if summary['entries']:
            print("\n📝 今日记录:")
            print("-" * 50)
            for entry in summary['entries']:
                time_str = entry['time'].split(' ')[1][:5] if ' ' in entry['time'] else ''
                duration_str = f" ⏱{format_duration(entry['duration'])}" if entry.get('duration') else ""
                cat_str = f" [{entry['category']}]" if entry.get('category') else ""
                print(f"  {time_str}{cat_str} {entry['content']}{duration_str}")
    
    elif args.command == 'categories':
        categories = logger.get_categories()
        print("📂 可用分类:")
        print("-" * 30)
        for cat in categories:
            icon = cat['icon'] or '•'
            color = cat['color'] or ''
            print(f"  {icon} {cat['name']}")
    
    elif args.command == 'delete':
        if logger.delete_entry(args.id):
            print(f"🗑️ 已删除记录 {args.id}")
        else:
            print(f"❌ 未找到记录 {args.id}")
    
    elif args.command == 'search':
        entries = logger.search_entries(args.keyword)
        if not entries:
            print(f"🔍 未找到包含 '{args.keyword}' 的记录")
            return
        
        print(f"🔍 找到 {len(entries)} 条记录:")
        print("-" * 60)
        for entry in entries:
            print_entry(entry)
            print()
    
    elif args.command == 'export':
        if args.format == 'json':
            count = logger.export_to_json(args.output, days=args.days)
        else:
            count = logger.export_to_csv(args.output, days=args.days)
        print(f"✅ 已导出 {count} 条记录到 {args.output}")

if __name__ == "__main__":
    main()
