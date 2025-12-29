# NocoDB Python SDK 技术栈

## 技术栈概述
NocoDB Python SDK 基于现代Python技术栈构建，注重类型安全、性能优化和开发体验。项目将全面支持NocoDB API V2，覆盖元数据管理和数据操作两大模块，特别关注记录操作功能和列类型验证系统，并实现完整的Python拷贝和序列化支持。

## 核心技术

### 编程语言
- **Python 3.9+**: 支持现代Python特性，包括类型提示
- **类型提示**: 完整的类型注解，提供更好的开发体验和IDE支持

### 核心依赖
- **requests 2.25.0+**: HTTP客户端库，处理API调用
- **threading**: 内置线程安全机制，支持并发缓存访问
- **python-dotenv 1.0.0+**: 环境变量加载（测试专用，开发依赖）

### 开发工具
- **setuptools**: 包管理和构建工具
- **setuptools-scm**: 自动版本管理
- **pylint**: 代码质量检查（已配置）
- **pytest 7.0+**: 测试框架
- **pytest-cov 4.0+**: 测试覆盖率检查
- **black 23.0+**: 代码格式化
- **ruff 0.0.285+**: 代码质量检查
- **types-requests**: 类型提示支持

## 开发环境设置

### 项目结构
```
nocodb-py/
├── src/nocodb_py/          # 源代码目录
│   ├── __init__.py         # 包初始化
│   ├── client.py           # 主客户端类
│   ├── workspace.py        # 工作区管理
│   ├── project.py          # 项目管理
│   ├── table.py            # 表格管理
│   ├── record.py           # 记录管理
│   ├── column.py           # 列管理
│   ├── validator.py        # 验证器框架（新增）
│   ├── exceptions.py       # 异常处理模块
│   ├── utils.py            # 工具函数
│   └── variable.py         # 配置变量
├── tests/                  # 测试目录
│   ├── test.py            # 主测试文件
│   ├── test_api.py        # API测试
│   ├── draft/             # 临时测试数据目录
│   └── .env.example       # 环境变量示例
├── docs/                   # 文档目录
│   ├── api_reference_meta.md     # API元数据参考
│   ├── api_reference_data.md     # API数据操作参考
│   ├── column_encyclopedia.md    # 列类别百科
│   ├── plan.md                   # 实施计划
│   └── VENV_SETUP.md             # 虚拟环境设置指南
├── pyproject.toml         # 项目配置
├── README.md              # 英文文档
├── README_zh.md           # 中文文档
└── LICENSE                # 许可证文件
```

### 构建配置
- **包名称**: `nocodb-py`
- **版本管理**: 使用setuptools-scm自动生成版本号
- **Python要求**: >=3.9
- **依赖管理**: 通过pyproject.toml管理

## 技术约束

### 兼容性约束
- 仅支持Python 3.9及以上版本
- 依赖requests库，不支持异步HTTP客户端
- 缓存机制基于内存，不支持分布式缓存
- 支持NocoDB API V2，需要适配V2 API的错误响应格式

### 性能约束
- 缓存TTL可配置，默认300秒
- 请求超时可配置，默认10秒
- 线程安全设计，支持并发访问
- 支持分页查询，优化大数据量处理

## 开发模式

### 记录操作实现架构
基于 `docs/plan.md` 中的详细方案，记录操作功能已实现基础CRUD操作和记录对象模型，采用以下技术架构：

#### 已实现的记录操作功能
- **列表记录**：`list_records()` - 获取表格中的所有记录
- **获取记录**：`get_record(record_id)` - 根据ID获取单个记录
- **创建记录**：`create_records(records)` - 创建单个或多个记录
- **更新记录**：`update_records(records)` - 更新单个或多个记录
- **删除记录**：`delete_records(records)` - 删除单个或多个记录
- **统计记录**：`count_records()` - 统计表格中的记录数量

