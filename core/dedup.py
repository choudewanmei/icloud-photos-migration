"""
文件去重模块
基于 SHA256 哈希识别重复文件
"""

import os
import hashlib
from pathlib import Path
from collections import defaultdict


class FileDeduplicator:
    """文件去重器"""
    
    def __init__(self, target_dir):
        self.target_dir = target_dir
        self.hash_map = defaultdict(list)  # hash -> [file_paths]
        self.duplicates = []  # [(original, duplicate), ...]
    
    def scan_directory(self, progress_callback=None):
        """
        扫描目录，计算所有文件的哈希值
        """
        self.hash_map.clear()
        self.duplicates.clear()
        
        all_files = []
        for root, dirs, files in os.walk(self.target_dir):
            # 跳过特殊目录
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '_duplicates']
            
            for filename in files:
                if not filename.startswith('.'):
                    filepath = os.path.join(root, filename)
                    all_files.append(filepath)
        
        total_files = len(all_files)
        
        for i, filepath in enumerate(all_files):
            try:
                file_hash = self._calculate_hash(filepath)
                self.hash_map[file_hash].append(filepath)
                
                if progress_callback:
                    progress_callback(i + 1, total_files, filepath)
                    
            except Exception as e:
                print(f"计算哈希失败: {filepath} - {e}")
        
        # 识别重复文件
        self._find_duplicates()
        
        return self.duplicates
    
    def _calculate_hash(self, filepath, chunk_size=8192):
        """计算文件的 SHA256 哈希值"""
        sha256 = hashlib.sha256()
        
        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                sha256.update(chunk)
        
        return sha256.hexdigest()
    
    def _find_duplicates(self):
        """识别重复文件"""
        self.duplicates.clear()
        
        for file_hash, file_list in self.hash_map.items():
            if len(file_list) > 1:
                # 按文件路径排序，保留第一个作为原始文件
                file_list.sort()
                original = file_list[0]
                
                for duplicate in file_list[1:]:
                    self.duplicates.append((original, duplicate))
    
    def get_duplicates(self):
        """获取重复文件列表"""
        return self.duplicates
    
    def get_duplicate_count(self):
        """获取重复文件数量"""
        return len(self.duplicates)
    
    def move_duplicates(self, duplicate_dir=None, dry_run=False):
        """
        将重复文件移动到 _duplicates 目录
        
        Args:
            duplicate_dir: 重复文件存放目录，默认为 _duplicates
            dry_run: 仅模拟，不实际移动
        
        Returns:
            moved_count: 成功移动的文件数量
        """
        if not self.duplicates:
            return 0
        
        if duplicate_dir is None:
            duplicate_dir = os.path.join(self.target_dir, "_duplicates")
        
        moved_count = 0
        
        for original, duplicate in self.duplicates:
            try:
                # 保持相对路径结构
                rel_path = os.path.relpath(duplicate, self.target_dir)
                dest_path = os.path.join(duplicate_dir, rel_path)
                dest_dir = os.path.dirname(dest_path)
                
                if dry_run:
                    print(f"[模拟] 移动: {duplicate} -> {dest_path}")
                    moved_count += 1
                else:
                    os.makedirs(dest_dir, exist_ok=True)
                    
                    # 如果目标文件已存在，添加后缀
                    if os.path.exists(dest_path):
                        base, ext = os.path.splitext(dest_path)
                        counter = 1
                        while os.path.exists(dest_path):
                            dest_path = f"{base}_{counter}{ext}"
                            counter += 1
                    
                    os.rename(duplicate, dest_path)
                    moved_count += 1
                    
            except Exception as e:
                print(f"移动失败: {duplicate} - {e}")
        
        return moved_count
    
    def generate_report(self):
        """生成去重报告"""
        report = []
        report.append("=" * 50)
        report.append("文件去重报告")
        report.append("=" * 50)
        report.append(f"扫描目录: {self.target_dir}")
        report.append(f"总文件数: {sum(len(files) for files in self.hash_map.values())}")
        report.append(f"唯一文件数: {len(self.hash_map)}")
        report.append(f"重复文件数: {len(self.duplicates)}")
        report.append("")
        
        if self.duplicates:
            report.append("重复文件详情:")
            report.append("-" * 50)
            
            # 按哈希值分组显示
            hash_groups = defaultdict(list)
            for original, duplicate in self.duplicates:
                file_hash = self._calculate_hash(original)
                hash_groups[file_hash].append((original, duplicate))
            
            for i, (file_hash, pairs) in enumerate(hash_groups.items(), 1):
                report.append(f"\n重复组 {i} (哈希: {file_hash[:16]}...):")
                original, _ = pairs[0]
                report.append(f"  原始: {original}")
                for _, duplicate in pairs:
                    report.append(f"  重复: {duplicate}")
        else:
            report.append("\n未发现重复文件")
        
        return "\n".join(report)


class DeduplicationStats:
    """去重统计信息"""
    
    def __init__(self):
        self.total_files = 0
        self.unique_files = 0
        self.duplicate_files = 0
        self.saved_space = 0  # bytes
    
    @property
    def duplicate_ratio(self):
        """重复率"""
        if self.total_files == 0:
            return 0
        return self.duplicate_files / self.total_files
    
    @property
    def saved_space_mb(self):
        """节省空间（MB）"""
        return self.saved_space / (1024 * 1024)
    
    @property
    def saved_space_gb(self):
        """节省空间（GB）"""
        return self.saved_space / (1024 * 1024 * 1024)
    
    def to_dict(self):
        """转换为字典"""
        return {
            "total_files": self.total_files,
            "unique_files": self.unique_files,
            "duplicate_files": self.duplicate_files,
            "duplicate_ratio": f"{self.duplicate_ratio:.2%}",
            "saved_space_mb": f"{self.saved_space_mb:.2f}",
            "saved_space_gb": f"{self.saved_space_gb:.2f}"
        }
