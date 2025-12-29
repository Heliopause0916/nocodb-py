# NocoDBSchema 离线状态功能文档

## 概述

NocoDBSchema 类现在支持离线状态（Detached）和在线状态（Attached）两种模式，参考了 NocoDBRecord 的 `attach` 思想。这使得开发者可以在本地设计表结构，然后再将其附加到实际的 NocoDB 表上。

## 设计理念

### 状态管理
- **离线状态 (Detached)**: `table` 为 `None`，所有与列ID或table相关的成员保持为 `None`
- **在线状态 (Attached)**: `table` 不为 `None`，可以正常访问所有列信息

### 简化存储结构
基于用户建议，简化了内部存储结构：
- 移除了 `_columns_info` 成员（可以从table获取）
- 将 `_offline_columns` 与 `_column_types_by_title` 合并
- 暂时不考虑metadata，只存储列类型

## 核心功能

### 状态管理方法

```python
# 创建离线Schema
schema = NocoDBSchema()  # table=None

# 状态检查
schema.is_attached  # False
schema.is_detached  # True

# 附加到表（一次性操作）
schema.attach(table_object)
```

### 离线列管理

```python
# 添加列（仅支持basic类型）
schema.add_column("name", NocoDBColumnType.SINGLE_LINE_TEXT)
schema.add_column("age", NocoDBColumnType.NUMBER)

# 更新列类型
schema.update_column("age", NocoDBColumnType.DECIMAL)

# 删除列
schema.remove_column("email")

# 获取离线列定义
schema.offline_columns  # {'name': SINGLE_LINE_TEXT, 'age': DECIMAL}
```

### Schema同步机制

```python
# 通过load_schema进行attach操作
schema.load_schema(table=table_object)  # 一次性attach

# 同步过程中的冲突处理：
# 1. 已存在且类型匹配：赋予列ID（自然处理）
# 2. 已存在且类型不匹配：警告并强制修改类型与table匹配
# 3. table中存在但离线不存在：创建此列
# 4. table中不存在但离线存在：警告并删除此列
```

## 使用示例

### 基本用法
```python
from nocodb_py.column import NocoDBSchema, NocoDBColumnType

# 创建离线Schema
schema = NocoDBSchema()

# 设计表结构
schema.add_column("name", NocoDBColumnType.SINGLE_LINE_TEXT)
schema.add_column("age", NocoDBColumnType.NUMBER)
schema.add_column("email", NocoDBColumnType.EMAIL)

# 附加到实际表
schema.attach(my_table)  # 或 schema.load_schema(table=my_table)

# 后续正常使用
print(schema.writable_fields)  # ['name', 'age', 'email']
```

### 冲突处理示例
```python
# 假设离线Schema有列 "age" (NUMBER类型)
# 但实际表中有列 "age" (DECIMAL类型)

schema.attach(table)  # 会发出警告并强制修改类型
# 警告: Column 'age' type mismatch: offline=Number, table=Decimal. Using table type.
```

## API参考

### 构造函数
```python
NocoDBSchema(table: Optional['NocoDBTable'] = None)
```

### 属性
- `is_attached: bool` - 是否已附加到表
- `is_detached: bool` - 是否处于离线状态
- `offline_columns: Dict[str, NocoDBColumnType]` - 离线列定义（仅离线状态可用）

### 方法
- `attach(table: 'NocoDBTable') -> None` - 附加到表（一次性操作）
- `add_column(title: str, column_type: NocoDBColumnType) -> None` - 添加离线列
- `remove_column(title: str) -> None` - 删除离线列
- `update_column(title: str, new_type: NocoDBColumnType) -> None` - 更新列类型

## 限制

1. **仅支持basic类型**: 离线状态下只能添加basic类型的列
2. **一次性attach**: attach操作只能执行一次
3. **简化metadata**: 暂时不考虑列元数据，只关注类型

## 测试验证

已通过单元测试验证功能：
- 离线状态管理
- 列操作（添加/更新/删除）
- 状态转换
- 冲突处理机制

测试文件：`tests/draft/test_schema_offline.py`