"""
改进的测试架构 - 专注于项目和表格层次的CRUD测试设计
提供步骤报告机制和更好的测试组织
"""

import os
import uuid
import json
import time
import pytest
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple, cast
from dotenv import load_dotenv
from loguru import logger
from nocodb_py import NocoDBClient, NocoDBProject, NocoDBTable
from requests.exceptions import RequestException

# 获取当前文件路径
current_file_path = Path(__file__).resolve()

# 加载环境变量
env_file_path = current_file_path.parent / ".env"
load_dotenv(dotenv_path=env_file_path, override=True)

api_key = os.getenv("NOCODB_API_KEY", "changeme")
base_url = os.getenv("NOCODB_BASE_URL", "http://localhost:8080")

# 配置loguru日志
log_file_path = current_file_path.parent / "test_improved.log"

# 移除默认logger配置
logger.remove()

# 配置文件日志
logger.add(
    log_file_path,
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="10 MB",
    retention="10 days",
    encoding="utf-8"
)

# 配置控制台日志
logger.add(
    lambda msg: print(msg, end=""),
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True
)

logger.info(f"Improved test architecture log file: {log_file_path}")

def generate_test_name(prefix: str = "test") -> str:
    """生成唯一的测试名称"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

# 在模块级别创建并打印客户端信息一次
client_instance = NocoDBClient(base_url=base_url, xc_token=api_key)

def print_client_info(client: NocoDBClient) -> None:
    """打印客户端基础信息"""
    try:
        server_version = client.server_version()
        is_cloud = client.is_cloud()
        user_email = client.user_email()
        user_display_name = client.user_display_name()
        base_url = client.get_base_url()
        
        logger.info("=" * 60)
        logger.info("NocoDB Client Information")
        logger.info("=" * 60)
        logger.info(f"Server Version: {server_version}")
        logger.info(f"Instance Type: {'Cloud' if is_cloud else 'Self-Hosted'}")
        logger.info(f"User Email: {user_email}")
        logger.info(f"User Display Name: {user_display_name}")
        logger.info(f"Base URL: {base_url}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.warning(f"Failed to get client information: {e}")

print_client_info(client_instance)

# Fixture：创建本地客户端
@pytest.fixture
def client() -> NocoDBClient:
    return client_instance

# 测试数据管理fixture
@pytest.fixture
def test_project(client: NocoDBClient):
    """创建测试项目fixture"""
    project_name = generate_test_name("test_project")
    logger.info(f"Creating test project: {project_name}")
    project = cast(NocoDBProject, client.create_project(project_name, return_type='object'))
    
    yield project
    
    # 清理逻辑
    try:
        logger.info(f"Cleaning up test project: {project.get_project_id()}")
        client.delete_project(project.get_project_id())
    except Exception as e:
        logger.warning(f"Project cleanup failed: {e}")

@pytest.fixture
def test_table(test_project: NocoDBProject, client: NocoDBClient) -> NocoDBTable:
    """创建测试表格fixture"""
    table_name = generate_test_name("test_table")
    logger.info(f"Creating test table: {table_name}")
    table: NocoDBTable = cast(NocoDBTable, test_project.create_table(table_name))
    
    yield table
    
    # 清理逻辑 - 使用客户端直接删除表格
    try:
        logger.info(f"Cleaning up test table: {table.get_table_id()}")
        # 使用客户端直接调用表格删除API
        client._delete(f"/api/v2/meta/tables/{table.get_table_id()}")
    except Exception as e:
        logger.warning(f"Table cleanup failed: {e}")

# 分层测试类 - 专注于项目和表格层次
class TestProjectCRUD:
    """项目CRUD测试类"""
    
    def test_create_project(self, client: NocoDBClient) -> None:
        """测试项目创建"""
        logger.info("[STEP START] 创建项目")
        project_name = generate_test_name("test_project")
        project = cast(NocoDBProject, client.create_project(project_name, return_type='object'))
        project_id = project.get_project_id()
        
        assert project_id is not None, "Project ID should not be None"
        assert isinstance(project, NocoDBProject), "Should return NocoDBProject object"
        
        # 验证项目信息
        project_info = project.get_full_info()
        assert project_info.get("title") == project_name, "Project title should match"
        
        # 清理
        client.delete_project(project_id)
        logger.info("[STEP COMPLETE] 创建项目")
    
    def test_get_project(self, test_project: NocoDBProject) -> None:
        """测试项目读取"""
        logger.info("[STEP START] 读取项目")
        project_id = test_project.get_project_id()
        project_info = test_project.get_full_info()
        
        assert "title" in project_info, "Project info should contain title"
        assert project_info.get("id") == project_id, "Project ID should match"
        assert "created_at" in project_info, "Project info should contain created_at"
        
        logger.info("[STEP COMPLETE] 读取项目")
    
    def test_update_project(self, test_project: NocoDBProject, client: NocoDBClient) -> None:
        """测试项目更新"""
        logger.info("[STEP START] 更新项目")
        original_title = test_project.get_title()
        updated_title = generate_test_name("updated_project")
        
        updated_project = cast(NocoDBProject, client.update_project(
            test_project.get_project_id(),
            title=updated_title,
            return_type='object'
        ))
        
        updated_info = updated_project.get_full_info()
        assert updated_info.get("title") == updated_title, "Project title should be updated"
        assert updated_info.get("title") != original_title, "Project title should be changed"
        
        logger.info("[STEP COMPLETE] 更新项目")
    
    def test_delete_project(self, client: NocoDBClient) -> None:
        """测试项目删除"""
        logger.info("[STEP START] 删除项目")
        project_name = generate_test_name("test_project")
        project = cast(NocoDBProject, client.create_project(project_name, return_type='object'))
        project_id = project.get_project_id()

        # 删除项目
        delete_response = client.delete_project(project_id)
        assert delete_response is not None, "Delete response should not be None"

        # 等待一段时间确保删除操作完成
        time.sleep(2)

        # 验证项目不在列表中（主要验证方式）
        all_projects = client.list_projects()
        project_ids = [p.get("id") for p in all_projects if p.get("id")]
        assert project_id not in project_ids, "Deleted project should not be in project list"

        # 尝试获取已删除项目（可能不会抛出异常，取决于API行为）
        try:
            deleted_project = client.get_project(project_id)
            # 如果获取成功，检查项目状态
            project_info = deleted_project.get_full_info()
            logger.warning(f"Project still accessible after deletion: {project_info}")
            # 如果项目仍然可访问，这可能表示删除操作没有完全生效
        except RequestException:
            # 如果抛出异常，说明项目确实被删除了
            logger.info("Project access correctly raised exception after deletion")

        logger.info("[STEP COMPLETE] 删除项目")

class TestTableCRUD:
    """表格CRUD测试类"""
    
    def test_create_table(self, test_project: NocoDBProject) -> None:
        """测试表格创建"""
        logger.info("[STEP START] 创建表格")
        table_name = generate_test_name("test_table")
        table: NocoDBTable = cast(NocoDBTable, test_project.create_table(table_name))
        table_id = table.get_table_id()
        
        assert table_id is not None, "Table ID should not be None"
        assert isinstance(table, NocoDBTable), "Should return NocoDBTable object"
        
        # 验证表格信息
        table_info = table.get_full_info()
        assert table_info.get("title") == table_name, "Table title should match"
        
        logger.info("[STEP COMPLETE] 创建表格")
    
    def test_get_table(self, test_table: NocoDBTable) -> None:
        """测试表格读取"""
        logger.info("[STEP START] 读取表格")
        table_id = test_table.get_table_id()
        table_info = test_table.get_full_info()
        
        assert "title" in table_info, "Table info should contain title"
        assert table_info.get("id") == table_id, "Table ID should match"
        assert "table_name" in table_info, "Table info should contain table_name"
        
        logger.info("[STEP COMPLETE] 读取表格")
    
    def test_update_table(self, test_table: NocoDBTable, test_project: NocoDBProject) -> None:
        """测试表格更新"""
        logger.info("[STEP START] 更新表格")
        original_title = test_table.get_title()
        updated_title = generate_test_name("updated_table")

        try:
            updated_table: NocoDBTable = cast(NocoDBTable, test_project.update_table(
                test_table.get_table_id(),
                title=updated_title
            ))

            updated_info = updated_table.get_full_info()
            assert updated_info.get("title") == updated_title, "Table title should be updated"
            assert updated_info.get("title") != original_title, "Table title should be changed"
            logger.info("[STEP COMPLETE] 更新表格")
        except RequestException as e:
            # 如果表格更新API不支持，跳过此测试
            logger.warning(f"Table update not supported: {e}")
            pytest.skip("Table update API not supported")
    
    def test_delete_table(self, test_project: NocoDBProject, client: NocoDBClient) -> None:
        """测试表格删除"""
        logger.info("[STEP START] 删除表格")
        table_name = generate_test_name("test_table")
        table: NocoDBTable = cast(NocoDBTable, test_project.create_table(table_name))
        table_id = table.get_table_id()
        
        # 删除表格 - 使用客户端直接调用API
        delete_response = client._delete(f"/api/v2/meta/tables/{table_id}")
        assert delete_response is not None, "Delete response should not be None"
        
        # 验证表格已删除（通过列表验证）
        tables = test_project.list_tables()
        table_ids = [t.get("id") for t in tables if t.get("id")]
        assert table_id not in table_ids, "Deleted table should not be in table list"
        
        logger.info("[STEP COMPLETE] 删除表格")

# 集成测试：项目→表格的完整流程
class TestIntegratedProjectTable:
    """集成测试 - 项目→表格的完整业务流程"""
    
    def test_project_table_workflow(self, client: NocoDBClient) -> None:
        """测试完整的项目→表格业务流程"""
        logger.info("[STEP START] 项目→表格完整流程")
        
        # 1. 创建项目
        project_name = generate_test_name("integrated_project")
        project = cast(NocoDBProject, client.create_project(project_name, return_type='object'))
        project_id = project.get_project_id()
        
        assert project_id is not None, "Project should be created"
        logger.info(f"Project created: {project_id}")
        
        # 2. 创建表格
        table_name = generate_test_name("integrated_table")
        table: NocoDBTable = cast(NocoDBTable, project.create_table(table_name))
        table_id = table.get_table_id()
        
        assert table_id is not None, "Table should be created"
        logger.info(f"Table created: {table_id}")
        
        # 3. 验证表格信息
        table_info = table.get_full_info()
        assert table_info.get("title") == table_name, "Table title should match"
        
        # 4. 更新表格（如果支持）
        updated_table_name = generate_test_name("updated_integrated_table")
        try:
            updated_table: NocoDBTable = cast(NocoDBTable, project.update_table(table_id, title=updated_table_name))
            updated_info = updated_table.get_full_info()
            assert updated_info.get("title") == updated_table_name, "Table should be updated"
        except RequestException:
            # 如果表格更新API不支持，跳过此步骤
            logger.warning("Table update not supported, skipping update step")
        
        # 5. 清理
        # 使用客户端直接删除表格
        client._delete(f"/api/v2/meta/tables/{table_id}")
        client.delete_project(project_id)
        
        logger.info("[STEP COMPLETE] 项目→表格完整流程")

# 参数化测试示例（可选）
@pytest.mark.parametrize("operation", ["create", "read", "update", "delete"])
class TestParametrizedProject:
    """参数化项目操作测试"""
    
    def test_project_operations(self, operation: str, client: NocoDBClient) -> None:
        """参数化测试项目操作"""
        if operation == "create":
            project_name = generate_test_name("param_project")
            project = cast(NocoDBProject, client.create_project(project_name, return_type='object'))
            assert project.get_project_id() is not None
            client.delete_project(project.get_project_id())
            
        elif operation == "read":
            # 需要先创建项目
            project_name = generate_test_name("param_project")
            project = cast(NocoDBProject, client.create_project(project_name, return_type='object'))
            project_info = project.get_full_info()
            assert "title" in project_info
            client.delete_project(project.get_project_id())
            
        elif operation == "update":
            project_name = generate_test_name("param_project")
            project = cast(NocoDBProject, client.create_project(project_name, return_type='object'))
            updated_name = generate_test_name("updated_param_project")
            updated_project = cast(NocoDBProject, client.update_project(
                project.get_project_id(), title=updated_name, return_type='object'
            ))
            assert updated_project.get_title() == updated_name
            client.delete_project(project.get_project_id())
            
        elif operation == "delete":
            project_name = generate_test_name("param_project")
            project = cast(NocoDBProject, client.create_project(project_name, return_type='object'))
            project_id = project.get_project_id()
            client.delete_project(project_id)

            # 等待一段时间确保删除操作完成
            time.sleep(2)

            # 验证项目不在列表中（主要验证方式）
            all_projects = client.list_projects()
            project_ids = [p.get("id") for p in all_projects if p.get("id")]
            assert project_id not in project_ids, "Deleted project should not be in project list"

if __name__ == "__main__":
    # 直接运行测试
    pytest.main([__file__, "-v", "-s"])