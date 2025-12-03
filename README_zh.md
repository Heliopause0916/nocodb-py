# NocoDB Python SDK

Python SDK for NocoDB - 一个开源的智能电子表格和无代码平台，用于构建数据库应用程序。

> ⚠️ **注意**: 此SDK处于早期开发阶段，API可能会发生重大变化。

## 功能特性

- 与NocoDB API交互的Python客户端
- 支持工作区、项目和表格操作
- 内置缓存机制提高性能
- 类型提示支持

## 安装

### 要求

- Python 3.9 或更高版本

### 安装方式

```bash
pip install nocodb-py
```

或者从源码安装：

```bash
pip install git+https://github.com/your-username/nocodb-py.git
```

## 快速开始

### 初始化客户端

```python
from nocodb_py import NocoDBClient

# 自托管实例
client = NocoDBClient(
    base_url="http://localhost:8080",
    xc_token="your-api-token"
)

# NocoDB云实例
cloud_client = NocoDBClient(
    base_url="https://app.nocodb.com",
    xc_token="your-cloud-api-token"
)
```

### 列出工作区

```python
# 仅适用于云实例
workspaces = cloud_client.list_workspaces()
print(workspaces)
```

### 获取工作区

```python
# 仅适用于云实例
workspace = cloud_client.get_workspace("workspace-id")
```

### 列出项目

```python
# 自托管实例
projects = client.list_projects()

# 云实例中的特定工作区
projects = workspace.list_projects()
```

### 获取项目

```python
project = client.get_project("project-id")
# 或者从工作区获取
project = workspace.get_project("project-id")
```

### 表格操作

```python
# 获取项目中的表格
tables = project.list_tables()

# 获取特定表格
table = project.get_table("table-id")

# 获取表格列信息
columns = table.list_columns()
```

## API参考

### NocoDBClient

主要客户端类，用于与NocoDB实例交互。

#### 构造函数

```python
NocoDBClient(base_url: str, xc_token: str, cache_ttl: Optional[int] = 300, timeout = 10)
```

参数:
- `base_url`: NocoDB实例的基础URL
- `xc_token`: API认证令牌
- `cache_ttl`: 缓存过期时间（秒），None表示永不过期
- `timeout`: 请求超时时间（秒）

#### 主要方法

- `list_workspaces()`: 列出所有工作区（仅限云实例）
- `get_workspace(workspace_id: str)`: 获取特定工作区（仅限云实例）
- `list_projects()`: 列出所有项目
- `get_project(project_id: str)`: 获取特定项目

### NocoDBWorkspace

表示NocoDB工作区（仅限云实例）。

#### 主要方法

- `list_projects()`: 列出工作区中的所有项目
- `get_project(project_id: str)`: 获取工作区中的特定项目

### NocoDBProject

表示NocoDB项目。

#### 主要方法

- `list_tables()`: 列出项目中的所有表格
- `get_table(table_id: str)`: 获取项目中的特定表格

### NocoDBTable

表示NocoDB表格。

#### 主要方法

- `list_columns()`: 列出表格中的所有列
- `get_full_info()`: 获取表格的完整信息

## 开发

### 设置开发环境

1. 克隆仓库:
   ```bash
   git clone https://github.com/your-username/nocodb-py.git
   cd nocodb-py
   ```

2. 创建虚拟环境:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate  # Windows
   ```

3. 安装依赖:
   ```bash
   pip install -e .
   ```

### 运行测试

1. 复制测试环境配置:
   ```bash
   cp tests/.env.example tests/.env
   ```

2. 在 `tests/.env` 中配置你的NocoDB实例信息

3. 运行测试:
   ```bash
   python tests/test.py
   ```

## 状态

此SDK处于早期开发阶段，API可能会发生变化。不建议在生产环境中使用。

## 许可证

本项目采用MIT许可证。详情请见 [LICENSE](LICENSE) 文件。