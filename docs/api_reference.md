# NocoDB API V2 Meta 参考文档

本文档基于NocoDB官方API V2 Meta文档自动生成，包含所有可用的API端点及其详细说明。

## 基础管理 (Bases)

### 列出基础 (云实例)
**描述**: 获取指定工作区ID关联的基础列表，返回分页结果。

**HTTP方法**: GET  
**路径**: `/api/v2/meta/workspaces/{workspaceId}/bases`

**路径参数**:
- `workspaceId` (必需): 工作区ID

**头参数**:
- `xc-token` (必需): API令牌

**响应示例**:
```json
{
  "list": [
    {
      "sources": [...],
      "color": "#24716E",
      "created_at": "2023-03-01 14:27:36",
      "deleted": true,
      "description": "This is my base description",
      "id": "p_124hhlkbeasewh",
      "title": "my-base"
    }
  ],
  "pageInfo": {
    "isFirstPage": true,
    "isLastPage": true,
    "page": 1,
    "pageSize": 10,
    "totalRows": 1
  }
}
```

### 创建基础 (云实例)
**描述**: 在指定工作区内创建新基础。

**HTTP方法**: POST  
**路径**: `/api/v2/meta/workspaces/{workspaceId}/bases`

**路径参数**:
- `workspaceId` (必需): 工作区ID

**头参数**:
- `xc-token` (必需): API令牌

**请求体参数**:
- `title` (必需): 基础标题 (1-128字符)
- `description`: 基础描述
- `meta`: 基础元数据对象

### 获取基础详情
**描述**: 获取指定基础ID的详细信息。

**HTTP方法**: GET  
**路径**: `/api/v2/meta/bases/{baseId}`

**路径参数**:
- `baseId` (必需): 基础ID

### 更新基础
**描述**: 更新指定基础的属性。

**HTTP方法**: PUT  
**路径**: `/api/v2/meta/bases/{baseId}`

**请求体参数**:
- `title`: 基础标题
- `order`: 项目列表顺序
- `meta`: 基础元数据

### 删除基础
**描述**: 永久删除指定基础。

**HTTP方法**: DELETE  
**路径**: `/api/v2/meta/bases/{baseId}`

### 列出基础 (OSS版本)
**描述**: 获取所有可用基础列表 (开源版本)。

**HTTP方法**: GET  
**路径**: `/api/v2/meta/bases/`

### 创建基础 (OSS版本)
**描述**: 在系统中创建新基础 (开源版本)。

**HTTP方法**: POST  
**路径**: `/api/v2/meta/bases/`

## 表格管理 (Tables)

### 列出表格
**描述**: 获取指定基础内的所有表格列表。

**HTTP方法**: GET  
**路径**: `/api/v2/meta/bases/{baseId}/tables`

**查询参数**:
- `page`: 分页页码
- `pageSize`: 每页项目数
- `sort`: 排序规则
- `includeM2M`: 是否包含多对多关系表

### 创建表格
**描述**: 在指定基础内创建新表格。

**HTTP方法**: POST  
**路径**: `/api/v2/meta/bases/{baseId}/tables`

**请求体参数**:
- `table_name`: 表格名称
- `columns`: 列模型数组
- `title` (必需): 表格标题
- `description`: 表格描述

### 获取表格元数据
**描述**: 通过表格ID获取表格元数据。

**HTTP方法**: GET  
**路径**: `/api/v2/meta/tables/{tableId}`

### 更新表格
**描述**: 通过表格ID更新表格元数据。

**HTTP方法**: PUT  
**路径**: `/api/v2/meta/tables/{tableId}`

**请求体参数**:
- `table_name` (必需): 表格名称
- `title`: 表格标题

### 删除表格
**描述**: 通过表格ID删除表格。

**HTTP方法**: DELETE  
**路径**: `/api/v2/meta/tables/{tableId}`

## 视图管理 (Views)

### 列出视图
**描述**: 获取指定表格内的所有视图列表。

**HTTP方法**: GET  
**路径**: `/api/v2/meta/tables/{tableId}/views`

### 删除视图
**描述**: 通过视图ID删除视图。

**HTTP方法**: DELETE  
**路径**: `/api/v2/meta/views/{viewId}`

### 列出视图列
**描述**: 获取指定视图内的所有列列表。

**HTTP方法**: GET  
**路径**: `/api/v2/meta/views/{viewId}/columns`

### 创建网格视图
**描述**: 在指定表格内创建新网格视图。

**HTTP方法**: POST  
**路径**: `/api/v2/meta/tables/{tableId}/grids`

**请求体参数**:
- `title` (必需): 视图标题
- `type` (必需): 视图类型 (3=Grid)
- `fk_grp_col_id`: 分组列外键

### 更新网格视图
**描述**: 通过视图ID更新网格视图。

