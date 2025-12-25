# NocoDB Python SDK

Python SDK for NocoDB - an open-source intelligent spreadsheet and no-code platform for building database applications.

> ⚠️ **Note**: This SDK is in early development stage, and the API may undergo significant changes.

## Features

- **Complete Python client** for interacting with the NocoDB API V2
- **Support for both self-hosted and cloud instances** with automatic deployment mode detection
- **Hierarchical architecture**: Client → Workspace → Project → Table → Column
- **Built-in caching mechanism** with thread-safe implementation and TTL configuration
- **Full type hint support** for better development experience
- **V2 API support** including project creation, table metadata, and column management
- **Copy and serialization support** for all core classes
- **Comprehensive error handling** adapted for V2 API response formats

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

### Create a New Project

```python
# Create project on self-hosted instance
project = client.create_project(
    title="My New Project",
    description="Project description"
)

# Create project in cloud workspace (uses correct API path automatically)
workspace = cloud_client.get_workspace("workspace-id")
project = workspace.create_project(
    title="Cloud Project",
    description="Project in cloud workspace"
)
```

### List Workspaces (Cloud Only)

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

# Get full table metadata
table_info = table.get_full_info()
```

### Column Operations

```python
from nocodb_py import NocoDBColumnType

# List columns with full information
columns = table.list_columns(full_info=True)

# Access column type information
for column in columns:
    column_type = NocoDBColumnType.from_string(column["uidt"])
    print(f"Column: {column['title']}, Type: {column_type.value}")
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
- `create_project(title: str, description: Optional[str] = None)`: Create new project
- `is_cloud()`: Check if instance is NocoDB Cloud
- `server_version()`: Get NocoDB server version

### NocoDBWorkspace

Represents a NocoDB workspace (cloud instances only).

#### Main Methods

- `list_projects()`: List all projects in the workspace
- `get_project(project_id: str)`: Get specific project in the workspace
- `create_project(title: str, description: Optional[str] = None)`: Create project in workspace (inherited with correct API path)

### NocoDBProject

Represents a NocoDB project.

#### Main Methods

- `list_tables()`: List all tables in the project
- `get_table(table_id: str)`: Get specific table in the project
- `get_full_info()`: Get full project information

### NocoDBTable

Represents a NocoDB table.

#### Main Methods

- `list_columns()`: List all columns in the table
- `get_full_info()`: Get full table metadata
- `find_columns_by_title()`: Find columns by title
- `count_columns()`: Count columns in table

### NocoDBColumnType

Enumeration of all NocoDB column types for type-safe operations.

```python
from nocodb_py import NocoDBColumnType

# Available column types
NocoDBColumnType.SINGLE_LINE_TEXT    # SingleLineText
NocoDBColumnType.LONG_TEXT           # LongText
NocoDBColumnType.NUMBER              # Number
NocoDBColumnType.DATE                # Date
NocoDBColumnType.CHECKBOX            # Checkbox
NocoDBColumnType.SINGLE_SELECT       # SingleSelect
# ... and many more
```

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
   pip install -e .[dev]
   ```

### Running Tests

1. Copy test environment configuration:
   ```bash
   cp tests/.env.example tests/.env
   ```

2. Configure your NocoDB instance information in `tests/.env`

3. Run tests:
   ```bash
   python -m pytest tests/
   ```

### Code Quality

The project uses several tools for code quality:

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking (if mypy is configured)
mypy src/
```

## V2 API Support Status

### ✅ Implemented Features
- **Project Management**: Create projects (self-hosted and cloud)
- **Table Operations**: Get table metadata and column information
- **Column Management**: Basic column type enumeration and information
- **Deployment Mode Handling**: Automatic detection of self-hosted vs cloud instances
- **Caching System**: Thread-safe caching with TTL configuration
- **Copy & Serialization**: Full Python copy and pickle support

### ⏳ Planned Features
- **Record Operations**: CRUD operations for table records
- **Advanced Column Operations**: Create, update, delete columns
- **View Management**: Grid, form, gallery, kanban views
- **Filtering & Sorting**: View-level filters and sort rules
- **Link Record Management**: Many-to-many and one-to-many relationships
- **Attachment Upload**: File upload support

## Status

This SDK is in early development stage. Core architecture and V2 API foundation are implemented, but many advanced features are still in development. Not recommended for production use.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.