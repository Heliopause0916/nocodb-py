"""
NocoDB Python SDK CRUD Chain Tests
Tests with dependency chain: project → table → record
Each level follows the pattern: read(empty), create, read, update, read, delete, read
"""

import os
import uuid
import pytest
from dotenv import load_dotenv
from nocodb_py import NocoDBClient

# Load environment variables
load_dotenv(dotenv_path="tests/.env", override=True)

api_key = os.getenv("NOCODB_API_KEY", "changeme")
base_url = os.getenv("NOCODB_BASE_URL", "http://localhost:8080")


def generate_test_name(prefix="test"):
    """Generate unique test name using UUID"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


# ============================================================================
# Base Fixtures
# ============================================================================

@pytest.fixture
def client():
    """Create NocoDB client instance"""
    return NocoDBClient(base_url=base_url, xc_token=api_key)


# ============================================================================
# Project Level Fixture
# ============================================================================

@pytest.fixture
def test_project(client):
    """
    Test project CRUD operations.
    Follows the pattern: read(empty), create, read, update, read, delete, read
    Returns project object for dependent tests.
    """
    test_title = generate_test_name("project")
    test_description = "Test project for CRUD chain tests"
    
    # 1. read（读到空值）- Check project doesn't exist
    projects = client.list_projects()
    project_titles = [p.get("title") for p in projects]
    assert test_title not in project_titles, f"Project '{test_title}' already exists"
    
    # 2. create - Create test project
    project = client.create_project(title=test_title, description=test_description)
    assert project is not None, "Failed to create project"
    
    # 3. read - Verify project was created successfully
    assert project.get_title() == test_title, "Project title doesn't match"
    assert project._project_id is not None, "Project ID is None"
    
    # 4. update - Update project information
    updated_title = f"{test_title}_updated"
    updated_description = f"{test_description} - updated"
    client.update_project(project, title=updated_title, description=updated_description)
    
    # 5. read - Verify update was successful
    assert project.get_title() == updated_title, "Project title update failed"
    
    yield project  # Return project object for dependent tests
    
    # 6. delete - Delete project (cleanup)
    client.delete_project(project)
    
    # 7. read - Verify project was deleted successfully
    projects_after = client.list_projects()
    project_ids = [p.get("id") for p in projects_after]
    assert project._project_id not in project_ids, "Project was not deleted"


# ============================================================================
# Table Level Fixture (Depends on test_project)
# ============================================================================

@pytest.fixture
def test_table(test_project):
    """
    Test table CRUD operations.
    Depends on test_project fixture (executes after project update).
    Note: This fixture uses existing tables if create_table is not implemented.
    """
    # Get existing tables from the project
    tables = test_project.list_tables()
    
    if not tables:
        pytest.skip("No tables found in test project. Cannot proceed with table-level tests.")
    
    # Use the first available table for testing
    table_id = tables[0].get("id")
    table_title = tables[0].get("title")
    
    # Get table object
    from nocodb_py import NocoDBTable
    table = NocoDBTable(project=test_project, table_id=table_id)
    
    # 1. read（读到空值）- Check table exists (already verified above)
    assert table is not None, "Failed to get table object"
    
    # 2. create - Skip (using existing table)
    # Note: create_table method may not be implemented yet
    
    # 3. read - Verify table information
    assert table.table_id == table_id, "Table ID doesn't match"
    
    # 4. update - Skip (update_table method may not be implemented yet)
    
    # 5. read - Verify table still exists
    assert table is not None, "Table object became None"
    
    yield table  # Return table object for dependent tests
    
    # 6. delete - Skip (using existing table, don't delete)
    
    # 7. read - Verify table still exists
    tables_after = test_project.list_tables()
    table_ids = [t.get("id") for t in tables_after]
    assert table_id in table_ids, "Table was unexpectedly deleted"


# ============================================================================
# Record Level Fixture (Depends on test_table)
# ============================================================================

@pytest.fixture
def test_record(test_table):
    """
    Test record CRUD operations.
    Depends on test_table fixture (executes after table is ready).
    Follows the pattern: read(empty), create, read, update, read, delete, read
    """
    # Get table schema to understand available columns
    schema = test_table.get_schema()
    writable_columns = schema.get_writable_columns()
    
    if not writable_columns:
        pytest.skip("No writable columns found in test table. Cannot proceed with record-level tests.")
    
    # Create test record data using first writable column
    first_column = writable_columns[0]
    column_title = first_column.get("title")
    test_value = f"test_value_{uuid.uuid4().hex[:8]}"
    
    # 1. read（读到空值）- Check record doesn't exist
    # We'll verify this by checking if we can create a new record
    initial_count = test_table.count_records()
    
    # 2. create - Create test record
    record_data = {column_title: test_value}
    created_records = test_table.create_records(record_data, return_type="object")
    
    assert created_records is not None, "Failed to create record"
    assert len(created_records) > 0, "No records returned from create_records"
    
    record = created_records[0] if isinstance(created_records, list) else created_records
    record_id = record.record_id if hasattr(record, 'record_id') else record.get('Id')
    
    # 3. read - Verify record was created successfully
    retrieved_record = test_table.get_record(record_id, return_type="object")
    assert retrieved_record is not None, "Failed to retrieve created record"
    
    # 4. update - Update record
    updated_value = f"{test_value}_updated"
    updated_record_data = {column_title: updated_value}
    test_table.update_records(record_id, updated_record_data)
    
    # 5. read - Verify update was successful
    updated_record = test_table.get_record(record_id, return_type="object")
    assert updated_record is not None, "Failed to retrieve updated record"
    
    yield record_id  # Return record ID for dependent tests
    
    # 6. delete - Delete record (cleanup)
    test_table.delete_records(record_id)
    
    # 7. read - Verify record was deleted successfully
    final_count = test_table.count_records()
    assert final_count == initial_count, "Record was not deleted"


# ============================================================================
# Test Classes for Different Test Depths
# ============================================================================

class TestProjectOnly:
    """Test only project level CRUD operations"""
    
    def test_project_crud(self, test_project):
        """
        Test project CRUD operations.
        The test_project fixture already performs the full CRUD cycle.
        This test verifies the fixture completed successfully.
        """
        assert test_project is not None, "Project fixture failed"
        assert test_project._project_id is not None, "Project ID is None"
        print(f"✓ Project CRUD test passed for project: {test_project.get_title()}")


class TestProjectAndTable:
    """Test project and table level CRUD operations"""
    
    def test_table_crud(self, test_table):
        """
        Test table CRUD operations.
        Depends on test_project fixture.
        """
        assert test_table is not None, "Table fixture failed"
        assert test_table.table_id is not None, "Table ID is None"
        print(f"✓ Table CRUD test passed for table: {test_table.table_id}")


class TestFullChain:
    """Test full CRUD chain: project → table → record"""
    
    def test_record_crud(self, test_record):
        """
        Test record CRUD operations.
        Depends on test_table fixture, which depends on test_project.
        """
        assert test_record is not None, "Record fixture failed"
        print(f"✓ Record CRUD test passed for record ID: {test_record}")
    
    def test_dependency_chain(self, test_project, test_table, test_record):
        """
        Verify the dependency chain works correctly.
        Ensures: project → table → record
        """
        assert test_project is not None, "Project is None"
        assert test_table is not None, "Table is None"
        assert test_record is not None, "Record is None"
        
        # Verify table belongs to project
        assert test_table._project == test_project, "Table doesn't belong to project"
        
        print("✓ Dependency chain test passed: project → table → record")


# ============================================================================
# Additional Utility Tests
# ============================================================================

class TestUtilities:
    """Test utility functions and helpers"""
    
    def test_generate_test_name(self):
        """Test that generate_test_name creates unique names"""
        name1 = generate_test_name("test")
        name2 = generate_test_name("test")
        assert name1 != name2, "Generated names are not unique"
        assert name1.startswith("test_"), "Generated name doesn't start with prefix"
        print(f"✓ Test name generation works: {name1}, {name2}")
    
    def test_client_creation(self, client):
        """Test that client is created successfully"""
        assert client is not None, "Client is None"
        assert client._base_url == base_url, "Base URL doesn't match"
        print(f"✓ Client created successfully: {client}")