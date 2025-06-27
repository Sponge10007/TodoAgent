#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生活管家AI Agent - 启动脚本
"""

import os
import sys
import uvicorn
from database import init_db

def main():
    """主启动函数"""
    print("🤖 生活管家AI Agent 启动中...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要Python 3.8或更高版本")
        sys.exit(1)
    
    # 初始化数据库
    print("📊 初始化数据库...")
    try:
        init_db()
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        sys.exit(1)
    
    # 检查环境变量
    if not os.path.exists("env.example"):
        print("⚠️  警告: 未找到env.example文件，请配置环境变量")
    
    # 创建必要的目录
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    print("✅ 数据库初始化完成")
    print("🌐 启动Web服务器...")
    print("📍 访问地址: http://localhost:8000")
    print("📖 API文档: http://localhost:8000/docs")
    print("🛑 停止服务: Ctrl+C")
    print("-" * 50)
    
    # 启动服务器
    try:
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,  # 开发模式自动重载
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 感谢使用生活管家AI Agent！")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 