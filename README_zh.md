# NocoDB Python SDK

Python SDK for NocoDB - 一个开源的智能电子表格和无代码平台，用于构建数据库应用程序。

> ⚠️ **注意**: 此SDK处于早期开发阶段，API可能会发生重大变化。

## 功能特性

- **完整的Python客户端**，用于与NocoDB API V2交互
- **支持自托管和云实例**，自动检测部署模式
- **分层架构**：客户端 → 工作区 → 项目 → 表格 → 列
- **内置缓存机制**，线程安全实现，支持TTL配置
- **完整的类型提示支持**，提供更好的开发体验
- **V2 API支持**，包括项目创建、表格元数据和列管理
- **拷贝和序列化支持**，所有核心类支持Python标准操作
- **全面的错误处理**，适配V2 API响应格式

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

### 创建新项目

```python
# 在自托管实例上创建项目
project = client.create_project(
    title="我的新项目",
    description="项目描述"
)

# 在云工作区中创建项目（自动使用正确的API路径）
workspace = cloud_client.get_workspace("workspace-id")
project = workspace.create_project(
    title="云项目",
    description="云工作区中的项目"
)
```

### 列出工作区（仅限云实例）

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

# 获取完整表格元数据
table_info = table.get_full_info()
```

### 列操作

```python
from nocodb_py import NocoDBColumnType

# 列出包含完整信息的列
columns = table.list_columns(full_info=True)

# 访问列类型信息
for column in columns:
    column_type = NocoDBColumnType.from_string(column["uidt"])
    print(f"列: {column['title']}, 类型: {column_type.value}")
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
- `create_project(title: str, description: Optional[str] = None)`: 创建新项目
- `is_cloud()`: 检查实例是否为NocoDB云实例
- `server_version()`: 获取NocoDB服务器版本

### NocoDBWorkspace

表示NocoDB工作区（仅限云实例）。

#### 主要方法

- `list_projects()`: 列出工作区中的所有项目
- `get_project(project_id: str)`: 获取工作区中的特定项目
- `create_project(title: str, description: Optional[str] = None)`: 在工作区中创建项目（继承并自动使用正确的API路径）

### NocoDBProject

表示NocoDB项目。

#### 主要方法

- `list_tables()`: 列出项目中的所有表格
- `get_table(table_id: str)`: 获取项目中的特定表格
- `get_full_info()`: 获取完整项目信息

### NocoDBTable

表示NocoDB表格。

#### 主要方法

- `list_columns()`: 列出表格中的所有列
- `get_full_info()`: 获取完整表格元数据
- `find_columns_by_title()`: 按标题查找列
- `count_columns()`: 统计表格中的列数

### NocoDBColumnType

所有NocoDB列类型的枚举，用于类型安全操作。

```python
from nocodb_py import NocoDBColumnType

# 可用的列类型
NocoDBColumnType.SINGLE_LINE_TEXT    # 单行文本
NocoDBColumnType.LONG_TEXT           # 长文本
NocoDBColumnType.NUMBER              # 数字
NocoDBColumnType.DATE                # 日期
NocoDBColumnType.CHECKBOX            # 复选框
NocoDBColumnType.SINGLE_SELECT       # 单选
# ... 以及更多
```

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
   pip install -e .[dev]
   ```

### 运行测试

1. 复制测试环境配置:
   ```bash
   cp tests/.env.example tests/.env
   ```

2. 在 `tests/.env` 中配置你的NocoDB实例信息

3. 运行测试:
   ```bash
   python -m pytest tests/
   ```

### 代码质量

项目使用多种工具保证代码质量：

```bash
# 格式化代码
black src/ tests/

# 代码检查
ruff check src/ tests/

# 类型检查（如果配置了mypy）
mypy src/
```

## V2 API支持状态

### ✅ 已实现功能
- **项目管理**: 创建项目（自托管和云实例）
- **表格操作**: 获取表格元数据和列信息
- **列管理**: 基础列类型枚举和信息获取
- **部署模式处理**: 自动检测自托管与云实例
- **缓存系统**: 线程安全缓存，支持TTL配置
- **拷贝与序列化**: 完整的Python拷贝和pickle支持

### ⏳ 计划功能
- **记录操作**: 表格记录的CRUD操作
- **高级列操作**: 创建、更新、删除列
- **视图管理**: 网格视图、表单视图、画廊视图、看板视图
- **过滤与排序**: 视图级别的过滤条件和排序规则
- **链接记录管理**: 多对多和一对多关系
- **附件上传**: 文件上传支持

## 状态

此SDK处于早期开发阶段。核心架构和V2 API基础已实现，但许多高级功能仍在开发中。不建议在生产环境中使用。

## 许可证

本项目采用MIT许可证。详情请见 [LICENSE](LICENSE) 文件。