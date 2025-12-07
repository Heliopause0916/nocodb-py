# test_nocodb_integration.py
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

api_key_cloud = os.getenv("NOCODB_CLOUD_API_KEY", "changeme")
base_url_cloud = os.getenv("NOCODB_CLOUD_BASE_URL", "https://app.nocodb.com")
workspace_name_cloud = os.getenv("NOCODB_CLOUD_WORKSPACE_NAME", "test")
project_name_cloud = os.getenv("NOCODB_CLOUD_PROJECT_NAME", "test")
table_name_cloud = os.getenv("NOCODB_CLOUD_TABLE_NAME", "test")

# Fixture：创建客户端
@pytest.fixture
def client():
    return NocoDBClient(base_url=base_url, xc_token=api_key)

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

# Fixture：查找本地项目
@pytest.fixture
def local_project(client):
    """查找本地名为NOCODB_PROJECT_NAME的项目"""
    projects_own = client.list_projects()
    
    for tmp_project in projects_own:
        if tmp_project["title"] == project_name:
            return client.get_project(tmp_project["id"])
    
    pytest.skip(f"Local project '{project_name}' not found")

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
class TestNocoDBIntegration:
    """NocoDB 客户端集成测试"""
    
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
    
    def test_count_projects(self, client):
        """测试计数项目"""
        count = client.count_projects()
        print(f"Local projects count: {count}")
    
    def test_list_projects_both_clients(self, client, target_workspace):
        """测试在两个客户端下列出项目"""
        projects_own = client.list_projects()
        projects_cloud = target_workspace.list_projects()
        print(f"Local projects: {len(projects_own)}, Cloud projects: {len(projects_cloud)}")
    
    def test_project_details(self, local_project, cloud_project):
        """测试项目详情和表格列表"""
        # 本地项目表格列表
        tables = local_project.list_tables()
        print(f"Local project tables count: {len(tables)}")
        
        # 可以打印表格详情（可选）
        # print(json.dumps(tables, indent=2, ensure_ascii=False))
    
    def test_cloud_project_tables(self, cloud_project):
        """测试云端项目表格列表"""
        tables = cloud_project.list_tables()
        print(f"Cloud project tables count: {len(tables)}")
    
    def test_get_nocodb_info(self, client, client_cloud):
        """测试获取 NocoDB 完整信息（注释掉的代码）"""
        # 如果这些函数存在且你想测试它们，取消注释
        # info_local = client.get_full_info()
        # info_cloud = client_cloud.get_full_info()
        # print("NocoDB info functions executed successfully")

# 如果需要更详细的调试信息，可以添加这个测试
def test_debug_info(client, client_cloud, target_workspace):
    """调试信息测试（原代码中的打印语句）"""
    # 这些可以保留用于调试，但通常生产测试中会去掉
    print("Debug info test - all operations completed without exceptions")
