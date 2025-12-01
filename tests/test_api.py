import pytest
import os

from dotenv import load_dotenv

# 尝试加载本地敏感配置（如果存在）
load_dotenv(dotenv_path="tests/.env", override=True)

@pytest.mark.needs_api
def test_api_connection():
    """需要真实 API 密钥的测试"""
    api_key: str = os.getenv("NOCODB_API_KEY", "changeme")
    base_url = os.getenv("NOCODB_BASE_URL", "http://localhost:8080")
    

def test_safe_unit_test():
    """不需要敏感信息的单元测试"""
    assert 1 + 1 == 2  # 安全测试始终运行
    