#### 记录对象模型（新增）
- **NocoDBRecord类**：封装记录数据和元数据，支持在线/离线状态管理
  - 在线记录：已附加到表，包含系统字段（ID、创建时间等）
  - 离线记录：本地数据组织，不包含系统字段
  - 支持字典式访问：`record["field"]`和`record.get("field")`
  - API格式转换：`to_api_format()`和`from_api_format()`方法
- **NocoDBRecordSet类**：封装多个记录的集合
  - 支持迭代、索引访问和长度查询
  - 提供`to_list()`和`to_api_format_list()`方法保持向后兼容
  - 为未来扩展预留接口（过滤、排序等）

#### 列类型验证系统（已实现框架）
- **验证器框架**：ValidationResult、ValidationLevel、Validator基类已实现
- **单行文本验证器**：SingleLineTextValidator已实现，支持验证级别和结果类型
- **20+种列类型支持**：包括基础类型、选择类型、验证类型和特殊类型（待完善）
- **验证器接口**：统一的验证和转换接口，支持类型安全的数据处理
- **特殊类型处理**：附件、链接记录、只读字段、系统字段的智能处理
- **数据类型映射**：NocoDB列类型到Python类型的精确映射
- **时间转换支持**：完整的时间转换函数集，支持日期、时间、日期时间类型的精确解析和转换，为时间相关列验证器提供基础工具

##### 列分类与只读属性
基于对NocoDB列模型的深入分析，SDK识别出三类特殊列，这些列在记录操作中需要特殊处理：
- **系统列**：由NocoDB系统自动生成，值完全由系统控制（如Id、CreatedAt、UpdatedAt等），用户无法修改。
- **用户定义的值只读列**：由用户创建，但值由系统计算或生成（如Formula、QrCode、Button等），用户无法直接修改值。
- **链接列**：由用户创建Links列时，系统自动衍生的LinkToAnotherRecord列，值只读，必须通过专门的链接记录API管理关系。

SDK自动处理这些特殊列，在创建/更新记录时过滤只读字段，提供清晰的错误信息，并通过专用API管理链接关系。

#### 记录操作API
- **CRUD操作**：完整记录创建、读取、更新、删除功能已实现
- **批量操作**：支持批量记录操作，减少API调用次数
- **记录对象模型**：NocoDBRecord和NocoDBRecordSet类提供更好的数据结构
- **高级查询**：字段筛选、排序、分页、视图过滤支持（待实现）
- **链接记录管理**：多对多、一对多关系链接操作（待实现）

### 拷贝和序列化支持
- **核心类实现**：Client、Project、Table类实现`__copy__`、`__deepcopy__`、`__getstate__`、`__setstate__`方法
- **缓存状态管理**：拷贝时自动重置缓存状态，保持对象独立性
- **线程安全处理**：正确处理线程锁的序列化和反序列化
- **pickle兼容**：支持标准的Python序列化操作
- **测试验证**：已验证功能正常

### 代码组织模式
- 分层架构：客户端→工作区→项目→表格→视图→列
- 每个类负责单一职责
- 统一的缓存和错误处理机制
- 模块化设计，支持V2 API功能扩展
- 支持元数据管理和数据操作两大模块分离

### 测试策略
- 使用环境变量配置测试实例（通过python-dotenv加载）
- 支持自托管和云实例测试
- 完整的测试框架已配置，包含9个集成测试用例
- 使用pytest作为测试运行器，支持测试覆盖率检查
- 测试环境验证通过，环境变量加载正常
- 计划增加V2 API端点的集成测试
- 覆盖元数据API和数据操作API的完整测试
- 当前测试覆盖V2 API基础功能，但完整功能覆盖率有待提高

