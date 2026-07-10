#!/usr/bin/env python3
"""每日记录工具 - 记录你的日常活动并统计分类"""

import sqlite3
import argparse
import sys
from datetime import datetime, date
from pathlib import Path

class DailyLogger:
    def __init__(self, db_path=None):
        if db_path is None:
            # 使用当前目录下的数据库文件
            db_path = Path.cwd() / "daily_logger.db"
        self.db_path = Path(db_path)
        self.init_db()
    
    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                content TEXT NOT NULL,
                category TEXT,
                date DATE DEFAULT (date('now'))
            )
        ''')
        # 创建分类表，方便管理
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # 插入一些默认分类
        default_categories = ['工作', '学习', '生活', '娱乐', '运动', '社交', '其他']
        for cat in default_categories:
            cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (cat,))
        
        conn.commit()
        conn.close()
    
    def add_entry(self, content, category=None):
        """添加记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 如果提供了分类，确保它存在于分类表中
        if category:
            cursor.execute('INSERT OR IGNORE INTO categories (name) VALUES (?)', (category,))
        
        cursor.execute('''
            INSERT INTO daily_log (content, category, date)
            VALUES (?, ?, date('now'))
        ''', (content, category))
        
        entry_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return entry_id
    
    def get_entries(self, days=None, category=None, limit=50):
        """获取记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT id, timestamp, content, category, date FROM daily_log WHERE 1=1"
        params = []
        
        if days:
            query += " AND date >= date('now', ?)"
            params.append(f"-{days} days")
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        entries = cursor.fetchall()
        conn.close()
        return entries
    
    def get_categories(self):
        """获取所有分类"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM categories ORDER BY name")
        categories = [row[0] for row in cursor.fetchall()]
        conn.close()
        return categories
    
    def get_stats(self, days=None):
        """获取统计信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 总记录数
        query_total = "SELECT COUNT(*) FROM daily_log"
        if days:
            query_total += " WHERE date >= date('now', ?)"
            cursor.execute(query_total, (f"-{days} days",))
        else:
            cursor.execute(query_total)
        total = cursor.fetchone()[0]
        
        # 按分类统计
        query_cat = "SELECT category, COUNT(*) as count FROM daily_log WHERE category IS NOT NULL"
        if days:
            query_cat += " AND date >= date('now', ?)"
        query_cat += " GROUP BY category ORDER BY count DESC"
        
        if days:
            cursor.execute(query_cat, (f"-{days} days",))
        else:
            cursor.execute(query_cat)
        
        category_stats = cursor.fetchall()
        
        # 最近7天每天的记录数
        cursor.execute('''
            SELECT date, COUNT(*) as count 
            FROM daily_log 
            WHERE date >= date('now', '-7 days')
            GROUP BY date 
            ORDER BY date DESC
        ''')
        daily_stats = cursor.fetchall()
        
        conn.close()
        return {
            'total': total,
            'category_stats': category_stats,
            'daily_stats': daily_stats
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
            SELECT id, timestamp, content, category, date 
            FROM daily_log 
            WHERE content LIKE ? 
            ORDER BY timestamp DESC 
            LIMIT 50
        ''', (f'%{keyword}%',))
        entries = cursor.fetchall()
        conn.close()
        return entries

def format_timestamp(timestamp_str):
    """格式化时间戳"""
    try:
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%m-%d %H:%M")
    except:
        return timestamp_str

def main():
    parser = argparse.ArgumentParser(description="每日记录工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 添加记录
    add_parser = subparsers.add_parser('add', help='添加新记录')
    add_parser.add_argument('content', help='记录内容')
    add_parser.add_argument('-c', '--category', help='分类')
    
    # 查看记录
    list_parser = subparsers.add_parser('list', help='查看记录')
    list_parser.add_argument('-d', '--days', type=int, help='显示最近几天的记录')
    list_parser.add_argument('-c', '--category', help='按分类筛选')
    list_parser.add_argument('-n', '--limit', type=int, default=20, help='显示数量限制')
    
    # 统计信息
    stats_parser = subparsers.add_parser('stats', help='查看统计信息')
    stats_parser.add_argument('-d', '--days', type=int, help='统计最近几天')
    
    # 分类管理
    cat_parser = subparsers.add_parser('categories', help='查看所有分类')
    
    # 删除记录
    delete_parser = subparsers.add_parser('delete', help='删除记录')
    delete_parser.add_argument('id', type=int, help='记录ID')
    
    # 搜索记录
    search_parser = subparsers.add_parser('search', help='搜索记录')
    search_parser.add_argument('keyword', help='搜索关键词')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    logger = DailyLogger()
    
    if args.command == 'add':
        entry_id = logger.add_entry(args.content, args.category)
        print(f"✅ 记录已添加 (ID: {entry_id})")
        print(f"   内容: {args.content}")
        if args.category:
            print(f"   分类: {args.category}")
    
    elif args.command == 'list':
        entries = logger.get_entries(
            days=args.days,
            category=args.category,
            limit=args.limit
        )
        
        if not entries:
            print("📝 没有找到记录")
            return
        
        print(f"📝 找到 {len(entries)} 条记录:")
        print("-" * 60)
        for entry in entries:
            entry_id, timestamp, content, category, entry_date = entry
            cat_str = f" [{category}]" if category else ""
            print(f"{entry_id:3}. {format_timestamp(timestamp)}{cat_str}")
            print(f"     {content}")
            print()
    
    elif args.command == 'stats':
        stats = logger.get_stats(days=args.days)
        
        print("📊 统计信息")
        print("=" * 40)
        print(f"总记录数: {stats['total']}")
        
        if stats['category_stats']:
            print("\n分类统计:")
            for category, count in stats['category_stats']:
                print(f"  {category}: {count} 条")
        
        if stats['daily_stats']:
            print("\n最近7天:")
            for day, count in stats['daily_stats']:
                print(f"  {day}: {count} 条")
    
    elif args.command == 'categories':
        categories = logger.get_categories()
        print("📂 可用分类:")
        for cat in categories:
            print(f"  • {cat}")
    
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
        for entry in entries:
            entry_id, timestamp, content, category, entry_date = entry
            cat_str = f" [{category}]" if category else ""
            print(f"{entry_id:3}. {format_timestamp(timestamp)}{cat_str}")
            print(f"     {content}")
            print()

if __name__ == "__main__":
    main()
