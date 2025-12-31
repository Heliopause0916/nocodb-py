# NocoDB Python SDK 测试指南

## 概述

本文档描述了 NocoDB Python SDK 的测试框架，特别是具有依赖链的 CRUD 测试架构。

## 测试架构设计

### 依赖链结构
```
project → table → record
```

### 测试模式
每个层级都遵循相同的 7 步测试模式：
1. **read（读到空值）** - 初始状态检查
2. **create** - 创建资源
3. **read** - 验证创建成功
4. **update** - 更新资源
5. **read** - 验证更新成功
6. **delete** - 删除资源
7. **read** - 验证删除成功

## 测试文件结构

### 主要测试文件
- [`tests/tests.py`](../tests/tests.py) - 具有依赖链的 CRUD 测试
- [`tests/test_api.py`](../tests/test_api.py) - 基础 API 集成测试

## 环境配置

### 环境变量文件
在 `tests/.env` 文件中配置：

```bash
# 测试环境配置
NOCODB_API_KEY=your_api_key
NOCODB_BASE_URL=http://localhost:8080
NOCODB_PROJECT_NAME=test_project
NOCODB_TABLE_NAME=test_table

# 云实例测试配置（可选）
NOCODB_CLOUD_API_KEY=your_cloud_api_key
NOCODB_CLOUD_BASE_URL=https://app.nocodb.com
NOCODB_CLOUD_WORKSPACE_NAME=test_workspace
NOCODB_CLOUD_PROJECT_NAME=test_cloud_project
NOCODB_CLOUD_TABLE_NAME=test_cloud_table
```

### 环境变量说明
- `NOCODB_API_KEY`: NocoDB 实例的 API 令牌
- `NOCODB_BASE_URL`: NocoDB 实例的基础 URL
- `NOCODB_PROJECT_NAME`: 用于测试的现有项目名称
- `NOCODB_TABLE_NAME`: 用于测试的现有表格名称

## 运行测试

### 激活虚拟环境
```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Linux/macOS
source .venv/bin/activate
```

### 运行所有测试
```bash
python -m pytest tests/ -v
```

### 运行特定测试文件
```bash
# 运行依赖链测试
python -m pytest tests/tests.py -v

# 运行基础 API 测试
python -m pytest tests/test_api.py -v
```

### 运行特定测试类
```bash
# 仅测试项目层级
python -m pytest tests/tests.py::TestProjectOnly -v

# 测试项目+表格层级
python -m pytest tests/tests.py::TestProjectAndTable -v

# 测试完整链条
python -m pytest tests/tests.py::TestFullChain -v

# 测试工具函数
python -m pytest tests/tests.py::TestUtilities -v
```

### 运行特定测试方法
```bash
python -m pytest tests/tests.py::TestProjectOnly::test_project_crud -v
```

## 测试类说明

### TestProjectOnly
仅测试项目层级的 CRUD 操作：
- 创建、读取、更新、删除项目
- 不依赖其他层级

### TestProjectAndTable
测试项目和表格层级的 CRUD 操作：
- 依赖于 TestProjectOnly
- 在项目更新后执行表格测试

### TestFullChain
测试完整的依赖链：项目 → 表格 → 记录：
- 验证依赖关系正确性
- 测试记录 CRUD 操作

### TestUtilities
测试工具函数和辅助功能：
- 测试名称生成
- 客户端创建验证

## Fixture 设计

### client fixture
- 创建 NocoDB 客户端实例
- 所有测试的基础依赖

### test_project fixture
- 执行项目的完整 CRUD 测试
- 返回项目对象供后续测试使用
- 自动清理：测试结束后删除项目

### test_table fixture
- 依赖于 test_project fixture
- 使用现有表格进行测试（避免创建/删除表格）
- 返回表格对象供后续测试使用

### test_record fixture
- 依赖于 test_table fixture
- 执行记录的完整 CRUD 测试
- 自动清理：测试结束后删除记录

## 测试策略

### 1. 唯一性保证
使用 UUID 生成唯一测试名称，避免测试间冲突：
```python
def generate_test_name(prefix="test"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"
```

### 2. 依赖时机管理
子层次测试在父层次的 `update` 之后执行，确保父资源处于稳定状态。

### 3. 清理策略
使用 `yield` fixture 确保资源在测试结束后被清理：
```python
@pytest.fixture
def test_project(client):
    # 创建和测试...
    yield project  # 返回对象
    # 清理资源...
```

### 4. 错误处理
- 使用 `pytest.skip()` 跳过不满足条件的测试
- 使用断言验证每个步骤的成功
- 提供清晰的错误信息

## 测试覆盖率

### 当前覆盖的功能
- ✅ 项目 CRUD 操作
- ✅ 表格基本操作（使用现有表格）
- ✅ 记录 CRUD 操作
- ✅ 依赖链验证

### 待实现的功能
- ⏳ 表格 CRUD 操作（创建/删除表格）
- ⏳ 列 CRUD 操作
- ⏳ 更复杂的记录操作（批量、过滤等）

## 最佳实践

### 1. 测试隔离
- 每个测试使用唯一的资源名称
- 测试结束后清理所有创建的资源
- 避免测试间的相互影响

### 2. 测试数据
- 使用有意义的测试数据
- 验证数据的完整性和一致性
- 测试边界条件和异常情况

### 3. 断言策略
- 使用明确的断言消息
- 验证返回值的类型和内容
- 检查错误处理逻辑

### 4. 调试技巧
- 使用 `-v` 参数获取详细输出
- 在测试中添加调试打印语句
- 使用 `pytest --pdb` 进行交互式调试

## 故障排除

### 常见问题

1. **环境变量未加载**
   - 确保 `tests/.env` 文件存在且格式正确
   - 检查环境变量名称拼写

2. **API 连接失败**
   - 验证 NocoDB 实例是否运行
   - 检查 API 令牌是否正确

3. **测试资源冲突**
   - 确保测试名称唯一
   - 检查是否有未清理的测试资源

4. **依赖方法未实现**
   - 某些 CRUD 方法可能尚未实现
   - 测试会自动跳过相关部分

### 调试命令
```bash
# 显示详细的测试输出
python -m pytest tests/ -v -s

# 在失败时进入调试模式
python -m pytest tests/ --pdb

# 显示测试覆盖率
python -m pytest tests/ --cov=nocodb_py

# 运行特定标记的测试
python -m pytest tests/ -m "slow"  # 如果有慢速测试标记
```

## 扩展测试

### 添加新的测试层级
要添加新的测试层级（如列层级），遵循相同的模式：

1. 创建新的 fixture，依赖于父层级
2. 实现 7 步 CRUD 测试模式
3. 创建对应的测试类
4. 更新依赖链验证

### 参数化测试
使用 `@pytest.mark.parametrize` 测试不同场景：
```python
@pytest.mark.parametrize("title,description", [
    ("test1", "desc1"),
    ("test2", "desc2"),
])
def test_project_with_params(test_title, test_description):
    # 测试逻辑...
```

这个测试框架提供了灵活且可扩展的基础，可以根据需要添加更多的测试功能和场景。