# create_table 方法使用指南

## 概述

`create_table` 方法允许在 NocoDB 项目中创建新表格。该方法实现了 NocoDB API V2 的表格创建功能。

## 方法签名

```python
def create_table(
    self,
    title: str,
    columns: List[Dict[str, Any]],
    table_name: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Any]
```

## 参数说明

### 必需参数

- **title** (str): 表格标题，必须是非空字符串（1-128字符）
- **columns** (List[Dict]): 列定义数组，每个列必须包含：
  - `title` (str): 列标题，非空字符串
  - `uidt` (str): 列类型标识符，如 "SingleLineText", "Number", "Date" 等

### 可选参数

- **table_name** (Optional[str]): 表格名称，如果提供必须是非空字符串
- **description** (Optional[str]): 表格描述，如果提供必须是非空字符串

## 支持的列类型 (uidt)

以下是一些常用的列类型标识符：

| 列类型 | uidt 值 | 说明 |
|--------|---------|------|
| 单行文本 | "SingleLineText" | 单行文本输入 |
| 长文本 | "LongText" | 多行文本输入 |
| 数字 | "Number" | 数值输入 |
| 小数 | "Decimal" | 高精度小数 |
| 百分比 | "Percent" | 百分比值 |
| 评分 | "Rating" | 评分控件（0-10） |
| 日期 | "Date" | 日期选择器 |
| 时间 | "Time" | 时间选择器 |
| 日期时间 | "DateTime" | 日期时间选择器 |
| 年份 | "Year" | 年份选择器 |
| 时长 | "Duration" | 时长输入 |
| 复选框 | "Checkbox" | 布尔值复选框 |
| 邮箱 | "Email" | 邮箱地址验证 |
| URL | "URL" | URL地址验证 |
| 电话 | "PhoneNumber" | 电话号码验证 |
| 货币 | "Currency" | 货币金额 |

## 使用示例

### 基本用法

```python
from nocodb_py.client import NocoDBClient
from nocodb_py.project import NocoDBProject

# 初始化客户端和项目
client = NocoDBClient(base_url="https://your-nocodb-instance.com", xc_token="your-api-token")
project = NocoDBProject(client, project_id="your-project-id")

# 创建简单表格
table_info = project.create_table(
    title="Users",
    columns=[
        {"title": "Name", "uidt": "SingleLineText"},
        {"title": "Age", "uidt": "Number"},
        {"title": "Email", "uidt": "Email"}
    ]
)

print(f"Created table: {table_info['title']} (ID: {table_info['id']})")
```

### 带可选参数的用法

```python
# 创建带可选参数的表格
table_info = project.create_table(
    title="Products",
    table_name="products_table",
    description="Product inventory management",
    columns=[
        {"title": "Product Name", "uidt": "SingleLineText"},
        {"title": "Price", "uidt": "Currency"},
        {"title": "Stock", "uidt": "Number"},
        {"title": "Created Date", "uidt": "Date"},
        {"title": "Active", "uidt": "Checkbox"}
    ]
)
```

### 复杂列类型示例

```python
# 使用多种列类型
table_info = project.create_table(
    title="Employee Records",
    columns=[
        {"title": "Employee ID", "uidt": "SingleLineText"},
        {"title": "Full Name", "uidt": "SingleLineText"},
        {"title": "Department", "uidt": "SingleLineText"},
        {"title": "Salary", "uidt": "Currency"},
        {"title": "Hire Date", "uidt": "Date"},
        {"title": "Performance Rating", "uidt": "Rating"},
        {"title": "Notes", "uidt": "LongText"},
        {"title": "Is Active", "uidt": "Checkbox"}
    ]
)
```

## 错误处理

### 参数验证错误

```python
try:
    # 空标题会抛出 ValueError
    project.create_table("", [{"title": "Name", "uidt": "SingleLineText"}])
except ValueError as e:
    print(f"Validation error: {e}")

try:
    # 空列列表会抛出 ValueError
    project.create_table("Test Table", [])
except ValueError as e:
    print(f"Validation error: {e}")

try:
    # 缺少 uidt 会抛出 ValueError
    project.create_table("Test Table", [{"title": "Name"}])
except ValueError as e:
    print(f"Validation error: {e}")
```

### API 错误

```python
try:
    table_info = project.create_table(
        title="Test Table",
        columns=[{"title": "Name", "uidt": "SingleLineText"}]
    )
except Exception as e:
    print(f"API error: {e}")
```

## 返回值

方法返回包含创建表格信息的字典，通常包含以下字段：

- `id`: 表格ID
- `title`: 表格标题
- `table_name`: 表格名称
- `description`: 表格描述
- `columns`: 列定义数组
- `created_at`: 创建时间
- `updated_at`: 更新时间

## 缓存处理

创建表格后，方法会自动清除项目的表格缓存，确保后续的表格列表查询能获取到最新数据。

## 最佳实践

1. **列命名**: 使用清晰、一致的列标题
2. **列类型选择**: 根据数据类型选择合适的列类型
3. **错误处理**: 始终处理可能的验证和API错误
4. **缓存管理**: 创建表格后不需要手动清除缓存，方法已自动处理
5. **测试**: 在生产环境使用前，先在测试环境中验证表格创建

## 相关方法

- `list_tables()`: 列出项目中的所有表格
- `get_table()`: 获取特定表格对象
- `count_tables()`: 统计表格数量
- `find_tables_by_title()`: 根据标题查找表格