#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL Server 连接测试工具
"""

import os
import pyodbc
import pymssql
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_pyodbc_connection():
    """使用 pyodbc 测试连接"""
    print("🔧 测试 pyodbc 连接...")
    
    try:
        server = os.getenv('DB_SERVER', 'localhost')
        database = os.getenv('DB_NAME', 'master')  # 先连接到 master
        username = os.getenv('DB_USER', 'sa')
        password = os.getenv('DB_PASSWORD', '')
        driver = os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
        port = os.getenv('DB_PORT', '1433')
        
        # 构建连接字符串
        if password:
            conn_str = f'DRIVER={{{driver}}};SERVER={server},{port};DATABASE={database};UID={username};PWD={password}'
        else:
            conn_str = f'DRIVER={{{driver}}};SERVER={server},{port};DATABASE={database};Trusted_Connection=yes'
        
        print(f"📡 连接字符串: {conn_str.replace(password, '***')}")
        
        conn = pyodbc.connect(conn_str, timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        print(f"✅ pyodbc 连接成功！")
        print(f"📊 SQL Server 版本: {version[:100]}...")
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ pyodbc 连接失败: {e}")
        return False

def test_pymssql_connection():
    """使用 pymssql 测试连接"""
    print("\n🔧 测试 pymssql 连接...")
    
    try:
        server = os.getenv('DB_SERVER', 'localhost')
        database = os.getenv('DB_NAME', 'master')
        username = os.getenv('DB_USER', 'sa')
        password = os.getenv('DB_PASSWORD', '')
        port = int(os.getenv('DB_PORT', '1433'))
        
        if password:
            conn = pymssql.connect(
                server=server,
                port=port,
                user=username,
                password=password,
                database=database,
                timeout=10
            )
        else:
            print("❌ pymssql 不支持 Windows 集成认证")
            return False
        
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        print(f"✅ pymssql 连接成功！")
        print(f"📊 SQL Server 版本: {version[:100]}...")
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ pymssql 连接失败: {e}")
        return False

def list_available_drivers():
    """列出可用的 ODBC 驱动"""
    print("\n📋 可用的 ODBC 驱动:")
    try:
        drivers = pyodbc.drivers()
        for i, driver in enumerate(drivers, 1):
            print(f"   {i}. {driver}")
        
        # 找出 SQL Server 相关的驱动
        sql_drivers = [d for d in drivers if 'SQL Server' in d]
        if sql_drivers:
            print(f"\n✅ 推荐使用的 SQL Server 驱动:")
            for driver in sql_drivers:
                print(f"   - {driver}")
        else:
            print("\n❌ 未找到 SQL Server ODBC 驱动，请安装 Microsoft ODBC Driver for SQL Server")
            
    except Exception as e:
        print(f"❌ 获取驱动列表失败: {e}")

def test_sqlalchemy_connection():
    """测试 SQLAlchemy 连接"""
    print("\n🔧 测试 SQLAlchemy 连接...")
    
    try:
        from database import get_database_url, create_engine
        from sqlalchemy import text
        
        database_url = get_database_url()
        print(f"📡 数据库 URL: {database_url}")
        
        # 创建临时引擎连接到 master 数据库
        master_url = database_url.replace(os.getenv('DB_NAME', 'life_manager'), 'master')
        engine = create_engine(master_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT @@VERSION"))
            version = result.fetchone()[0]
            print(f"✅ SQLAlchemy 连接成功！")
            print(f"📊 SQL Server 版本: {version[:100]}...")
            
        return True
        
    except Exception as e:
        print(f"❌ SQLAlchemy 连接失败: {e}")
        return False

def show_configuration():
    """显示当前配置"""
    print("\n" + "="*50)
    print("📋 当前配置信息")
    print("="*50)
    print(f"数据库类型: {os.getenv('DB_TYPE', '未设置')}")
    print(f"服务器: {os.getenv('DB_SERVER', '未设置')}")
    print(f"端口: {os.getenv('DB_PORT', '未设置')}")
    print(f"数据库名: {os.getenv('DB_NAME', '未设置')}")
    print(f"用户名: {os.getenv('DB_USER', '未设置')}")
    print(f"密码: {'已设置' if os.getenv('DB_PASSWORD') else '未设置'}")
    print(f"驱动: {os.getenv('DB_DRIVER', '未设置')}")
    print("="*50)

def main():
    """主函数"""
    print("🚀 SQL Server 连接测试工具")
    print("="*50)
    
    # 显示配置
    show_configuration()
    
    # 检查配置
    if os.getenv('DB_TYPE', '').lower() != 'sqlserver':
        print("\n⚠️  警告: DB_TYPE 未设置为 'sqlserver'")
        print("请在 .env 文件中设置 DB_TYPE=sqlserver")
    
    # 列出可用驱动
    list_available_drivers()
    
    # 测试连接
    print("\n🔍 开始连接测试...")
    
    success_count = 0
    
    if test_pyodbc_connection():
        success_count += 1
    
    if test_pymssql_connection():
        success_count += 1
        
    if test_sqlalchemy_connection():
        success_count += 1
    
    print(f"\n📊 测试结果: {success_count}/3 个连接方式成功")
    
    if success_count == 0:
        print("\n❌ 所有连接测试都失败了，请检查配置和网络")
        print("\n💡 常见解决方案:")
        print("1. 确认 SQL Server 正在运行")
        print("2. 检查用户名和密码")
        print("3. 确认 TCP/IP 协议已启用")
        print("4. 检查防火墙设置")
        print("5. 安装正确的 ODBC 驱动")
    elif success_count < 3:
        print("\n⚠️  部分连接测试失败，但应用程序仍可正常运行")
    else:
        print("\n🎉 所有连接测试都成功！可以开始使用 SQL Server 了")

if __name__ == "__main__":
    main() 