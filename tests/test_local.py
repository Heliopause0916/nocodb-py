# test_local.py - 本地实例测试
# pylint: disable=all
import os
import json
import pytest
from typing import Optional
from dotenv import load_dotenv
from nocodb_py import NocoDBClient

# 加载环境变量
load_dotenv(dotenv_path="tests/.env", override=True)

api_key = os.getenv("NOCODB_API_KEY", "changeme")
base_url = os.getenv("NOCODB_BASE_URL", "http://localhost:8080")
project_name = os.getenv("NOCODB_PROJECT_NAME", "test")
table_name = os.getenv("NOCODB_TABLE_NAME", "test")

# Fixture：创建本地客户端
@pytest.fixture
def client():
    return NocoDBClient(base_url=base_url, xc_token=api_key)

# Fixture：查找本地项目
@pytest.fixture
def local_project(client):
    """查找本地名为NOCODB_PROJECT_NAME的项目"""
    projects_own = client.list_projects()
    
    for tmp_project in projects_own:
        if tmp_project["title"] == project_name:
            return client.get_project(tmp_project["id"])
    
    pytest.skip(f"Local project '{project_name}' not found")

# 测试用例
class TestLocalNocoDB:
    """NocoDB 本地实例集成测试"""
    
    def test_count_projects(self, client):
        """测试计数本地项目"""
        count = client.count_projects()
        print(f"Local projects count: {count}")
    
    def test_list_projects(self, client):
        """测试列出本地项目"""
        projects = client.list_projects()
        print(f"Local projects: {len(projects)}")
    
    def test_local_project_tables(self, local_project):
        """测试本地项目表格列表"""
        tables = local_project.list_tables()
        print(f"Local project tables count: {len(tables)}")
        
        # 可以打印表格详情（可选）
        # print(json.dumps(tables, indent=2, ensure_ascii=False))