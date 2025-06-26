#!/usr/bin/env python3
"""
生活管家AI Agent 启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydantic
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        return False

def install_dependencies():
    """安装依赖"""
    print("📦 正在安装依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError:
        print("❌ 依赖安装失败")
        return False

def create_directories():
    """创建必要的目录"""
    directories = ["static", "templates"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ 目录结构检查完成")

def main():
    """主函数"""
    print("🚀 生活管家AI Agent 启动器")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("正在尝试安装依赖...")
        if not install_dependencies():
            print("❌ 无法安装依赖，请手动运行: pip install -r requirements.txt")
            return
    
    # 创建目录
    create_directories()
    
    # 启动应用
    print("🌐 启动Web应用...")
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main() 