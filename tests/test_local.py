# test_local.py - 本地实例测试
# pylint: disable=all
import os
import uuid
import json
import pytest
from typing import Optional, Dict, List, Any, Tuple, cast
from dotenv import load_dotenv
from nocodb_py import NocoDBClient, NocoDBProject
from requests.exceptions import RequestException

# 加载环境变量
load_dotenv(dotenv_path="tests/.env", override=True)

api_key = os.getenv("NOCODB_API_KEY", "changeme")
base_url = os.getenv("NOCODB_BASE_URL", "http://localhost:8080")


def generate_test_name(prefix: str = "test") -> str:
    """Generate unique test name using UUID"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


# Fixture：创建本地客户端
@pytest.fixture
def client() -> NocoDBClient:
    return NocoDBClient(base_url=base_url, xc_token=api_key)


# 测试用例
class TestLocalNocoDB:
    """NocoDB 本地实例集成测试"""
    
    def test_count_projects(self, client: NocoDBClient) -> None:
        """测试计数本地项目"""
        count: Optional[int] = client.count_projects()
        print(f"Local projects count: {count}")
    
    def test_list_projects(self, client: NocoDBClient) -> None:
        """测试列出本地项目"""
        projects: List[Dict[str, Any]] = client.list_projects()
        print(f"Local projects: {len(projects)}")
    
    def test_project_crud(self, client: NocoDBClient) -> None:
        """测试项目完整CRUD流程：read(empty), create, read, update, read, delete, read"""
        project_name: str = generate_test_name("test_project")
        updated_project_name: str = generate_test_name("updated_project")
        project_id: Optional[str] = None
        
        try:
            # Step 1: Read non-existent project (should raise exception)
            print(f"\n[Step 1] Attempting to read non-existent project: {project_name}")
            with pytest.raises(RequestException):
                client.get_project("non_existent_project_id_12345")
            print("✓ Non-existent project read correctly raised exception")
            
            # Step 2: Create project
            print(f"\n[Step 2] Creating project: {project_name}")
            project: NocoDBProject = cast(NocoDBProject, client.create_project(project_name, return_type='object'))
            project_id = project.get_project_id()
            print(f"✓ Project created with ID: {project_id}")
            assert project_id is not None, "Project ID should not be None"
            
            # Step 3: Read created project
            print(f"\n[Step 3] Reading created project: {project_id}")
            read_project: NocoDBProject = client.get_project(project_id)
            print(f"✓ Project read successfully")
            assert read_project.get_project_id() == project_id, "Project ID should match"
            
            # Step 4: Update project
            print(f"\n[Step 4] Updating project title to: {updated_project_name}")
            updated_project: NocoDBProject = cast(NocoDBProject, client.update_project(
                project_id,
                title=updated_project_name,
                return_type='object'
            ))
            print(f"✓ Project updated successfully")
            assert updated_project.get_project_id() == project_id, "Project ID should remain the same"
            
            # Step 5: Read updated project
            print(f"\n[Step 5] Reading updated project: {project_id}")
            read_updated_project: NocoDBProject = client.get_project(project_id)
            print(f"✓ Updated project read successfully")
            assert read_updated_project.get_project_id() == project_id, "Project ID should match"
            
            # Step 6: Delete project
            print(f"\n[Step 6] Deleting project: {project_id}")
            delete_response: Dict[str, Any] = client.delete_project(project_id)
            print(f"✓ Project deleted successfully")
            assert delete_response is not None, "Delete response should not be None"
            
            # Step 7: Read deleted project (should raise exception)
            print(f"\n[Step 7] Attempting to read deleted project: {project_id}")
            with pytest.raises(RequestException):
                client.get_project(project_id)
            print("✓ Deleted project read correctly raised exception")
            
            print("\n✅ All CRUD test steps passed successfully!")
            
        except Exception as e:
            # Cleanup on failure
            if project_id is not None:
                try:
                    print(f"\n⚠️ Cleaning up project {project_id} due to test failure")
                    client.delete_project(project_id)
                except Exception as cleanup_error:
                    print(f"⚠️ Cleanup failed: {cleanup_error}")
            raise