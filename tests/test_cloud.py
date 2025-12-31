# test_cloud.py - 云端实例测试
# pylint: disable=all
import os
import json
import pytest
from typing import Optional
from dotenv import load_dotenv
from nocodb_py import NocoDBClient

# 加载环境变量
load_dotenv(dotenv_path="tests/.env", override=True)

api_key_cloud = os.getenv("NOCODB_CLOUD_API_KEY", "changeme")
base_url_cloud = os.getenv("NOCODB_CLOUD_BASE_URL", "https://app.nocodb.com")
workspace_name_cloud = os.getenv("NOCODB_CLOUD_WORKSPACE_NAME", "test")
project_name_cloud = os.getenv("NOCODB_CLOUD_PROJECT_NAME", "test")
table_name_cloud = os.getenv("NOCODB_CLOUD_TABLE_NAME", "test")

# Fixture：创建云端客户端
@pytest.fixture
def client_cloud():
    return NocoDBClient(base_url=base_url_cloud, xc_token=api_key_cloud)

# Fixture：查找目标工作区
@pytest.fixture
def target_workspace(client_cloud):
    workspaces_list = client_cloud.list_workspaces()
    
    if not workspaces_list:
        pytest.skip("No workspaces found")
    
    for workspace in workspaces_list:
        if workspace["title"] == workspace_name_cloud:
            return client_cloud.get_workspace(workspace["id"])
    
    pytest.skip(f"Target workspace '{workspace_name_cloud}' not found")

# Fixture：查找云端项目
@pytest.fixture
def cloud_project(target_workspace):
    """在目标工作区中查找名为NOCODB_CLOUD_PROJECT_NAME的项目"""
    projects_cloud = target_workspace.list_projects()
    
    for tmp_project in projects_cloud:
        if tmp_project["title"] == project_name_cloud:
            return target_workspace.get_project(tmp_project["id"])
    
    pytest.skip(f"Cloud project '{project_name_cloud}' not found")

# 测试用例
class TestCloudNocoDB:
    """NocoDB 云端实例集成测试"""
    
    def test_list_workspaces(self, client_cloud):
        """测试列出工作区 - 只要不抛异常就通过"""
        result = client_cloud.list_workspaces()
        # 不会显式断言，只要函数正常返回就通过
    
    def test_count_workspaces(self, client_cloud):
        """测试计数工作区"""
        count = client_cloud.count_workspaces()
        print(f"Workspaces count: {count}")
    
    def test_workspace_operations(self, target_workspace):
        """测试工作区相关操作"""
        count = target_workspace.count_projects()
        print(f"Projects count in workspace: {count}")
    
    def test_list_projects(self, target_workspace):
        """测试列出云端项目"""
        projects = target_workspace.list_projects()
        print(f"Cloud projects: {len(projects)}")
    
    def test_cloud_project_tables(self, cloud_project):
        """测试云端项目表格列表"""
        tables = cloud_project.list_tables()
        print(f"Cloud project tables count: {len(tables)}")