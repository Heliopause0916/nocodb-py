# NocoDB Python SDK

Python SDK for NocoDB - an open-source intelligent spreadsheet and no-code platform for building database applications.

> ⚠️ **Note**: This SDK is in early development stage, and the API may undergo significant changes.

## Features

- Python client for interacting with the NocoDB API
- Support for workspace, project, and table operations
- Built-in caching mechanism for improved performance
- Type hint support

## Installation

### Requirements

- Python 3.9 or higher

### Installation Method

```bash
pip install nocodb-py
```

Or install from source:

```bash
pip install git+https://github.com/your-username/nocodb-py.git
```

## Quick Start

### Initialize Client

```python
from nocodb_py import NocoDBClient

# Self-hosted instance
client = NocoDBClient(
    base_url="http://localhost:8080",
    xc_token="your-api-token"
)

# NocoDB cloud instance
cloud_client = NocoDBClient(
    base_url="https://app.nocodb.com",
    xc_token="your-cloud-api-token"
)
```

### List Workspaces

```python
# Only for cloud instances
workspaces = cloud_client.list_workspaces()
print(workspaces)
```

### Get Workspace

```python
# Only for cloud instances
workspace = cloud_client.get_workspace("workspace-id")
```

### List Projects

```python
# Self-hosted instance
projects = client.list_projects()

# Specific workspace in cloud instance
projects = workspace.list_projects()
```

### Get Project

```python
project = client.get_project("project-id")
# Or get from workspace
project = workspace.get_project("project-id")
```

### Table Operations

```python
# Get tables in project
tables = project.list_tables()

# Get specific table
table = project.get_table("table-id")

# Get table column information
columns = table.list_columns()
```

## API Reference

### NocoDBClient

Main client class for interacting with NocoDB instances.

#### Constructor

```python
NocoDBClient(base_url: str, xc_token: str, cache_ttl: Optional[int] = 300, timeout = 10)
```

Parameters:
- `base_url`: Base URL of the NocoDB instance
- `xc_token`: API authentication token
- `cache_ttl`: Cache expiration time (seconds), None means never expires
- `timeout`: Request timeout time (seconds)

#### Main Methods

- `list_workspaces()`: List all workspaces (cloud instances only)
- `get_workspace(workspace_id: str)`: Get specific workspace (cloud instances only)
- `list_projects()`: List all projects
- `get_project(project_id: str)`: Get specific project

### NocoDBWorkspace

Represents a NocoDB workspace (cloud instances only).

#### Main Methods

- `list_projects()`: List all projects in the workspace
- `get_project(project_id: str)`: Get specific project in the workspace

### NocoDBProject

Represents a NocoDB project.

#### Main Methods

- `list_tables()`: List all tables in the project
- `get_table(table_id: str)`: Get specific table in the project

### NocoDBTable

Represents a NocoDB table.

#### Main Methods

- `list_columns()`: List all columns in the table
- `get_full_info()`: Get full information of the table

## Development

### Setting up Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/nocodb-py.git
   cd nocodb-py
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```

### Running Tests

1. Copy test environment configuration:
   ```bash
   cp tests/.env.example tests/.env
   ```

2. Configure your NocoDB instance information in `tests/.env`

3. Run tests:
   ```bash
   python tests/test.py
   ```

## Status

This SDK is in early development stage, and the API may change. Not recommended for production use.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.