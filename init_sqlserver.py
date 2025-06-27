#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL Server 数据库初始化脚本
"""

import os
import pyodbc
from sqlalchemy import create_engine, text
from database import get_database_url, Base, engine
import urllib.parse

def check_sql_server_connection():
    """检查 SQL Server 连接"""
    try:
        # 测试连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ SQL Server 连接成功！")
            return True
    except Exception as e:
        print(f"❌ SQL Server 连接失败: {e}")
        return False

def create_database_if_not_exists():
    """如果数据库不存在则创建"""
    try:
        db_name = os.getenv("DB_NAME", "life_manager")
        server = os.getenv("DB_SERVER", "localhost")
        username = os.getenv("DB_USER", "sa")
        password = os.getenv("DB_PASSWORD", "")
        driver = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
        port = os.getenv("DB_PORT", "1433")
        
        # 连接到 master 数据库来创建新数据库
        if password:
            master_conn_str = f"mssql+pyodbc://{username}:{urllib.parse.quote_plus(password)}@{server}:{port}/master?driver={urllib.parse.quote_plus(driver)}"
        else:
            master_conn_str = f"mssql+pyodbc://@{server}:{port}/master?driver={urllib.parse.quote_plus(driver)}&trusted_connection=yes"
        
        master_engine = create_engine(master_conn_str)
        
        with master_engine.connect() as conn:
            # 设置自动提交模式
            conn = conn.execution_options(autocommit=True)
            
            # 检查数据库是否存在
            result = conn.execute(text(f"SELECT name FROM sys.databases WHERE name = '{db_name}'"))
            if not result.fetchone():
                # 创建数据库
                conn.execute(text(f"CREATE DATABASE [{db_name}]"))
                print(f"✅ 数据库 '{db_name}' 创建成功！")
            else:
                print(f"✅ 数据库 '{db_name}' 已存在")
                
    except Exception as e:
        print(f"❌ 创建数据库失败: {e}")
        raise

def init_sql_server():
    """初始化 SQL Server 数据库"""
    print("🔧 初始化 SQL Server 数据库...")
    
    # 检查环境变量
    if os.getenv("DB_TYPE", "").lower() != "sqlserver":
        print("❌ 请先设置 DB_TYPE=sqlserver")
        return False
    
    try:
        # 创建数据库（如果不存在）
        create_database_if_not_exists()
        
        # 检查连接
        if not check_sql_server_connection():
            return False
        
        # 创建表
        print("📊 创建数据库表...")
        Base.metadata.create_all(bind=engine)
        print("✅ 数据库表创建成功！")
        
        return True
        
    except Exception as e:
        print(f"❌ SQL Server 初始化失败: {e}")
        return False

def show_sql_server_info():
    """显示 SQL Server 配置信息"""
    print("\n" + "="*50)
    print("📋 SQL Server 配置信息")
    print("="*50)
    print(f"数据库类型: {os.getenv('DB_TYPE', 'sqlite')}")
    print(f"服务器: {os.getenv('DB_SERVER', 'localhost')}")
    print(f"端口: {os.getenv('DB_PORT', '1433')}")
    print(f"数据库名: {os.getenv('DB_NAME', 'life_manager')}")
    print(f"用户名: {os.getenv('DB_USER', 'sa')}")
    print(f"驱动: {os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')}")
    print(f"连接字符串: {get_database_url()}")
    print("="*50)

if __name__ == "__main__":
    show_sql_server_info()
    
    if init_sql_server():
        print("\n🎉 SQL Server 数据库初始化完成！")
        print("现在可以启动应用程序了: python start.py")
    else:
        print("\n❌ SQL Server 初始化失败，请检查配置") 