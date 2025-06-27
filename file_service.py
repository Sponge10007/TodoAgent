#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件附件服务模块
支持文件上传、下载、管理
"""

import os
import uuid
import hashlib
import mimetypes
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
import shutil
import logging
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)

class FileService:
    """文件服务类"""
    
    def __init__(self):
        """初始化文件服务"""
        self.upload_dir = Path(os.getenv('UPLOAD_FOLDER', 'uploads'))
        self.max_file_size = int(os.getenv('MAX_FILE_SIZE', 10485760))  # 10MB
        self.allowed_extensions = {
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
            'document': ['.pdf', '.doc', '.docx', '.txt', '.md', '.rtf'],
            'spreadsheet': ['.xls', '.xlsx', '.csv'],
            'archive': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'other': ['.json', '.xml', '.yaml', '.yml']
        }
        
        # 确保上传目录存在
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        for category in self.allowed_extensions.keys():
            (self.upload_dir / category).mkdir(exist_ok=True)
    
    def get_file_category(self, filename: str) -> str:
        """根据文件扩展名获取分类"""
        ext = Path(filename).suffix.lower()
        
        for category, extensions in self.allowed_extensions.items():
            if ext in extensions:
                return category
        
        return 'other'
    
    def validate_file(self, file: UploadFile) -> Dict[str, Any]:
        """验证文件"""
        errors = []
        
        # 检查文件大小
        if hasattr(file, 'size') and file.size > self.max_file_size:
            errors.append(f"文件大小超过限制 ({self.max_file_size / 1024 / 1024:.1f}MB)")
        
        # 检查文件类型
        category = self.get_file_category(file.filename)
        if category == 'other':
            ext = Path(file.filename).suffix.lower()
            if ext not in self.allowed_extensions['other']:
                errors.append(f"不支持的文件类型: {ext}")
        
        # 检查文件名
        if not file.filename or len(file.filename) > 255:
            errors.append("文件名无效")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'category': category,
            'original_name': file.filename,
            'size': getattr(file, 'size', 0)
        }
    
    async def save_file(self, file: UploadFile, task_id: Optional[int] = None, 
                       todo_id: Optional[int] = None) -> Dict[str, Any]:
        """保存上传的文件"""
        try:
            # 验证文件
            validation = self.validate_file(file)
            if not validation['valid']:
                raise HTTPException(status_code=400, detail=validation['errors'])
            
            # 生成唯一文件名
            file_id = str(uuid.uuid4())
            file_ext = Path(file.filename).suffix.lower()
            new_filename = f"{file_id}{file_ext}"
            
            # 确定保存路径
            category = validation['category']
            file_path = self.upload_dir / category / new_filename
            
            # 保存文件
            content = await file.read()
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # 计算文件哈希
            file_hash = hashlib.md5(content).hexdigest()
            
            # 获取文件信息
            file_info = {
                'id': file_id,
                'original_name': file.filename,
                'filename': new_filename,
                'file_path': str(file_path),
                'category': category,
                'size': len(content),
                'mime_type': mimetypes.guess_type(file.filename)[0],
                'hash': file_hash,
                'task_id': task_id,
                'todo_id': todo_id,
                'uploaded_at': datetime.utcnow().isoformat(),
                'url': f"/api/files/{file_id}"
            }
            
            logger.info(f"文件保存成功: {file.filename} -> {new_filename}")
            return file_info
            
        except Exception as e:
            logger.error(f"文件保存失败: {e}")
            raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")
    
    def get_file_path(self, file_id: str) -> Optional[Path]:
        """根据文件ID获取文件路径"""
        for category_dir in self.upload_dir.iterdir():
            if category_dir.is_dir():
                for file_path in category_dir.glob(f"{file_id}.*"):
                    return file_path
        return None
    
    def delete_file(self, file_id: str) -> bool:
        """删除文件"""
        try:
            file_path = self.get_file_path(file_id)
            if file_path and file_path.exists():
                file_path.unlink()
                logger.info(f"文件删除成功: {file_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"文件删除失败: {e}")
            return False
    
    def get_file_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """获取文件信息"""
        file_path = self.get_file_path(file_id)
        if not file_path or not file_path.exists():
            return None
        
        stat = file_path.stat()
        return {
            'id': file_id,
            'filename': file_path.name,
            'size': stat.st_size,
            'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'category': file_path.parent.name,
            'mime_type': mimetypes.guess_type(file_path.name)[0]
        }
    
    def list_files(self, category: Optional[str] = None, 
                   task_id: Optional[int] = None,
                   todo_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """列出文件"""
        files = []
        
        if category:
            search_dirs = [self.upload_dir / category]
        else:
            search_dirs = [d for d in self.upload_dir.iterdir() if d.is_dir()]
        
        for dir_path in search_dirs:
            if not dir_path.exists():
                continue
                
            for file_path in dir_path.iterdir():
                if file_path.is_file():
                    file_id = file_path.stem
                    file_info = self.get_file_info(file_id)
                    if file_info:
                        files.append(file_info)
        
        return files
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """获取存储统计"""
        stats = {
            'total_files': 0,
            'total_size': 0,
            'by_category': {}
        }
        
        for category_dir in self.upload_dir.iterdir():
            if category_dir.is_dir():
                category_files = list(category_dir.glob('*'))
                category_size = sum(f.stat().st_size for f in category_files if f.is_file())
                
                stats['by_category'][category_dir.name] = {
                    'count': len(category_files),
                    'size': category_size
                }
                
                stats['total_files'] += len(category_files)
                stats['total_size'] += category_size
        
        return stats
    
    def cleanup_orphaned_files(self, valid_file_ids: List[str]) -> int:
        """清理孤立文件"""
        cleaned = 0
        
        for category_dir in self.upload_dir.iterdir():
            if category_dir.is_dir():
                for file_path in category_dir.iterdir():
                    if file_path.is_file():
                        file_id = file_path.stem
                        if file_id not in valid_file_ids:
                            try:
                                file_path.unlink()
                                cleaned += 1
                                logger.info(f"清理孤立文件: {file_path.name}")
                            except Exception as e:
                                logger.error(f"清理文件失败: {e}")
        
        return cleaned

# 全局文件服务实例
file_service = FileService() 