### API端点架构
#### 元数据API端点 (`/api/v2/meta/`)
- **项目管理**：项目CRUD操作，支持自托管和云实例路径差异
- **表格管理**：表格创建、元数据获取、更新和删除
- **视图管理**：网格视图、表单视图、画廊视图、看板视图
- **列操作**：列创建、更新、删除、主值设置
- **过滤器排序**：视图级别的条件过滤和排序规则
- **数据源管理**：多数据源支持和管理
- **用户权限**：项目用户管理和角色分配
- **评论系统**：行级别评论功能
- **Webhooks**：表钩子管理和事件触发
- **API令牌**：令牌创建和管理

#### 数据操作API端点 (`/api/v2/`)
- **记录CRUD**：列出、创建、读取、更新、删除表格记录
- **记录统计**：统计表格或视图中的记录数量
- **链接记录**：列出、链接、取消链接记录操作
- **附件上传**：支持文件上传到存储系统
- **高级查询**：支持字段筛选、排序、分页、视图过滤

#### 记录操作端点详细映射
- **列表记录**：`GET /api/v2/tables/{tableId}/records`
- **获取记录**：`GET /api/v2/tables/{tableId}/records/{recordId}`
- **创建记录**：`POST /api/v2/tables/{tableId}/records`
- **更新记录**：`PATCH /api/v2/tables/{tableId}/records/{recordId}`
- **删除记录**：`DELETE /api/v2/tables/{tableId}/records/{recordId}`
- **统计记录**：`GET /api/v2/tables/{tableId}/records/count`

## 部署和发布

### 包发布
- 通过PyPI发布
- 使用setuptools构建
- 支持源码安装和pip安装

### 版本策略
- 早期开发阶段：0.0.0版本
- 使用语义化版本控制
- 自动版本管理基于git提交
- 版本规划将考虑V2 API功能的逐步集成，当前已实现基础架构、项目创建、表格元数据获取、列管理功能、拷贝序列化支持、完整记录CRUD操作、记录对象模型、验证器框架和时间转换系统
- 记录操作功能已实现完整CRUD和记录对象模型，验证器框架已搭建，时间转换系统已完善，需要继续实现具体列类型验证器

## 开发工作流

### Python 命令执行规范
- **虚拟环境检查**: 使用 `execute_command` 工具执行 python、pip 等 Python 相关命令前，必须确认是否处于虚拟环境下，避免污染系统环境
- **简短测试**: 对于较短语句的 Python 测试，可以使用 `python -c` 直接执行
- **临时测试区**: `tests/draft.py` 为临时测试区（任何 `tests/draft*` 文件都在 `.gitignore` 规则内），可以自由创建、修改和删除这些文件中的代码并执行
- **输出管理**: 如果 draft 区域代码的 Python 输出结果可能过长，可以将结果保存在 `tests/draft/` 文件夹下以供后续读取

### 依赖管理
- **主依赖安装**: `pip install -e .`
- **开发依赖安装**: `pip install -e .[dev]`
- **开发依赖包含**: pytest, pytest-cov, black, ruff, types-requests, python-dotenv
- **虚拟环境**: 使用`.venv/`目录，已配置完整开发环境

### 代码质量
- 使用pylint和ruff进行代码检查
- 使用black进行代码格式化
- 类型提示强制使用
- 统一的代码风格
- 遵循API设计最佳实践，确保V2 API兼容性
- **文档字符串语言**: 所有文档字符串（docstring）必须使用英文编写，以确保代码库的一致性并便于国际协作。注释（comment）可以使用中文，但建议优先使用英文。

### 测试工作流
- 运行测试: `python -m pytest tests/`
- 检查覆盖率: `pytest --cov=nocodb_py tests/`
- 环境验证: 通过`tests/.env`文件配置测试环境变量

### 文档策略
- 提供中英文README文档
- 内嵌文档字符串
- API参考文档
- 更新文档以包含V2 API使用示例
- 添加记录操作使用指南和列类型约束说明
- 创建了面向用户的列类别百科文档 (`docs/column_encyclopedia.md`)
- 虚拟环境设置指南 (`docs/VENV_SETUP.md`) - 已从展示完成状态转换为完整的建立指导，适用于不同计算机的本地开发者