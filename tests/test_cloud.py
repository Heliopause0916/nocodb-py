# test_cloud.py - 云端实例测试
# pylint: disable=all
import os
import uuid
import json
import pytest
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple, cast, Union, Generator
from dotenv import load_dotenv
from loguru import logger
from nocodb_py import NocoDBClient, NocoDBProject, NocoDBWorkspace
from requests.exceptions import RequestException

# 获取当前文件路径
current_file_path = Path(__file__).resolve()

# 加载环境变量
env_file_path = current_file_path.parent / ".env"
load_dotenv(dotenv_path=env_file_path, override=True)

api_key_cloud = os.getenv("NOCODB_CLOUD_API_KEY", "changeme")
base_url_cloud = os.getenv("NOCODB_CLOUD_BASE_URL", "https://app.nocodb.com")
workspace_name_cloud = os.getenv("NOCODB_CLOUD_WORKSPACE_NAME", "test")

# 配置loguru日志
log_file_path = current_file_path.parent / "test_cloud.log"

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

logger.info(f"Log file path: {log_file_path}")


def generate_test_name(prefix: str = "test") -> str:
    """Generate unique test name using UUID"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def print_client_info(client: NocoDBClient) -> None:
    """打印客户端基础信息"""
    try:
        # 获取服务器信息
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


# 在模块级别创建并打印客户端信息一次
client_instance_cloud = NocoDBClient(base_url=base_url_cloud, xc_token=api_key_cloud)
print_client_info(client_instance_cloud)

# Fixture：创建云端客户端
@pytest.fixture
def client_cloud() -> NocoDBClient:
    return client_instance_cloud


# Fixture：查找目标工作区
@pytest.fixture
def target_workspace(client_cloud: NocoDBClient) -> NocoDBWorkspace:
    workspaces_list: List[Dict[str, Any]] = client_cloud.list_workspaces()
    
    if not workspaces_list:
        pytest.skip("No workspaces found")
    
    for workspace in workspaces_list:
        if workspace["title"] == workspace_name_cloud:
            logger.info(f"Found target workspace: {workspace_name_cloud} (ID: {workspace['id']})")
            return client_cloud.get_workspace(workspace["id"])
    
    pytest.skip(f"Target workspace '{workspace_name_cloud}' not found")


# Fixture：创建临时测试项目
@pytest.fixture
def cloud_project(target_workspace: NocoDBWorkspace) -> Generator[NocoDBProject, None, None]:
    """在目标工作区中创建临时测试项目"""
    project_name: str = generate_test_name("test_project")
    project: NocoDBProject = cast(NocoDBProject, target_workspace.create_project(project_name, return_type='object'))
    logger.info(f"Created temporary test project: {project_name} (ID: {project.get_project_id()})")
    
    yield project
    
    # 清理：删除临时项目
    try:
        target_workspace.delete_project(project.get_project_id())
        logger.info(f"Cleaned up temporary project: {project_name}")
    except Exception as e:
        logger.warning(f"Failed to cleanup temporary project: {e}")


# 测试用例
class TestCloudNocoDB:
    """NocoDB 云端实例集成测试"""
    
    def test_list_workspaces(self, client_cloud: NocoDBClient) -> None:
        """测试列出工作区"""
        result: List[Dict[str, Any]] = client_cloud.list_workspaces()
        logger.info(f"Cloud workspaces: {len(result)}")
        for workspace in result:
            logger.info(f"  - {workspace.get('title')} (ID: {workspace.get('id')})")
    
    def test_count_workspaces(self, client_cloud: NocoDBClient) -> None:
        """测试计数工作区"""
        count: Optional[int] = client_cloud.count_workspaces()
        logger.info(f"Cloud workspaces count: {count}")
    
    def test_workspace_operations(self, target_workspace: NocoDBWorkspace) -> None:
        """测试工作区相关操作"""
        count: Optional[int] = target_workspace.count_projects()
        logger.info(f"Projects count in workspace: {count}")
    
    def test_list_projects(self, target_workspace: NocoDBWorkspace) -> None:
        """测试列出云端项目"""
        projects: List[Dict[str, Any]] = target_workspace.list_projects()
        logger.info(f"Cloud projects: {len(projects)}")
        for project in projects:
            logger.info(f"  - {project.get('title')} (ID: {project.get('id')})")
    
    def test_cloud_project_tables(self, cloud_project: NocoDBProject) -> None:
        """测试云端项目表格列表"""
        tables: List[Dict[str, Any]] = cloud_project.list_tables()
        logger.info(f"Cloud project tables count: {len(tables)}")
        for table in tables:
            logger.info(f"  - {table.get('title')} (ID: {table.get('id')})")
    
    def test_project_crud(self, target_workspace: NocoDBWorkspace) -> None:
        """测试项目完整CRUD流程：create, read, update, delete"""
        project_name: str = generate_test_name("test_project")
        updated_project_name: str = generate_test_name("updated_project")
        project_id: Optional[str] = None
        
        try:
            # Step 1: Create project
            logger.info(f"[Step 1] Creating project: {project_name}")
            project: NocoDBProject = cast(NocoDBProject, target_workspace.create_project(project_name, return_type='object'))
            project_id = project.get_project_id()
            logger.success(f"Project created with ID: {project_id}")
            assert project_id is not None, "Project ID should not be None"
            
            # Add a short delay to ensure project is fully created
            import time
            time.sleep(2)
            
            # Step 2: Read created project (verify it exists)
            logger.info(f"[Step 2] Reading created project: {project_id}")
            read_project: NocoDBProject = target_workspace.get_project(project_id)
            project_info: Dict[str, Any] = read_project.get_full_info()
            logger.success(f"Project read successfully, title: {project_info.get('title')}")
            assert read_project.get_project_id() == project_id, "Project ID should match"
            assert project_info.get('title') == project_name, "Project title should match"
            
            # Step 3: Update project
            logger.info(f"[Step 3] Updating project title to: {updated_project_name}")
            updated_project: NocoDBProject = cast(NocoDBProject, target_workspace.update_project(
                project_id,
                title=updated_project_name,
                return_type='object'
            ))
            logger.success("Project updated successfully")
            assert updated_project.get_project_id() == project_id, "Project ID should remain the same"
            
            # Step 4: Read updated project (verify update)
            logger.info(f"[Step 4] Reading updated project: {project_id}")
            read_updated_project: NocoDBProject = target_workspace.get_project(project_id)
            updated_info: Dict[str, Any] = read_updated_project.get_full_info()
            logger.success(f"Updated project read successfully, title: {updated_info.get('title')}")
            assert read_updated_project.get_project_id() == project_id, "Project ID should match"
            assert updated_info.get('title') == updated_project_name, "Project title should be updated"
            
            # Step 5: Delete project
            logger.info(f"[Step 5] Deleting project: {project_id}")
            delete_response: Dict[str, Any] = target_workspace.delete_project(project_id)
            logger.success("Project deleted successfully")
            assert delete_response is not None, "Delete response should not be None"
            
            # Step 6: Verify deleted project (should raise exception when accessing)
            logger.info(f"[Step 6] Attempting to access deleted project: {project_id}")
            with pytest.raises(RequestException):
                deleted_project: NocoDBProject = target_workspace.get_project(project_id)
                deleted_project.get_full_info()
            logger.success("Deleted project access correctly raised exception")
            
            logger.success("All CRUD test steps passed successfully!")
            
        except Exception as e:
            # Cleanup on failure
            if project_id is not None:
                try:
                    logger.warning(f"Cleaning up project {project_id} due to test failure")
                    target_workspace.delete_project(project_id)
                except Exception as cleanup_error:
                    logger.error(f"Cleanup failed: {cleanup_error}")
            raise