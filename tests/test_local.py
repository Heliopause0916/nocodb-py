# test_local.py - 本地实例测试
# pylint: disable=all
import os
import uuid
import json
import pytest
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple, cast
from dotenv import load_dotenv
from loguru import logger
from nocodb_py import NocoDBClient, NocoDBProject
from requests.exceptions import RequestException

# 获取当前文件路径
current_file_path = Path(__file__).resolve()

# 加载环境变量
env_file_path = current_file_path.parent / ".env"
load_dotenv(dotenv_path=env_file_path, override=True)

api_key = os.getenv("NOCODB_API_KEY", "changeme")
base_url = os.getenv("NOCODB_BASE_URL", "http://localhost:8080")

# 配置loguru日志
log_file_path = current_file_path.parent / "test_local.log"

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
client_instance = NocoDBClient(base_url=base_url, xc_token=api_key)
print_client_info(client_instance)

# Fixture：创建本地客户端
@pytest.fixture
def client() -> NocoDBClient:
    return client_instance


# 测试用例
class TestLocalNocoDB:
    """NocoDB 本地实例集成测试"""
    
    def test_count_projects(self, client: NocoDBClient) -> None:
        """测试计数本地项目"""
        count: Optional[int] = client.count_projects()
        logger.info(f"Local projects count: {count}")
    
    def test_list_projects(self, client: NocoDBClient) -> None:
        """测试列出本地项目"""
        projects: List[Dict[str, Any]] = client.list_projects()
        logger.info(f"Local projects: {len(projects)}")
    
    def test_project_crud(self, client: NocoDBClient) -> None:
        """测试项目完整CRUD流程：create, read, update, delete"""
        project_name: str = generate_test_name("test_project")
        updated_project_name: str = generate_test_name("updated_project")
        project_id: Optional[str] = None
        
        try:
            # Step 1: Create project
            logger.info(f"[Step 1] Creating project: {project_name}")
            project: NocoDBProject = cast(NocoDBProject, client.create_project(project_name, return_type='object'))
            project_id = project.get_project_id()
            logger.success(f"Project created with ID: {project_id}")
            assert project_id is not None, "Project ID should not be None"
            
            # Step 2: Read created project (verify it exists)
            logger.info(f"[Step 2] Reading created project: {project_id}")
            read_project: NocoDBProject = client.get_project(project_id)
            project_info = read_project.get_full_info()
            logger.success(f"Project read successfully, title: {project_info.get('title')}")
            assert read_project.get_project_id() == project_id, "Project ID should match"
            assert project_info.get('title') == project_name, "Project title should match"
            
            # Step 3: Update project
            logger.info(f"[Step 3] Updating project title to: {updated_project_name}")
            updated_project: NocoDBProject = cast(NocoDBProject, client.update_project(
                project_id,
                title=updated_project_name,
                return_type='object'
            ))
            logger.success("Project updated successfully")
            assert updated_project.get_project_id() == project_id, "Project ID should remain the same"
            
            # Step 4: Read updated project (verify update)
            logger.info(f"[Step 4] Reading updated project: {project_id}")
            read_updated_project: NocoDBProject = client.get_project(project_id)
            updated_info = read_updated_project.get_full_info()
            logger.success(f"Updated project read successfully, title: {updated_info.get('title')}")
            assert read_updated_project.get_project_id() == project_id, "Project ID should match"
            assert updated_info.get('title') == updated_project_name, "Project title should be updated"
            
            # Step 5: Delete project
            logger.info(f"[Step 5] Deleting project: {project_id}")
            delete_response: Dict[str, Any] = client.delete_project(project_id)
            logger.success("Project deleted successfully")
            assert delete_response is not None, "Delete response should not be None"
            
            # Step 6: Verify deleted project (should raise exception when accessing)
            logger.info(f"[Step 6] Attempting to access deleted project: {project_id}")
            with pytest.raises(RequestException):
                deleted_project = client.get_project(project_id)
                deleted_project.get_full_info()
            logger.success("Deleted project access correctly raised exception")
            
            logger.success("All CRUD test steps passed successfully!")
            
        except Exception as e:
            # Cleanup on failure
            if project_id is not None:
                try:
                    logger.warning(f"Cleaning up project {project_id} due to test failure")
                    client.delete_project(project_id)
                except Exception as cleanup_error:
                    logger.error(f"Cleanup failed: {cleanup_error}")
            raise