**HTTP方法**: PUT  
**路径**: `/api/v2/meta/grids/{viewId}`

### 更新网格视图列
**描述**: 更新网格视图中的列。

**HTTP方法**: PUT  
**路径**: `/api/v2/meta/grid-columns/{columnId}`

### 创建表单视图
**描述**: 在指定表格内创建新表单视图。

**HTTP方法**: POST  
**路径**: `/api/v2/meta/tables/{tableId}/forms`

### 更新表单视图
**描述**: 通过表单视图ID更新表单数据。

**HTTP方法**: PUT  
**路径**: `/api/v2/meta/forms/{formViewId}`

### 获取表单视图元数据
**描述**: 通过表单视图ID获取表单数据。

**HTTP方法**: GET  
**路径**: `/api/v2/meta/forms/{formViewId}`

### 更新表单视图列
**描述**: 通过表单视图列ID更新表单列。

**HTTP方法**: PUT  
**路径**: `/api/v2/meta/form-columns/{formViewColumnId}`

### 创建画廊视图
**描述**: 在指定表格内创建新画廊视图。

**HTTP方法**: POST  
**路径**: `/api/v2/meta/tables/{tableId}/galleries`

### 获取画廊视图元数据
**描述**: 通过画廊视图ID获取画廊视图数据。

**HTTP方法**: GET  
**路径**: `/api/v2/meta/galleries/{galleryViewId}`

### 更新画廊视图
**描述**: 通过画廊视图ID更新画廊视图数据。

**HTTP方法**: PUT  
**路径**: `/api/v2/meta/galleries/{galleryViewId}`

### 创建看板视图
**描述**: 创建新看板视图。

**HTTP方法**: POST  
**路径**: `/api/v2/meta/tables/{tableId}/kanbans`

### 获取看板视图元数据
**描述**: 通过看板视图ID获取看板视图数据。

**HTTP方法**: GET  
**路径**: `/api/v2/meta/kanbans/{kanbanViewId}`

### 更新看板视图
**描述**: 通过看板视图ID更新看板视图数据。

**HTTP方法**: PUT  
**路径**: `/api/v2/meta/kanbans/{kanbanViewId}`

## 列操作 (Columns)

### 创建列
**描述**: 在指定表格内创建新列。

**HTTP方法**: POST  
**路径**: `/api/v2/meta/tables/{tableId}/columns`

**请求体参数**:
- `title` (必需): 列标题
- `uidt`: 列数据类型 (默认SingleLineText)
- `description`: 列描述
- `cdf`: 列默认值
- `pv`: 设置为主值
- `rqd`: 设置为必需

### 获取列元数据
**描述**: 通过列ID获取现有列信息。

**HTTP方法**: GET  
**路径**: `/api/v2/meta/columns/{columnId}`

### 更新列
**描述**: 通过列ID更新现有列。

**HTTP方法**: PUT  
**路径**: `/api/v2/meta/columns/{columnId}`

### 删除列
**描述**: 通过列ID删除现有列。

**HTTP方法**: DELETE  
**路径**: `/api/v2/meta/columns/{columnId}`

### 设置主值
**描述**: 在指定列上设置主值。

**HTTP方法**: POST  
**路径**: `/api/v2/meta/columns/{columnId}/primary`

## 过滤器 (Filters)

### 列出视图过滤器
**描述**: 获取指定视图内的所有过滤器列表。

**HTTP方法**: GET  
**路径**: `/api/v2/meta/views/{viewId}/filters`

### 创建视图过滤器
**描述**: 在指定视图中更新过滤器数据。

**HTTP方法**: POST  
**路径**: `/api/v2/meta/views/{viewId}/filters`

### 获取过滤器元数据
**描述**: 通过过滤器ID获取过滤器数据。

**HTTP方法**: GET  
**路径**: `/api/v2/meta/filters/{filterId}`

### 更新过滤器
**描述**: 通过过滤器ID更新过滤器数据。

**HTTP方法**: PUT  
**路径**: `/api/v2/meta/filters/{filterId}`

### 删除过滤器
**描述**: 通过过滤器ID删除过滤器数据。

**HTTP方法**: DELETE  
**路径**: `/api/v2/meta/filters/{filterId}`

### 获取过滤器组子项
**描述**: 获取指定过滤器组ID的子项。

**HTTP方法**: GET  
**路径**: `/api/v2/meta/filters/{filterGroupId}/children`

## 排序 (Sorts)

### 列出视图排序
**描述**: 获取指定视图内的所有排序列表。

**HTTP方法**: GET  
**路径**: `/api/v2/meta/views/{viewId}/sorts`

### 创建视图排序
**描述**: 在指定视图中更新排序数据。

**HTTP方法**: POST  
**路径**: `/api/v2/meta/views/{viewId}/sorts`

