# create_table 方法使用指南

## 概述

`create_table` 方法允许在 NocoDB 项目中创建新表格。该方法实现了 NocoDB API V2 的表格创建功能，支持灵活的参数配置和返回类型选择。

## 方法签名

```python
def create_table(
    self,
    title: str,
    columns: Optional[List[Dict[str, Any]]] = None,
    table_name: Optional[str] = None,
    description: Optional[str] = None,
    return_type: Literal["object", "json"] = "object"
) -> Union[Dict[str, Any], NocoDBTable]
```

## 参数说明

### 必需参数

- **title** (str): 表格标题，必须是非空字符串（1-128字符）

### 可选参数

- **columns** (Optional[List[Dict]]): 列定义数组，默认值为 `[{"title": "Title", "uidt": "SingleLineText"}]`
  - 每个列必须包含：
    - `title` (str): 列标题，非空字符串
    - `uidt` (Union[str, NocoDBColumnType]): 列类型，支持字符串或枚举值
- **table_name** (Optional[str]): 表格名称，默认值为 `title` 自身
- **description** (Optional[str]): 表格描述
- **return_type** (Literal["object", "json"]): 返回类型，默认值为 "object"
  - "object": 返回 `NocoDBTable` 对象
  - "json": 返回原始 API JSON 响应

## 支持的列类型 (uidt)

### 基础类型（允许创建）

以下基础列类型允许在表格创建时使用：

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
| 单选 | "SingleSelect" | 单选下拉框 |
| 多选 | "MultiSelect" | 多选下拉框 |
| 邮箱 | "Email" | 邮箱地址验证 |
| URL | "URL" | URL地址验证 |
| 电话 | "PhoneNumber" | 电话号码验证 |
| 货币 | "Currency" | 货币金额 |

### 非基础类型（不允许创建）

以下非基础列类型**不允许**在表格创建时使用，需要通过其他方式创建：

- JSON、Geometry、GeoData、QrCode、Barcode、User、Button、Formula、Attachment
- 系统字段：ID、Order、CreatedTime、LastModifiedTime、CreatedBy、LastModifiedBy
- 计算字段：Lookup、Rollup
- 关系字段：Links、LinkToAnotherRecord、ForeignKey

## 使用示例

### 基本用法（使用默认值）

```python
from nocodb_py.client import NocoDBClient
from nocodb_py.project import NocoDBProject

# 初始化客户端和项目
client = NocoDBClient(base_url="https://your-nocodb-instance.com", xc_token="your-api-token")
project = NocoDBProject(client, project_id="your-project-id")

# 创建简单表格（使用所有默认值）
table = project.create_table("Users")
# 默认：table_name="Users", columns=[{"title": "Title", "uidt": "SingleLineText"}], return_type="object"
```

### 使用 NocoDBColumnType 枚举

```python
from nocodb_py.column import NocoDBColumnType

# 使用枚举值定义列
table = project.create_table(
    title="Employees",
    columns=[
        {"title": "Name", "uidt": NocoDBColumnType.SINGLE_LINE_TEXT},
        {"title": "Age", "uidt": NocoDBColumnType.NUMBER},
        {"title": "Email", "uidt": NocoDBColumnType.EMAIL},
        {"title": "Active", "uidt": NocoDBColumnType.CHECKBOX}
    ]
)
```

### 使用字符串类型标识符

```python
# 使用字符串定义列
table = project.create_table(
    title="Products",
    columns=[
        {"title": "Product Name", "uidt": "SingleLineText"},
        {"title": "Price", "uidt": "Currency"},
        {"title": "Stock", "uidt": "Number"},
        {"title": "Created Date", "uidt": "Date"}
    ]
)
```

### 自定义表格名称和描述

```python
table = project.create_table(
    title="Customer Database",
    table_name="customers_table",  # 自定义表格名称
    description="Customer information and contact details",  # 表格描述
    columns=[
        {"title": "Customer ID", "uidt": "SingleLineText"},
        {"title": "Full Name", "uidt": "SingleLineText"},
        {"title": "Email", "uidt": "Email"},
        {"title": "Phone", "uidt": "PhoneNumber"}
    ]
)
```

### 返回 JSON 响应

```python
# 获取原始 API 响应
response = project.create_table(
    title="Test Table",
    return_type="json"  # 返回 JSON 而不是对象
)

print(f"Table created: {response['title']} (ID: {response['id']})")
```

### 混合使用字符串和枚举

```python
from nocodb_py.column import NocoDBColumnType

# 混合使用字符串和枚举
table = project.create_table(
    title="Mixed Types",
    columns=[
        {"title": "Name", "uidt": "SingleLineText"},  # 字符串
        {"title": "Age", "uidt": NocoDBColumnType.NUMBER},  # 枚举
        {"title": "Email", "uidt": "Email"}  # 字符串
    ]
)
```

## 错误处理

### 参数验证错误

```python
try:
    # 空标题会抛出 ValueError
    project.create_table("")
except ValueError as e:
    print(f"Validation error: {e}")

try:
    # 非基础列类型会抛出 ValueError
    project.create_table("Test Table", columns=[{"title": "Formula", "uidt": "Formula"}])
except ValueError as e:
    print(f"Validation error: {e}")

try:
    # 无效的列类型会抛出 ValueError
    project.create_table("Test Table", columns=[{"title": "Test", "uidt": "InvalidType"}])
except ValueError as e:
    print(f"Validation error: {e}")
```

### API 错误

```python
try:
    table = project.create_table(
        title="Test Table",
        columns=[{"title": "Name", "uidt": "SingleLineText"}]
    )
except Exception as e:
    print(f"API error: {e}")
```

### 无效的 return_type

```python
try:
    # 无效的 return_type 会抛出 ValueError
    result = project.create_table("Test Table", return_type="invalid")
except ValueError as e:
    print(f"Validation error: {e}")
```

## 返回值

### 返回 NocoDBTable 对象 (return_type="object")

默认返回类型，提供面向对象的接口：

```python
table = project.create_table("Users")  # 默认 return_type="object"

# 使用表格对象的方法
records = table.list_records()
count = table.count_records()
```

### 返回 JSON 响应 (return_type="json")

返回原始 API 响应数据：

```python
response = project.create_table("Users", return_type="json")

# 直接访问响应数据
table_id = response["id"]
table_title = response["title"]
columns = response["columns"]
```

## 缓存处理

创建表格后，方法会自动清除项目的表格缓存，确保后续的表格列表查询能获取到最新数据。

## 最佳实践

1. **列命名**: 使用清晰、一致的列标题
2. **列类型选择**: 根据数据类型选择合适的列类型，只使用基础类型
3. **表格命名**: 使用有意义的表格名称，便于识别和管理
4. **错误处理**: 始终处理可能的验证和API错误
5. **返回类型选择**: 
   - 使用 "object" 进行后续表格操作
   - 使用 "json" 获取创建详情或进行自定义处理
6. **测试**: 在生产环境使用前，先在测试环境中验证表格创建

## 相关方法

- `list_tables()`: 列出项目中的所有表格
- `get_table()`: 获取特定表格对象
- `count_tables()`: 统计表格数量
- `find_tables_by_title()`: 根据标题查找表格