import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# API Keys配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

# 应用配置
DEFAULT_MODEL = "qwen-turbo"
PLAN_FILE_PATH = "plan.json"

# 验证API Keys
def validate_config():
    missing_keys = []
    if not DASHSCOPE_API_KEY:
        missing_keys.append("DASHSCOPE_API_KEY")
    
    if missing_keys:
        print(f"⚠️  缺少以下环境变量: {', '.join(missing_keys)}")
        print("请在.env文件中设置API密钥")
        print("获取地址: https://dashscope.console.aliyun.com/apiKey")
        return False
    return True 