### 获取排序元数据
**描述**: 通过排序ID获取排序数据。

**HTTP方法**: GET  
**路径**: `/api/v2/meta/sorts/{sortId}`

### 更新排序
**描述**: 通过排序ID更新排序数据。

**HTTP方法**: PUT  
**路径**: `/api/v2/meta/sorts/{sortId}`

### 删除排序
**描述**: 通过排序ID删除排序数据。

**HTTP方法**: DELETE  
**路径**: `/api/v2/meta/sorts/{sortId}`

## 数据源管理 (Sources)

### 列出数据源
**描述**: 获取指定基础内的所有数据源列表。

**HTTP方法**: GET  
**路径**: `/api/v2/meta/bases/{baseId}/sources/`

### 创建数据源
**描述**: 在指定基础上创建新数据源。

**HTTP方法**: POST  
**路径**: `/api/v2/meta/bases/{baseId}/sources/`

### 获取数据源详情
**描述**: 获取指定基础的源详细信息。

**HTTP方法**: GET  
**路径**: `/api/v2/meta/bases/{baseId}/sources/{sourceId}`

### 列出表格 (特定源)
**描述**: 列出指定基础和源中的所有表格。

**HTTP方法**: GET  
**路径**: `/api/v2/meta/bases/{baseId}/{sourceId}/tables`

### 创建表格 (特定源)
**描述**: 在指定基础和源中创建新表格。

**HTTP方法**: POST  
**路径**: `/api/v2/meta/bases/{baseId}/{sourceId}/tables`

## 用户管理 (Users)

### 列出基础用户
**描述**: 获取指定基础内的所有用户列表。

**HTTP方法**: GET  
**路径**: `/api/v2/meta/bases/{baseId}/users`

### 创建基础用户
**描述**: 创建用户并将其添加到指定基础。

**HTTP方法**: POST  
**路径**: `/api/v2/meta/bases/{baseId}/users`

### 更新基础用户
**描述**: 更新指定基础中的给定用户。

**HTTP方法**: PUT  
**路径**: `/api/v2/meta/bases/{baseId}/users/{userId}`

### 删除基础用户
**描述**: 删除指定基础中的给定用户。

**HTTP方法**: DELETE  
**路径**: `/api/v2/meta/bases/{baseId}/users/{userId}`

## 评论系统 (Comments)

### 列出评论
**描述**: 列出所有评论。

**HTTP方法**: GET  
**路径**: `/api/v2/meta/comments`

**查询参数**:
- `row_id` (必需): 行ID
- `fk_model_id` (必需): 模型外键

### 添加评论
**描述**: 在行中创建新评论。

**HTTP方法**: POST  
**路径**: `/api/v2/meta/comments`

### 更新评论
**描述**: 更新评论。

**HTTP方法**: PUT  
**路径**: `/api/v2/meta/comment/{commentId}`

### 删除评论
**描述**: 删除评论。

**HTTP方法**: DELETE  
**路径**: `/api/v2/meta/comment/{commentId}`

## Webhooks管理 (Hooks)

### 列出表格钩子
**描述**: 获取指定表格内的所有Webhooks列表。

**HTTP方法**: GET  
**路径**: `/api/v2/meta/tables/{tableId}/hooks`

### 创建表格钩子
**描述**: 在指定表格中创建钩子。

**HTTP方法**: POST  
**路径**: `/api/v2/meta/tables/{tableId}/hooks`

### 更新表格钩子
**描述**: 通过ID更新现有钩子。

**HTTP方法**: PUT  
**路径**: `/api/v2/meta/hooks/{hookId}`

### 删除表格钩子
**描述**: 通过ID删除现有钩子。

**HTTP方法**: DELETE  
**路径**: `/api/v2/meta/hooks/{hookId}`

### 获取表格钩子过滤器
**描述**: 获取指定钩子中的过滤器数据。

**HTTP方法**: GET  
**路径**: `/api/v2/meta/hooks/{hookId}/filters`

### 创建表格钩子过滤器
**描述**: 在指定钩子中创建过滤器。

**HTTP方法**: POST  
**路径**: `/api/v2/meta/hooks/{hookId}/filters`

## API令牌管理 (API Tokens)

### 创建API令牌
**描述**: 在基础中创建API令牌。

**HTTP方法**: POST  
**路径**: `/api/v2/meta/bases/{baseId}/api-tokens`

**请求体参数**:
- `description`: API令牌描述

### 删除API令牌
**描述**: 删除基础中的给定API令牌。

**HTTP方法**: DELETE  
**路径**: `/api/v2/meta/bases/{baseId}/api-tokens/{tokenId}`

---

*本文档最后更新于: 2025-12-07*  
*数据来源: https://nocodb.com/apis/v2/meta*