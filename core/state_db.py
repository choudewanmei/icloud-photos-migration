"""
状态数据库模块
支持：断点续传、连接池、索引优化
"""

import sqlite3
import threading
from datetime import datetime
from contextlib import contextmanager
from typing import Optional, List, Dict, Any

from core.logger import get_logger
from core.constants import DB_MAX_CONNECTIONS


class ConnectionPool:
    """SQLite 连接池"""
    
    def __init__(self, db_path: str, max_connections: int = DB_MAX_CONNECTIONS):
        self.db_path = db_path
        self.max_connections = max_connections
        self._connections: List[sqlite3.Connection] = []
        self._lock = threading.Lock()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接"""
        conn = None
        with self._lock:
            if self._connections:
                conn = self._connections.pop()
        
        if conn is None:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
        
        try:
            yield conn
        except sqlite3.Error:
            conn.rollback()
            raise
        finally:
            with self._lock:
                if len(self._connections) < self.max_connections:
                    self._connections.append(conn)
                else:
                    conn.close()
    
    def close_all(self):
        """关闭所有连接"""
        with self._lock:
            for conn in self._connections:
                try:
                    conn.close()
                except sqlite3.Error:
                    pass
            self._connections.clear()


class StateDB:
    """状态数据库管理器"""
    
    def __init__(self, db_path: str = "migration_state.db"):
        self.db_path = db_path
        self.logger = get_logger()
        self.pool = ConnectionPool(db_path)
        self._init_db()
    
    def _init_db(self):
        """初始化数据库表和索引"""
        try:
            with self.pool.get_connection() as conn:
                # 迁移运行记录
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS migration_runs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        start_time TEXT,
                        end_time TEXT,
                        status TEXT,
                        total_assets INTEGER,
                        downloaded INTEGER DEFAULT 0,
                        skipped INTEGER DEFAULT 0,
                        failed INTEGER DEFAULT 0,
                        duplicates INTEGER DEFAULT 0,
                        retries INTEGER DEFAULT 0,
                        duration_seconds REAL DEFAULT 0
                    )
                """)
                
                # 已下载文件记录
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS downloaded_files (
                        asset_id TEXT PRIMARY KEY,
                        filename TEXT,
                        target_path TEXT,
                        file_hash TEXT,
                        file_size INTEGER,
                        download_time TEXT,
                        status TEXT DEFAULT 'completed'
                    )
                """)
                
                # 失败文件记录
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS failed_files (
                        asset_id TEXT PRIMARY KEY,
                        filename TEXT,
                        error_message TEXT,
                        retry_count INTEGER DEFAULT 0,
                        last_attempt TEXT,
                        status TEXT DEFAULT 'pending'
                    )
                """)
                
                # 配置存储
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS config (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_at TEXT
                    )
                """)
                
                # 创建索引
                conn.execute("CREATE INDEX IF NOT EXISTS idx_downloaded_files_status ON downloaded_files(status)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_failed_files_status ON failed_files(status)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_migration_runs_status ON migration_runs(status)")
                
                conn.commit()
                self.logger.info("数据库初始化完成")
                
        except sqlite3.Error as e:
            self.logger.error(f"数据库初始化失败: {e}")
            raise
    
    def start_run(self, total_assets: int) -> int:
        """开始新的迁移运行"""
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.execute(
                    "INSERT INTO migration_runs (start_time, status, total_assets) VALUES (?, ?, ?)",
                    (datetime.now().isoformat(), "running", total_assets)
                )
                conn.commit()
                self.logger.info(f"创建迁移运行记录: ID={cursor.lastrowid}, 总数={total_assets}")
                return cursor.lastrowid
        except sqlite3.Error as e:
            self.logger.error(f"创建迁移运行记录失败: {e}")
            raise
    
    def update_run(self, run_id: int, **kwargs):
        """更新运行状态"""
        try:
            with self.pool.get_connection() as conn:
                updates = []
                values = []
                for key, value in kwargs.items():
                    updates.append(f"{key} = ?")
                    values.append(value)
                
                values.append(run_id)
                sql = f"UPDATE migration_runs SET {', '.join(updates)} WHERE id = ?"
                conn.execute(sql, values)
                conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"更新运行状态失败: {e}")
            raise
    
    def complete_run(self, run_id: int, stats: dict):
        """完成迁移运行"""
        self.update_run(
            run_id,
            end_time=datetime.now().isoformat(),
            status="completed",
            downloaded=stats.get("downloaded", 0),
            skipped=stats.get("skipped", 0),
            failed=stats.get("failed", 0),
            duplicates=stats.get("duplicates", 0),
            retries=stats.get("total_retries", 0),
            duration_seconds=stats.get("duration_seconds", 0)
        )
        self.logger.info(f"迁移运行完成: ID={run_id}")
    
    def fail_run(self, run_id: int, error_message: str):
        """标记运行失败"""
        self.update_run(run_id, end_time=datetime.now().isoformat(), status="failed")
        self.logger.error(f"迁移运行失败: ID={run_id}, 错误={error_message}")
    
    def pause_run(self, run_id: int):
        """暂停运行"""
        self.update_run(run_id, status="paused")
        self.logger.info(f"迁移运行暂停: ID={run_id}")
    
    def get_latest_run(self) -> Optional[sqlite3.Row]:
        """获取最新的运行记录"""
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.execute("SELECT * FROM migration_runs ORDER BY id DESC LIMIT 1")
                return cursor.fetchone()
        except sqlite3.Error as e:
            self.logger.error(f"获取最新运行记录失败: {e}")
            return None
    
    def get_run_by_id(self, run_id: int) -> Optional[sqlite3.Row]:
        """根据 ID 获取运行记录"""
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.execute("SELECT * FROM migration_runs WHERE id = ?", (run_id,))
                return cursor.fetchone()
        except sqlite3.Error as e:
            self.logger.error(f"获取运行记录失败: {e}")
            return None
    
    def add_downloaded_file(self, asset_id: str, filename: str, target_path: str,
                           file_hash: Optional[str] = None, file_size: Optional[int] = None):
        """记录已下载文件"""
        try:
            with self.pool.get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO downloaded_files 
                    (asset_id, filename, target_path, file_hash, file_size, download_time, status) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (asset_id, filename, target_path, file_hash, file_size, 
                      datetime.now().isoformat(), "completed"))
                conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"记录已下载文件失败: {e}")
    
    def is_file_downloaded(self, asset_id: str) -> bool:
        """检查文件是否已下载"""
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT 1 FROM downloaded_files WHERE asset_id = ? AND status = 'completed'", 
                    (asset_id,)
                )
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            self.logger.error(f"检查文件下载状态失败: {e}")
            return False
    
    def get_downloaded_count(self) -> int:
        """获取已下载文件数量"""
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM downloaded_files WHERE status = 'completed'")
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            self.logger.error(f"获取已下载文件数量失败: {e}")
            return 0
    
    def get_failed_count(self, status: str = "pending") -> int:
        """获取失败文件数量"""
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM failed_files WHERE status = ?", (status,))
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            self.logger.error(f"获取失败文件数量失败: {e}")
            return 0
    
    def add_failed_file(self, asset_id: str, filename: str, error_message: str):
        """记录失败文件"""
        try:
            with self.pool.get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO failed_files 
                    (asset_id, filename, error_message, retry_count, last_attempt, status) 
                    VALUES (?, ?, ?, 
                        COALESCE((SELECT retry_count FROM failed_files WHERE asset_id = ?), 0) + 1,
                        ?, ?)
                """, (asset_id, filename, error_message, asset_id, datetime.now().isoformat(), "pending"))
                conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"记录失败文件失败: {e}")
    
    def get_failed_files(self, status: Optional[str] = None) -> List[sqlite3.Row]:
        """获取失败文件"""
        try:
            with self.pool.get_connection() as conn:
                if status:
                    cursor = conn.execute(
                        "SELECT * FROM failed_files WHERE status = ? ORDER BY last_attempt DESC",
                        (status,)
                    )
                else:
                    cursor = conn.execute("SELECT * FROM failed_files ORDER BY last_attempt DESC")
                return cursor.fetchall()
        except sqlite3.Error as e:
            self.logger.error(f"获取失败文件失败: {e}")
            return []
    
    def get_total_downloaded_size(self) -> int:
        """获取已下载文件总大小"""
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.execute("SELECT SUM(file_size) FROM downloaded_files WHERE status = 'completed'")
                result = cursor.fetchone()[0]
                return result if result else 0
        except sqlite3.Error as e:
            self.logger.error(f"获取已下载文件总大小失败: {e}")
            return 0
    
    def save_config(self, key: str, value: str):
        """保存配置"""
        try:
            with self.pool.get_connection() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO config (key, value, updated_at) VALUES (?, ?, ?)",
                    (key, value, datetime.now().isoformat())
                )
                conn.commit()
        except sqlite3.Error as e:
            self.logger.error(f"保存配置失败: {e}")
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置"""
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.execute("SELECT value FROM config WHERE key = ?", (key,))
                row = cursor.fetchone()
                return row[0] if row else default
        except sqlite3.Error as e:
            self.logger.error(f"获取配置失败: {e}")
            return default
    
    def get_all_configs(self) -> Dict[str, str]:
        """获取所有配置"""
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.execute("SELECT key, value FROM config")
                return {row[0]: row[1] for row in cursor.fetchall()}
        except sqlite3.Error as e:
            self.logger.error(f"获取所有配置失败: {e}")
            return {}
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "downloaded": self.get_downloaded_count(),
            "failed": self.get_failed_count(),
            "total_size": self.get_total_downloaded_size()
        }
    
    def get_resume_info(self) -> Dict[str, Any]:
        """获取断点续传信息"""
        latest_run = self.get_latest_run()
        
        if latest_run and latest_run["status"] == "paused":
            return {
                "can_resume": True,
                "run_id": latest_run["id"],
                "downloaded": latest_run["downloaded"],
                "total": latest_run["total_assets"],
                "progress": latest_run["downloaded"] / latest_run["total_assets"] if latest_run["total_assets"] > 0 else 0
            }
        
        return {"can_resume": False}
    
    def close(self):
        """关闭数据库连接池"""
        self.pool.close_all()
        self.logger.info("数据库连接已关闭")
