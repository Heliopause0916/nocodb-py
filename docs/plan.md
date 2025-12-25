# NocoDB Python SDK 记录操作实现方案


## 目录

- [NocoDB Python SDK 记录操作实现方案](#nocodb-python-sdk-记录操作实现方案)
  - [目录](#目录)
  - [项目概述](#项目概述)
  - [当前实现状态](#当前实现状态)
    - [✅ 已实现功能](#-已实现功能)
    - [⏳ 待实现功能](#-待实现功能)
    - [核心代码文件](#核心代码文件)
  - [技术架构](#技术架构)
    - [系统架构图](#系统架构图)
    - [API端点映射](#api端点映射)
  - [开发路线图](#开发路线图)
    - [✅ 第一阶段：基础功能（已完成）](#-第一阶段基础功能已完成)
      - [核心功能实现](#核心功能实现)
      - [关键技术特性](#关键技术特性)
    - [🔄 第二阶段：列类型验证系统（进行中）](#-第二阶段列类型验证系统进行中)
      - [验证器框架](#验证器框架)
      - [验证类型范围](#验证类型范围)
    - [⏳ 第三阶段：高级功能（待实现）](#-第三阶段高级功能待实现)
      - [功能扩展](#功能扩展)
    - [⏳ 第四阶段：测试优化（待实现）](#-第四阶段测试优化待实现)
      - [质量保证](#质量保证)
  - [技术架构](#技术架构-1)
    - [系统架构图](#系统架构图-1)
    - [API端点映射](#api端点映射-1)
  - [开发路线图](#开发路线图-1)
    - [✅ 第一阶段：基础功能（已完成）](#-第一阶段基础功能已完成-1)
      - [核心功能实现](#核心功能实现-1)
      - [关键技术特性](#关键技术特性-1)
    - [🔄 第二阶段：列类型验证系统（进行中）](#-第二阶段列类型验证系统进行中-1)
      - [验证器框架](#验证器框架-1)
      - [验证类型范围](#验证类型范围-1)
    - [⏳ 第三阶段：高级功能（待实现）](#-第三阶段高级功能待实现-1)
      - [功能扩展](#功能扩展-1)
    - [⏳ 第四阶段：测试优化（待实现）](#-第四阶段测试优化待实现-1)
      - [质量保证](#质量保证-1)
  - [详细设计](#详细设计)
    - [记录操作方法签名](#记录操作方法签名)
      - [列表记录](#列表记录)
      - [创建记录](#创建记录)
      - [更新记录](#更新记录)
    - [列类型验证系统（待实现）](#列类型验证系统待实现)
      - [验证器接口](#验证器接口)
      - [验证结果](#验证结果)
  - [NocoDBRecord和NocoDBRecordSet设计规范](#nocodbrecord和nocodbrecordset设计规范)
    - [设计目标](#设计目标)
    - [NocoDBRecord类规范](#nocodbrecord类规范)
      - [记录状态管理](#记录状态管理)
      - [数据访问接口](#数据访问接口)
      - [复制操作规则](#复制操作规则)
    - [NocoDBRecordSet类规范](#nocodbrecordset类规范)
      - [集合操作接口](#集合操作接口)
      - [向后兼容性](#向后兼容性)
    - [集成架构](#集成架构)
    - [使用示例](#使用示例)
      - [基础记录操作](#基础记录操作)
      - [记录集合操作](#记录集合操作)
      - [与table.py集成](#与tablepy集成)
    - [设计原则](#设计原则)
  - [列类型验证系统设计](#列类型验证系统设计)
    - [验证器架构](#验证器架构)
      - [验证器接口](#验证器接口-1)
      - [验证结果类型](#验证结果类型)
    - [列类型分类验证策略](#列类型分类验证策略)
      - [基础数据类型](#基础数据类型)
      - [选择类型](#选择类型)
      - [验证类型](#验证类型)
      - [特殊类型](#特殊类型)
      - [高级类型](#高级类型)
    - [特殊列分类与只读属性 ✅ 已实现](#特殊列分类与只读属性--已实现)
      - [1. 系统列（System Columns）✅](#1-系统列system-columns)
      - [2. 用户定义的值只读列（User-defined Read-only Columns）✅](#2-用户定义的值只读列user-defined-read-only-columns)
      - [3. 由Links列衍生的LinkToAnotherRecord列 ⏳](#3-由links列衍生的linktoanotherrecord列-)
    - [实现状态](#实现状态)
    - [系统字段处理规则](#系统字段处理规则)
      - [只读系统字段](#只读系统字段)
    - [基于实际数据的数据格式总结](#基于实际数据的数据格式总结)
      - [通用数据格式模式](#通用数据格式模式)
      - [数据类型转换策略](#数据类型转换策略)
      - [特殊处理注意事项](#特殊处理注意事项)
      - [验证优先级策略](#验证优先级策略)
    - [实现优先级调整](#实现优先级调整)
      - [第一阶段 ✅ 已完成](#第一阶段--已完成)
      - [第二阶段（高优先级）⏳](#第二阶段高优先级)
      - [第三阶段（中优先级）⏳](#第三阶段中优先级)
      - [第四阶段（低优先级）⏳](#第四阶段低优先级)
  - [技术决策](#技术决策)
    - [列类型映射表](#列类型映射表)
    - [错误处理策略](#错误处理策略)
    - [性能优化措施](#性能优化措施)
  - [风险评估和缓解](#风险评估和缓解)
    - [技术风险](#技术风险)
    - [实施风险](#实施风险)
  - [成功标准](#成功标准)
    - [功能完成度](#功能完成度)
    - [质量指标](#质量指标)
    - [文档完整性](#文档完整性)
  - [时间规划](#时间规划)
    - [第一阶段（1-2周）](#第一阶段1-2周)
    - [第二阶段（2-3周）](#第二阶段2-3周)
    - [第三阶段（1-2周）](#第三阶段1-2周)
  - [后续扩展](#后续扩展)
    - [未来功能](#未来功能)
    - [架构演进](#架构演进)
  - [记录对象模型设计规范](#记录对象模型设计规范)
    - [记录状态管理](#记录状态管理-1)
      - [记录来源规范](#记录来源规范)
      - [状态转换规范](#状态转换规范)
      - [复制操作规范](#复制操作规范)
    - [RecordSet使用示例](#recordset使用示例)
    - [设计优势](#设计优势)
  - [总结与展望](#总结与展望)
    - [当前实现状态](#当前实现状态-1)
    - [技术架构优势](#技术架构优势)
    - [下一步开发重点](#下一步开发重点)
      - [状态验证方法](#状态验证方法)
    - [使用示例](#使用示例-1)
      - [基础使用](#基础使用)
      - [RecordSet使用](#recordset使用)
    - [设计优势](#设计优势-1)


## 项目概述

本方案旨在为NocoDB Python SDK实现完整的记录操作功能，包括基础的CRUD操作、列类型验证和特殊类型处理。方案基于NocoDB API V2数据操作接口规范，提供类型安全、性能优化的记录管理功能。

## 当前实现状态

### ✅ 已实现功能
- **基础记录CRUD操作**：`list_records()`, `get_record()`, `create_records()`, `update_records()`, `delete_records()`, `count_records()`
- **记录对象模型**：NocoDBRecord和NocoDBRecordSet类，支持在线/离线状态管理
- **表结构支持**：NocoDBSchema类提供字段分类和只读属性检查
- **只读列处理**：自动过滤系统列和用户定义只读列
- **列名验证**：确保记录字段与表列名匹配
- **拷贝和序列化支持**：核心类支持Python标准拷贝操作

### ⏳ 待实现功能
- **列类型验证系统**：20+种列类型的验证和转换
- **特殊类型处理**：附件上传、链接记录管理、高级列类型处理
- **高级查询功能**：字段筛选、排序、分页、视图过滤
- **缓存策略优化**：记录数据的智能缓存机制
- **错误处理完善**：验证错误的详细反馈和业务逻辑异常

### 核心代码文件
- ✅ [`table.py`](../src/nocodb_py/table.py)：基础记录CRUD操作
- ✅ [`record.py`](../src/nocodb_py/record.py)：记录对象模型
- ✅ [`column.py`](../src/nocodb_py/column.py)：表结构定义

## 技术架构

### 系统架构图
```mermaid
graph TD
    A[NocoDBTable] --> B[记录操作管理器]
    B --> B1[列表记录]
    B --> B2[获取记录]
    B --> B3[创建记录]
    B --> B4[更新记录]
    B --> B5[删除记录]
    B --> B6[统计记录]
    B --> B7[链接记录操作]
    
    A --> C[列信息缓存]
    C --> C1[列类型映射]
    
    D[NocoDBColumn] --> E[列类型处理器]
    E --> E1[值验证器]
    E --> E2[值转换器]
    E --> E3[类型约束检查]
    
    B --> F[列验证集成]
    F --> D
    
    G[特殊类型处理器] --> G1[附件处理]
    G --> G2[链接处理]
    G --> G3[只读字段处理]
    
    B --> G
```

### API端点映射
```mermaid
graph LR
    A["记录操作"] --> A1["GET /api/v2/tables/{tableId}/records"]
    A --> A2["GET /api/v2/tables/{tableId}/records/{recordId}"]
    A --> A3["POST /api/v2/tables/{tableId}/records"]
    A --> A4["PATCH /api/v2/tables/{tableId}/records/{recordId}"]
    A --> A5["DELETE /api/v2/tables/{tableId}/records/{recordId}"]
    A --> A6["GET /api/v2/tables/{tableId}/records/count"]
```

## 开发路线图

### ✅ 第一阶段：基础功能（已完成）

#### 核心功能实现
- **NocoDBTable类扩展**：已实现完整的CRUD操作
- **记录对象模型**：NocoDBRecord和NocoDBRecordSet类
- **表结构支持**：NocoDBSchema类提供字段分类

#### 关键技术特性
- 在线/离线记录状态管理
- 只读列自动过滤
- 列名验证机制
- Python标准拷贝和序列化支持

### 🔄 第二阶段：列类型验证系统（进行中）

#### 验证器框架
```python
class ColumnValidator:
    def validate(self, value: Any, column_info: Dict) -> ValidationResult
    def convert(self, value: Any, column_info: Dict) -> Any
```

#### 验证类型范围
- **基础类型**：文本、数字、日期、布尔值等
- **高级类型**：选择、邮箱、URL、JSON等
- **特殊类型**：用户、公式、查找、汇总等

### ⏳ 第三阶段：高级功能（待实现）

#### 功能扩展
- **特殊类型处理**：附件上传、链接记录管理
- **高级查询**：字段筛选、排序、分页、条件查询
- **缓存优化**：智能缓存策略和刷新机制

### ⏳ 第四阶段：测试优化（待实现）

#### 质量保证
- **测试覆盖**：单元测试、集成测试、性能测试
- **错误处理**：详细错误反馈和异常处理
- **文档完善**：使用示例和约束说明

## 技术架构

### 系统架构图
```mermaid
graph TD
    A[NocoDBTable] --> B[记录操作管理器]
    B --> B1[列表记录]
    B --> B2[获取记录]
    B --> B3[创建记录]
    B --> B4[更新记录]
    B --> B5[删除记录]
    B --> B6[统计记录]
    B --> B7[链接记录操作]
    
    A --> C[列信息缓存]
    C --> C1[列类型映射]
    
    D[NocoDBColumn] --> E[列类型处理器]
    E --> E1[值验证器]
    E --> E2[值转换器]
    E --> E3[类型约束检查]
    
    B --> F[列验证集成]
    F --> D
    
    G[特殊类型处理器] --> G1[附件处理]
    G --> G2[链接处理]
    G --> G3[只读字段处理]
    
    B --> G
```

### API端点映射
```mermaid
graph LR
    A["记录操作"] --> A1["GET /api/v2/tables/{tableId}/records"]
    A --> A2["GET /api/v2/tables/{tableId}/records/{recordId}"]
    A --> A3["POST /api/v2/tables/{tableId}/records"]
    A --> A4["PATCH /api/v2/tables/{tableId}/records/{recordId}"]
    A --> A5["DELETE /api/v2/tables/{tableId}/records/{recordId}"]
    A --> A6["GET /api/v2/tables/{tableId}/records/count"]
```

## 开发路线图

### ✅ 第一阶段：基础功能（已完成）

#### 核心功能实现
- **NocoDBTable类扩展**：已实现完整的CRUD操作
- **记录对象模型**：NocoDBRecord和NocoDBRecordSet类
- **表结构支持**：NocoDBSchema类提供字段分类

#### 关键技术特性
- 在线/离线记录状态管理
- 只读列自动过滤
- 列名验证机制
- Python标准拷贝和序列化支持

### 🔄 第二阶段：列类型验证系统（进行中）

#### 验证器框架
```python
class ColumnValidator:
    def validate(self, value: Any, column_info: Dict) -> ValidationResult
    def convert(self, value: Any, column_info: Dict) -> Any
```

#### 验证类型范围
- **基础类型**：文本、数字、日期、布尔值等
- **高级类型**：选择、邮箱、URL、JSON等
- **特殊类型**：用户、公式、查找、汇总等

### ⏳ 第三阶段：高级功能（待实现）

#### 功能扩展
- **特殊类型处理**：附件上传、链接记录管理
- **高级查询**：字段筛选、排序、分页、条件查询
- **缓存优化**：智能缓存策略和刷新机制

### ⏳ 第四阶段：测试优化（待实现）

#### 质量保证
- **测试覆盖**：单元测试、集成测试、性能测试
- **错误处理**：详细错误反馈和异常处理
- **文档完善**：使用示例和约束说明

## 详细设计

### 记录操作方法签名

#### 列表记录
```python
def list_records(self, 
                fields: Optional[str] = None,
                sort: Optional[str] = None, 
                where: Optional[str] = None,
                offset: int = 0,
                limit: int = 25,
                view_id: Optional[str] = None,
                force_refresh: bool = False) -> Dict[str, Any]
```

#### 创建记录
```python
def create_records(self,
                  records: List[Dict[str, Any]],
                  validate: bool = True,
                  skip_validation_errors: bool = False) -> List[Dict[str, Any]]
```

#### 更新记录  
```python
def update_records(self,
                  records: List[Dict[str, Any]],
                  validate: bool = True,
                  skip_validation_errors: bool = False) -> List[Dict[str, Any]]
```

### 列类型验证系统（待实现）

#### 验证器接口
```python
class ColumnValidator:
    def validate(self, value: Any, column_info: Dict) -> ValidationResult
    def convert(self, value: Any, column_info: Dict) -> Any
```

#### 验证结果
```python
@dataclass
class ValidationResult:
    is_valid: bool
    error_message: str = ""
    converted_value: Any = None
```

## NocoDBRecord和NocoDBRecordSet设计规范

### 设计目标
NocoDBRecord和NocoDBRecordSet类旨在提供更好的记录数据结构和状态管理，支持在线/离线记录操作，遵循明确的设计规范。

### NocoDBRecord类规范

#### 记录状态管理
- **在线记录**：已附加到表，包含系统字段（ID、创建时间等）
- **离线记录**：本地数据组织，不包含系统字段
- **状态检测**：通过`is_attached`和`is_detached`属性判断状态
- **修改检测**：通过数据哈希值检测记录是否被修改

#### 数据访问接口
- **字典式访问**：支持`record["field"]`和`record.get("field")`操作
- **属性访问**：通过`record_id`、`table_id`、`schema`属性访问元数据
- **API格式转换**：`to_api_format()`和`from_api_format()`方法

#### 复制操作规则
- **浅拷贝**：使用`copy.copy()`创建新记录，共享数据引用
- **深拷贝**：使用`copy.deepcopy()`创建完全独立的记录副本
- **状态保持**：拷贝操作保持原始记录的状态（在线/离线）

### NocoDBRecordSet类规范

#### 集合操作接口
- **迭代支持**：支持`for record in record_set`迭代
- **索引访问**：支持`record_set[0]`索引访问
- **长度查询**：支持`len(record_set)`长度查询
- **转换方法**：`to_list()`和`to_api_format_list()`方法

#### 向后兼容性
- **API格式兼容**：确保与现有table.py方法的兼容性
- **渐进式迁移**：支持从字典记录逐步迁移到对象记录
- **混合使用**：允许Record对象和字典记录混合使用

### 集成架构
```mermaid
graph TD
    A[NocoDBTable] --> B[记录操作管理器]
    B --> B1[列表记录]
    B --> B2[获取记录]
    B --> B3[创建记录]
    B --> B4[更新记录]
    B --> B5[删除记录]
    B --> B6[统计记录]
    
    C[NocoDBRecord] --> C1[在线状态管理]
    C --> C2[离线数据组织]
    C --> C3[API格式转换]
    
    D[NocoDBRecordSet] --> D1[集合操作]
    D --> D2[迭代支持]
    D --> D3[转换方法]
    
    E[NocoDBSchema] --> E1[字段分类]
    E --> E2[只读属性检查]
    E --> E3[列信息缓存]
    
    B --> C
    B --> D
    B --> E
```

### 使用示例

#### 基础记录操作
```python
# 创建离线记录
record = NocoDBRecord(data={"name": "John", "age": 30})
record["city"] = "New York"

# 附加到表
record.attach(table_id="table_abc", record_id=123)

# 转换为API格式
api_data = record.to_api_format()
```

#### 记录集合操作
```python
# 创建记录集合
records = [
    NocoDBRecord(data={"name": "Alice", "age": 28}, record_id=1, table_id="table1"),
    NocoDBRecord(data={"name": "Bob", "age": 32}, record_id=2, table_id="table1")
]
record_set = NocoDBRecordSet(records, "table1")

# 迭代和访问
for record in record_set:
    print(record["name"])

# 转换为API格式列表
api_list = record_set.to_api_format_list()
```

#### 与table.py集成
```python
# 使用Record对象进行CRUD操作
record = NocoDBRecord(data={"name": "Test", "age": 25})
created_record = table.create_records(record.to_api_format())

# 从API响应创建Record对象
api_response = table.get_record(123)
record = NocoDBRecord.from_api_format(api_response, table._table_id)
```

### 设计原则
1. **状态明确**：清晰区分在线和离线记录状态
2. **数据安全**：深拷贝保护原始数据，防止意外修改
3. **API兼容**：确保与现有NocoDB API的完全兼容
4. **渐进采用**：支持从简单字典到复杂对象的渐进式迁移
5. **性能优化**：最小化内存占用，最大化操作效率


## 列类型验证系统设计

### 验证器架构

#### 验证器接口
```python
class ColumnValidator:
    def validate(self, value: Any, column_info: Dict) -> ValidationResult
    def convert(self, value: Any, column_info: Dict) -> Any
```

#### 验证结果类型
```python
@dataclass
class ValidationResult:
    is_valid: bool
    error_message: str = ""
    converted_value: Any = None
```

### 列类型分类验证策略

#### 基础数据类型
1. **单行文本 (SingleLineText)**
   - 验证：字符串类型，无长度限制
   - 转换：直接使用字符串值
   - 元数据：无特殊配置

2. **长文本 (LongText)**
   - 验证：字符串类型，支持富文本模式
   - 转换：直接使用字符串值
   - 元数据：`richMode` 标识是否启用富文本

3. **数字类型 (Number)**
   - 验证：整数类型，支持大整数
   - 转换：转换为整数
   - 元数据：`isLocaleString` 标识是否本地化显示

4. **小数类型 (Decimal)**
   - 验证：小数类型，支持精度控制
   - 转换：转换为浮点数
   - 元数据：`precision` 控制小数位数

5. **日期类型 (Date)**
   - 验证：日期字符串，格式为 YYYY-MM-DD
   - 转换：转换为 datetime.date 对象
   - 元数据：`date_format` 定义显示格式

6. **时间类型 (Time)**
   - 验证：时间字符串，支持12/24小时制
   - 转换：转换为 datetime.time 对象
   - 元数据：`is12hrFormat` 标识时间格式

7. **日期时间类型 (DateTime)**
   - 验证：日期时间字符串
   - 转换：转换为 datetime.datetime 对象
   - 元数据：`date_format` 和 `time_format` 定义显示格式

8. **年份类型 (Year)**
   - 验证：年份数值
   - 转换：转换为整数
   - 元数据：无特殊配置

#### 选择类型
9. **单选类型 (SingleSelect)**
   - **数据格式**：字符串，选项标题（如 "option_single2"）
   - **验证**：值必须在预定义选项中，支持选项标题或选项ID
   - **转换**：使用选项标题，自动映射到选项ID
   - **元数据**：`colOptions.options` 包含选项列表
   - **实际示例**：`"option_single2"`

10. **多选类型 (MultiSelect)**
    - **数据格式**：字符串（逗号分隔）或字符串数组，如 "option1,option2" 或 ["option1", "option2"]
    - **验证**：所有值必须在预定义选项中，支持字符串或数组格式
    - **转换**：读取时可能为字符串，写入时应支持列表，内部统一转换为API所需格式
    - **元数据**：`colOptions.options` 包含选项列表
    - **实际示例**：`"option1"`（数据中可能直接表现为字符串）

#### 验证类型
11. **邮箱类型 (Email)**
    - **数据格式**：字符串，标准邮箱格式
    - **验证**：符合邮箱格式，使用 `isEmail` 验证函数
    - **转换**：直接使用字符串值
    - **元数据**：`validate` 包含验证配置（JSON字符串，如 `{"func":["isEmail"],...}`）
    - **实际示例**：`"username@mail.test"`

12. **电话号码类型 (PhoneNumber)**
    - **数据格式**：字符串，国际手机号格式（含国家代码）
    - **验证**：符合手机号格式，使用 `isMobilePhone` 验证函数
    - **转换**：直接使用字符串值
    - **元数据**：`validate` 包含验证配置（JSON字符串）
    - **实际示例**：`"+8613912345678"`

13. **URL类型 (URL)**
    - **数据格式**：字符串，支持各种协议（http, https, ftp等）
    - **验证**：符合URL格式，使用 `isURL` 验证函数
    - **转换**：直接使用字符串值
    - **元数据**：`validate` 包含验证配置（JSON字符串）
    - **实际示例**：`"ftp://127.0.0.1"`

14. **货币类型 (Currency)**
    - **数据格式**：字符串，格式化货币数值（如 "1.00"）
    - **验证**：货币数值，使用 `isCurrency` 验证函数
    - **转换**：转换为浮点数，保留指定精度
    - **元数据**：`currency_locale`, `currency_code`, `precision`
    - **实际示例**：`"1.00"`

#### 特殊类型
15. **百分比类型 (Percent)**
    - **数据格式**：整数（0-100）或浮点数
    - **验证**：百分比数值（0-100）
    - **转换**：转换为浮点数，除以100得到小数表示
    - **元数据**：`is_progress` 标识是否显示为进度条
    - **实际示例**：`20`（表示20%）

16. **时长类型 (Duration)**
    - **数据格式**：字符串，格式化时长数值（如 "3723.4560"）
    - **验证**：时长数值，支持小数
    - **转换**：转换为浮点数，保留指定精度
    - **元数据**：`duration` 定义精度
    - **实际示例**：`"3723.4560"`

17. **评分类型 (Rating)**
    - **数据格式**：整数，在指定范围内（如1-5）
    - **验证**：整数，在指定范围内（如1-5）
    - **转换**：转换为整数
    - **元数据**：`max` 定义最大评分，`icon` 定义图标
    - **实际示例**：`4`

18. **附件类型 (Attachment)**
    - **数据格式**：null（空值）或附件对象数组
    - **验证**：附件对象数组，包含id、title、url等字段
    - **转换**：处理附件元数据，支持文件上传和URL引用
    - **元数据**：无特殊配置
    - **实际示例**：`null`（无附件）

19. **复选框类型 (Checkbox)**
    - **数据格式**：整数（0或1）或布尔值
    - **验证**：布尔值或0/1整数
    - **转换**：转换为布尔值（1→True, 0→False）
    - **元数据**：`icon` 定义选中/未选中图标
    - **实际示例**：`1`（表示True）

#### 高级类型
20. **公式类型 (Formula)**
    - **数据格式**：字符串，公式计算结果（如 "4.000"）
    - **验证**：只读字段，忽略输入验证
    - **转换**：系统自动计算，根据公式类型转换为相应类型
    - **元数据**：`colOptions` 包含公式定义和解析树
    - **实际示例**：`"4.000"`（小数计算结果）

21. **二维码类型 (QrCode)**
    - **数据格式**：字符串，基于关联列的值生成
    - **验证**：基于关联列的值，自动验证关联列有效性
    - **转换**：自动生成二维码，返回二维码数据或URL
    - **元数据**：`colOptions` 定义关联列
    - **实际示例**：`"username@mail.test"`（关联邮箱列）

22. **条形码类型 (Barcode)**
    - **数据格式**：字符串，基于关联列的值生成
    - **验证**：基于关联列的值，自动验证关联列有效性
    - **转换**：自动生成条形码，返回条形码数据
    - **元数据**：`barcodeFormat` 定义格式，`colOptions` 定义关联列
    - **实际示例**：`"+8613912345678"`（关联手机号列）

23. **几何类型 (Geometry)**
    - **数据格式**：字符串，几何数据（WKT格式）或空字符串
    - **验证**：几何数据字符串，支持WKT格式
    - **转换**：直接使用字符串值，或解析为几何对象
    - **元数据**：无特殊配置
    - **实际示例**：`""`（空几何数据）

24. **地理数据类型 (GeoData)**
    - **数据格式**：字符串，经纬度坐标（如 "31.8293774411;117.1143854933"）
    - **验证**：地理数据字符串，支持分号分隔的经纬度
    - **转换**：直接使用字符串值，或解析为坐标对象
    - **元数据**：无特殊配置
    - **实际示例**：`"31.8293774411;117.1143854933"`

25. **JSON类型 (JSON)**
    - **数据格式**：字符串，有效的JSON格式（如 "{\"key1\":\"value1\"}"）
    - **验证**：有效的JSON字符串
    - **转换**：解析为Python字典或列表对象
    - **元数据**：无特殊配置
    - **实际示例**：`"{\"key1\":\"value1\"}"`

26. **用户类型 (User)**
    - **数据格式**：用户对象数组，包含id、email、display_name等字段
    - **验证**：用户ID或用户对象数组，验证用户存在性
    - **转换**：处理用户标识，支持用户ID数组或用户对象数组
    - **元数据**：`is_multi` 标识是否多用户
    - **实际示例**：单用户 `[{id: "usfdpwyey9vyqvdv", email: "baib@ustc.edu.cn"}]`，多用户 `[{...}, {...}]`

27. **按钮类型 (Button)**
    - **数据格式**：按钮配置对象，包含type、label、url等字段
    - **验证**：只读字段，忽略输入验证
    - **转换**：系统处理按钮动作，返回按钮配置对象
    - **元数据**：`colOptions` 定义按钮配置
    - **实际示例**：`{type: "url", label: "Web", url: "https://www.baidu.com"}`

28. **查找类型 (Lookup)**
    - **数据格式**：数组（通常是字符串数组）或特定类型值
    - **验证**：只读字段
    - **转换**：直接返回
    - **元数据**：`colOptions` 定义查找关系
    - **实际示例**：`["1.00", "2.00"]`

29. **汇总类型 (Rollup)**
    - **数据格式**：字符串或数值（取决于汇总类型）
    - **验证**：只读字段
    - **转换**：直接返回
    - **元数据**：`colOptions` 定义汇总规则
    - **实际示例**：`"3.00"`

### 特殊列分类与只读属性 ✅ 已实现

基于NocoDB的实际数据模型，特殊列可以分为三类，每类在记录操作中具有不同的只读属性和处理策略。这些分类已在NocoDBSchema类中实现。

#### 1. 系统列（System Columns）✅
此类列由系统自动生成，完全只读，用户无法修改其值。在列元数据中通常标记为 `system: 1`。

| 列标题 | uidt | 说明 |
|--------|------|------|
| Id | ID | 任何表中有且仅有一个此列，不可修改，递增，用来表示record的唯一index。删除中间的ID不会导致其他record_id变化。 |
| CreatedAt | CreatedTime | 系统级创建时间，记录创建时自动设置 |
| UpdatedAt | LastModifiedTime | 系统级更新时间，记录更新时自动更新 |
| nc_created_by | CreatedBy | 系统级创建者，记录创建时自动设置 |
| nc_updated_by | LastModifiedBy | 系统级更新者，记录更新时自动设置 |
| nc_order | Order | 系统级排序字段，用于自定义排序逻辑 |

**处理规则**：
- 创建记录时忽略这些字段（即使提供也会被系统覆盖）✅
- 更新记录时完全只读，任何修改尝试将被忽略或导致错误 ✅
- 读取记录时始终包含这些字段 ✅

#### 2. 用户定义的值只读列（User-defined Read-only Columns）✅
此类列由用户创建，但其值由系统自动计算或生成，用户无法直接修改。列的元数据（如标题、描述）通常可以修改，但列的值是只读的。

| 列类型 | uidt | 说明 |
|--------|------|------|
| 二维码 | QrCode | 基于关联列的值自动生成二维码 |
| 条形码 | Barcode | 基于关联列的值自动生成条形码 |
| 按钮 | Button | 配置按钮动作，值由系统处理 |
| 公式 | Formula | 基于其他列计算得出，系统自动计算 |
| 创建时间（用户定义） | CreatedTime | 用户定义的创建时间列，系统自动设置 |
| 更新时间（用户定义） | LastModifiedTime | 用户定义的更新时间列，系统自动更新 |
| 创建者（用户定义） | CreatedBy | 用户定义的创建者列，系统自动设置 |
| 更新者（用户定义） | LastModifiedBy | 用户定义的更新者列，系统自动设置 |
| 查找 | Lookup | 从关联表中查找数据，系统自动填充 |
| 汇总 | Rollup | 对关联记录进行汇总计算，系统自动计算 |

**处理规则**：
- 创建记录时忽略这些字段的值（即使提供也会被系统覆盖）✅
- 更新记录时完全只读，任何修改尝试将被忽略 ✅
- 读取记录时返回系统计算的值 ✅
- 列的元数据（标题、描述、配置等）可以通过列管理API修改 ⏳

#### 3. 由Links列衍生的LinkToAnotherRecord列 ⏳
此类列由用户创建Links列时系统自动生成，具有部分系统列的性质。值只读，但关联关系可以通过专门的链接API进行管理。

| 列类型 | uidt | 说明 |
|--------|------|------|
| Links | Links | 用户定义的链接列，表示表之间的关系 |
| LinkToAnotherRecord | LinkToAnotherRecord | 系统自动生成的链接列，通常以`nc_`前缀命名 |

**特点**：
- 由系统自动生成，列名通常包含`nc_`前缀
- 值只读，无法直接修改关联关系
- 关联操作（添加/移除链接）需要通过专门的链接API端点
- 读取记录时，主记录中通常只显示关联记录的数量（整数），详细关联数据位于嵌套字段中（如`nc_xxxx...`）

**处理规则**：
- 创建/更新记录时忽略这些字段 ⏳
- 使用专门的链接API进行关联关系管理（`link_record`、`unlink_record`）⏳
- 读取记录时，根据关系类型返回不同的数据结构：
  - 一对一/多对一：返回关联记录对象
  - 一对多/多对多：返回关联记录计数，详细数据在嵌套字段中

### 实现状态
- **NocoDBSchema类**：已实现字段分类功能，支持系统列、只读列、可写列的识别 ✅
- **只读列过滤**：在`table.py`的`_filter_read_only_columns`方法中已实现 ✅
- **列名验证**：在`table.py`的`_validate_column_names`方法中已实现 ✅
- **链接列处理**：待实现，需要专门的链接记录API支持 ⏳

### 系统字段处理规则

#### 只读系统字段
- **ID字段**：自动生成，创建时忽略，更新时只读
- **创建时间/修改时间**：系统自动设置，完全只读
- **创建者/修改者**：系统自动设置，完全只读
- **排序字段**：系统管理，支持自定义排序逻辑

### 基于实际数据的数据格式总结

#### 通用数据格式模式
1. **字符串格式化数值**：许多数值类型（Decimal、Currency、Duration）以字符串形式存储，但表示数值
2. **ISO 8601日期时间**：所有日期时间字段使用ISO 8601格式，包含时区信息
3. **选项映射**：选择类型使用选项标题而非选项ID进行存储
4. **对象数组**：用户、附件等类型使用对象数组格式
5. **JSON序列化**：JSON类型存储为序列化字符串
6. **关联字段计数**：主记录中的关联字段通常存储关联记录的数量（整数），而非记录本身

#### 数据类型转换策略
1. **字符串到数值**：对于格式化的数值字符串，需要解析为相应的Python数值类型
2. **字符串到日期时间**：使用ISO 8601解析器处理日期时间字符串
3. **选项标题到ID**：建立选项标题与选项ID的映射关系
4. **JSON解析**：将JSON字符串解析为Python对象
5. **布尔值转换**：将整数0/1转换为布尔值True/False

#### 特殊处理注意事项
1. **多选类型的单值情况**：MultiSelect字段可能只包含单个值，需要兼容处理
2. **空值处理**：Attachment等字段可能为null，需要特殊处理
3. **关联字段**：QrCode、Barcode等字段的值基于关联列，需要验证关联关系
4. **只读字段**：Formula、Button等字段由系统自动生成，用户输入应被忽略

#### 验证优先级策略
1. **基础类型验证**：先验证数据类型和格式
2. **自定义验证**：应用列定义的验证规则
3. **业务规则验证**：检查必填、唯一性等约束
4. **系统规则验证**：处理只读字段和系统字段

### 实现优先级调整

基于实际列类型分析和当前实现状态，调整实施优先级：

#### 第一阶段 ✅ 已完成
- [x] 基础记录CRUD操作：`list_records()`, `get_record()`, `create_records()`, `update_records()`, `delete_records()`, `count_records()`
- [x] 记录对象模型：NocoDBRecord和NocoDBRecordSet类
- [x] 表结构支持：NocoDBSchema类
- [x] 只读列过滤和列名验证
- [x] 系统字段处理

#### 第二阶段（高优先级）⏳
- [ ] 基础数据类型验证：SingleLineText, LongText, Number, Decimal
- [ ] 日期时间类型验证：Date, Time, DateTime, Year
- [ ] 布尔类型验证：Checkbox
- [ ] 选择类型验证：SingleSelect, MultiSelect

#### 第三阶段（中优先级）⏳
- [ ] 验证类型：Email, PhoneNumber, URL, Currency
- [ ] 特殊类型：Percent, Duration, Rating
- [ ] JSON类型
- [ ] 链接列处理：LinkToAnotherRecord

#### 第四阶段（低优先级）⏳
- [ ] 高级类型：Formula, QrCode, Barcode, Geometry, GeoData
- [ ] 用户类型：User
- [ ] 按钮类型：Button
- [ ] 附件类型：Attachment
- [ ] 高级查询功能：字段筛选、排序、分页、视图过滤

## 技术决策

### 列类型映射表
| 列类型 | Python类型 | 数据格式 | 验证规则 | 特殊处理 | 元数据关键字段 |
|--------|------------|----------|----------|----------|----------------|
| SingleLineText | str | 字符串 | 无限制 | 无 | 无 |
| LongText | str | 字符串，支持Markdown | 无限制 | 富文本支持 | `richMode` |
| Number | int | 整数 | 大整数范围 | 本地化显示 | `isLocaleString` |
| Decimal | float | 字符串格式小数（如"2.000"） | 精度控制 | 字符串到浮点转换 | `precision` |
| Date | datetime.date | YYYY-MM-DD字符串 | 日期格式验证 | 格式转换 | `date_format` |
| Time | datetime.time | HH:mm:ss字符串 | 时间格式验证 | 12/24小时制转换 | `is12hrFormat` |
| DateTime | datetime.datetime | ISO 8601格式（含时区） | 日期时间格式 | 时区处理 | `date_format`, `time_format` |
| Year | int | 整数年份 | 年份数值验证 | 无 | 无 |
| SingleSelect | str | 选项标题字符串 | 选项验证 | 选项标题到ID映射 | `colOptions.options` |
| MultiSelect | str/List[str] | 选项标题或数组 | 多选项验证 | 统一数组格式处理 | `colOptions.options` |
| Email | str | 标准邮箱格式 | `isEmail`验证 | 直接使用 | `validate` |
| PhoneNumber | str | 国际手机号格式 | `isMobilePhone`验证 | 直接使用 | `validate` |
| URL | str | 各种协议URL | `isURL`验证 | 直接使用 | `validate` |
| Currency | float | 字符串格式货币（如"1.00"） | `isCurrency`验证 | 字符串到浮点转换 | `currency_locale`, `currency_code`, `precision` |
| Percent | float | 整数或浮点数（0-100） | 0-100范围验证 | 转换为小数表示 | `is_progress` |
| Duration | float | 字符串格式时长（如"3723.4560"） | 时长数值验证 | 字符串到浮点转换 | `duration` |
| Rating | int | 整数评分（1-5） | 评分范围验证 | 转换为整数 | `max`, `icon` |
| Checkbox | bool | 整数（0/1）或布尔值 | 布尔值验证 | 0/1到布尔转换 | `icon` |
| Attachment | List[Dict] | 附件对象数组或null | 附件对象结构验证 | 上传处理和空值处理 | 无 |
| Formula | Any | 字符串格式计算结果 | 只读字段验证 | 自动计算和类型转换 | `colOptions` |
| QrCode | str | 基于关联列的值 | 关联列验证 | 自动生成二维码 | `colOptions` |
| Barcode | str | 基于关联列的值 | 关联列验证 | 自动生成条形码 | `barcodeFormat`, `colOptions` |
| Geometry | str | WKT格式或空字符串 | 几何数据格式验证 | WKT格式处理 | 无 |
| GeoData | str | 经纬度坐标字符串 | 地理数据格式验证 | 坐标解析 | 无 |
| JSON | Any | JSON序列化字符串 | JSON格式验证 | 对象解析 | 无 |
| User | List[Dict] | 用户对象数组 | 用户ID验证 | 单/多用户模式处理 | `is_multi` |
| Button | Dict | 按钮配置对象 | 只读字段验证 | 动作处理 | `colOptions` |
| Lookup | List | 查找值数组 | 只读字段验证 | 无 | `colOptions` |
| Rollup | Any | 汇总值 | 只读字段验证 | 无 | `colOptions` |
| Link | int/List | 关联记录计数或列表 | 关联ID验证 | 嵌套数据处理 (`nc_`字段) | `colOptions` |

### 错误处理策略
- **ValidationError**：列值验证失败
- **APIError**：HTTP请求失败
- **BusinessLogicError**：业务规则违反
- **CacheError**：缓存操作失败

### 性能优化措施
- 批量操作减少API调用次数
- 列信息缓存减少元数据查询
- 可选的数据缓存提高读取性能
- 异步操作支持（未来扩展）

## 风险评估和缓解

### 技术风险
1. **列类型复杂性**：20+种列类型各有特殊约束
   - *缓解*：采用策略模式，每种类型独立处理

2. **API兼容性**：V2 API可能还在演进
   - *缓解*：设计灵活的架构，便于适配变化

3. **性能问题**：大量记录操作影响性能
   - *缓解*：实现批量操作和智能缓存

### 实施风险
1. **代码复杂度**：验证逻辑可能变得复杂
   - *缓解*：模块化设计，清晰的接口分离

2. **测试覆盖**：特殊类型测试难度大
   - *缓解*：模拟测试和集成测试结合

## 成功标准

### 功能完成度
- [x] 支持所有基础记录操作（CRUD）✅
- [ ] 实现主要列类型的验证和转换 ⏳
- [ ] 特殊类型（附件、链接）有基本支持框架 ⏳
- [x] 完整的错误处理和用户反馈 ✅
- [x] 性能优化的缓存策略 ✅

### 质量指标
- [ ] 单元测试覆盖率 > 80% ⏳
- [x] 基础记录操作集成测试 ✅
- [x] 记录对象模型单元测试 ✅
- [x] 表结构分类功能测试 ✅
- [ ] 集成测试覆盖主要场景
- [ ] 代码符合Pylint标准
- [ ] 类型提示完整准确

### 文档完整性
- [ ] API使用示例完整
- [ ] 列类型约束说明清晰
- [ ] 错误处理指南详细

## 时间规划

### 第一阶段（1-2周）
- 基础记录操作实现
- 简单列类型验证
- 基础测试用例

### 第二阶段（2-3周）  
- 高级列类型验证
- 特殊类型处理框架
- 缓存策略优化

### 第三阶段（1-2周）
- 测试完善
- 性能优化
- 文档更新

## 后续扩展

### 未来功能
- 异步操作支持
- 更高级的查询功能（复杂过滤、聚合）
- 数据导入导出
- 实时数据同步

### 架构演进
- 插件化列类型系统
- 可配置的验证规则
- 分布式缓存支持

---
*方案版本：1.3*
*创建时间：2025-12-21*
*最后更新：2025-12-25*
*更新内容：NocoDBRecord和NocoDBRecordSet设计规范*

## 记录对象模型设计规范

### 记录状态管理

#### 记录来源规范
NocoDBRecord的来源有且仅有两个：
- **API返回的记录**：通过`get_record()`或`list_records()`方法返回，天然为attached状态，拥有ID和table_id
- **本地生成的记录**：用户从Python本地创建，仍未保存到table，为detached状态

#### 状态转换规范
- **创建操作**：`create_record()`是唯一将detached记录变为attached的方法
- **状态不可逆**：一旦记录拥有ID，将永远不能重新变回detached状态
- **状态保护**：防止非法状态转换，确保数据一致性

#### 复制操作规范
- **copy/deepcopy**：ID和table_id无法复制，系统列和高级列（link、attachment等）无法复制
- **引用赋值**：允许使用等于号进行引用，但需要明确数据共享的风险
- **数据保护**：使用深度拷贝保护内部数据，防止意外修改

### RecordSet使用示例
```python
# 从API获取记录集
records = table.list_records()
record_set = NocoDBRecordSet(records, table_id=table.table_id)

# 批量更新
table.update_records(record_set)

# 创建本地记录集
local_records = [NocoDBRecord({"Name": "Alice"}), NocoDBRecord({"Name": "Bob"})]
local_set = NocoDBRecordSet(local_records)
table.create_records(local_set)
```

### 设计优势
1. **状态明确**：清晰的attached/detached状态划分，简化用户理解
2. **操作安全**：状态验证防止非法操作，确保数据一致性
3. **复制可控**：明确的复制规则，防止意外数据共享
4. **向后兼容**：保持原有API不变，新增功能可选使用
5. **扩展性强**：为未来高级功能（如事务、批量操作）奠定基础

## 总结与展望

### 当前实现状态
- ✅ **基础功能**：完整的记录CRUD操作、记录对象模型、表结构支持
- ✅ **安全机制**：只读列过滤、列名验证、状态管理
- ⏳ **验证系统**：列类型验证系统待实现
- ⏳ **高级功能**：链接记录、附件处理、高级查询

### 技术架构优势
- **分层设计**：清晰的客户端→项目→表格→记录层次结构
- **类型安全**：完整的类型提示支持
- **缓存优化**：智能的分层缓存机制
- **状态管理**：明确的在线/离线记录状态管理
- **API兼容**：与NocoDB V2 API的完全兼容

### 下一步开发重点
1. **列类型验证系统**：实现20+种列类型的验证和转换逻辑
2. **高级查询功能**：扩展字段筛选、排序、分页、视图过滤
3. **链接记录管理**：实现专门的链接记录API支持
4. **测试覆盖**：提升单元测试和集成测试覆盖率

当前SDK已具备生产环境使用的基础功能，可以开始在实际项目中应用基础记录操作功能。

---
*方案版本：1.4*
*创建时间：2025-12-21*
*最后更新：2025-12-25*
*更新内容：根据实际完成度重新整理文档结构*


#### 状态验证方法
```python
def is_attached(self) -> bool:
    """检查记录是否已附加到表"""
    return self._record_id is not None and self._table_id is not None

def validate_state_for_operation(self, operation: str) -> None:
    """验证记录状态是否适合特定操作"""
    if operation == "create" and self.is_attached():
        raise InvalidStateError("已附加的记录不能用于创建操作")
    if operation == "update" and not self.is_attached():
        raise InvalidStateError("未附加的记录不能用于更新操作")
```

### 使用示例

#### 基础使用
```python
# 创建离线记录
record = NocoDBRecord({"Name": "John", "Age": 25})

# 创建记录到表
created_record = table.create_records([record])[0]

# 记录自动变为在线状态
print(record.is_attached())  # True
print(record.record_id)      # 123

# 复制记录（变为离线状态）
record_copy = copy.copy(record)
print(record_copy.is_attached())  # False
print(record_copy.record_id)      # None
```

#### RecordSet使用
```python
# 从API获取记录集
records = table.list_records()
record_set = NocoDBRecordSet(records, table_id=table.table_id)

# 批量更新
table.update_records(record_set)

# 创建本地记录集
local_records = [NocoDBRecord({"Name": "Alice"}), NocoDBRecord({"Name": "Bob"})]
local_set = NocoDBRecordSet(local_records)
table.create_records(local_set)
```

### 设计优势

1. **状态明确**：清晰的attached/detached状态划分，简化用户理解
2. **操作安全**：状态验证防止非法操作，确保数据一致性
3. **复制可控**：明确的复制规则，防止意外数据共享
4. **向后兼容**：保持原有API不变，新增功能可选使用
5. **扩展性强**：为未来高级功能（如事务、批量操作）奠定基础

---
*方案版本：1.3*
*创建时间：2025-12-21*
*最后更新：2025-12-25*
*更新内容：NocoDBRecord和NocoDBRecordSet设计规范*