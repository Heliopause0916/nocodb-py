# NocoDB API V2 数据操作参考

本文档汇总了NocoDB API V2中数据操作相关的所有接口，基于官方文档 [https://nocodb.com/apis/v2/data](https://nocodb.com/apis/v2/data)。

## 概述

NocoDB API V2数据操作接口提供了完整的CRUD（创建、读取、更新、删除）功能，支持表格记录的全面管理。所有接口都需要`xc-token`认证头。

## API接口列表

### 1. 列出表格记录 (List Table Records)

**端点**: `GET /api/v2/tables/{tableId}/records`

**描述**: 从指定表格中检索记录，支持过滤、排序和分页。

**路径参数**:
- `tableId` (string): 表格标识符

**查询参数**:
- `fields` (string): 指定返回字段，逗号分隔
- `sort` (string): 排序字段，`-field`表示降序
- `where` (string): 过滤条件，格式`(field,operator,value)~and(field,operator,value)`
- `offset` (integer): 跳过记录数，默认0
- `limit` (integer): 返回记录数限制
- `viewId` (string): 视图标识符

**请求头**:
- `xc-token` (string, required): API令牌

**响应示例**:
```json
{
  "list": [
    {
      "Id": 1,
      "SingleLineText": "David",
      "Year": 2023,
      "URL": "www.google.com",
      "SingleSelect": "Jan",
      "Email": "a@b.com",
      "Duration": 74040,
      "Decimal": 23.658,
      "Currency": 23,
      "JSON": { "name": "John Doe", "age": 30 },
      "Date": "2023-10-16",
      "Time": "06:02:00",
      "Rating": 1,
      "Percent": 55,
      "Checkbox": true,
      "Attachment": [{ "url": "", "title": "2 be loved.jpeg", "mimetype": "image/jpeg", "size": 146143 }],
      "MultiSelect": "Jan,Feb",
      "DateTime": "2023-10-16 08:56:32+00:00",
      "LongText": "The sunsets in the small coastal town...",
      "Geometry": "23.23, 36.54",
      "PhoneNumber": "123456789",
      "Number": 5248,
      "Barcode": "David",
      "QRCode": "David",
      "Formula": "10",
      "Lookup": "a",
      "Links:belongs-to": { "Id": 1, "Title": "a" },
      "Links:has-many": 2,
      "Rollup": 3,
      "Links:many-many": 3
    }
  ],
  "pageInfo": {
    "totalRows": 5,
    "page": 1,
    "pageSize": 1,
    "isFirstPage": true,
    "isLastPage": false
  }
}
```

### 2. 创建表格记录 (Create Table Records)

**端点**: `POST /api/v2/tables/{tableId}/records`

**描述**: 在指定表格中创建新记录。

**路径参数**:
- `tableId` (string, required): 表格标识符

**请求头**:
- `xc-token` (string, required): API令牌

**请求体**: 记录对象数组

**请求示例**:
```json
[
  {
    "SingleLineText": "David",
    "LongText": "The sunsets in the small coastal town...",
    "CreatedAt": "2023-10-16 08:27:59+00:00",
    "UpdatedAt": "2023-10-16 08:56:32+00:00",
    "Decimal": 23.658,
    "Checkbox": true,
    "Attachment": [{ "url": "", "title": "2 be loved.jpeg", "mimetype": "image/jpeg", "size": 146143 }],
    "MultiSelect": "Jan,Feb",
    "SingleSelect": "Jan",
    "Date": "2023-10-16",
    "Year": 2023,
    "Time": "06:02:00",
    "PhoneNumber": "123456789",
    "Email": "a@b.com",
    "URL": "www.google.com",
    "Currency": 23,
    "Percent": 55,
    "Duration": 74040,
    "Rating": 1,
    "JSON": { "name": "John Doe", "age": 30 },
    "DateTime": "2023-10-16 08:56:32+00:00",
    "Geometry": "23.23, 36.54",
    "Number": 5248
  }
]
```

**响应示例**:
```json
[{ "Id": 10 }, { "Id": 11 }]
```

### 3. 更新表格记录 (Update Table Records)

**端点**: `PATCH /api/v2/tables/{tableId}/records`

**描述**: 更新指定表格中的现有记录。

**路径参数**:
- `tableId` (string, required): 表格标识符

**请求头**:
- `xc-token` (string, required): API令牌

**请求体**: 包含记录ID的更新对象数组

**请求示例**:
```json
[
  {
    "Id": 6,
    "SingleLineText": "Updated text-1",
    "DateTime": "2023-10-19 08:56:32+00:00",
    "Geometry": "23.232, 36.542",
    "Number": 52482
  },
  {
    "Id": 7,
    "SingleLineText": "Updated text-2",
    "DateTime": "2023-10-19 08:56:32+00:00",
    "Geometry": "23.232, 36.542",
    "Number": 52482
  }
]
```

**响应示例**:
```json
[{ "Id": 6 }, { "Id": 7 }]
```

### 4. 删除表格记录 (Delete Table Records)

**端点**: `DELETE /api/v2/tables/{tableId}/records`

**描述**: 删除指定表格中的记录。

**路径参数**:
- `tableId` (string, required): 表格标识符

**请求头**:
- `xc-token` (string, required): API令牌

**请求体**: 记录ID数组

**请求示例**:
```json
[{ "Id": 1 }, { "Id": 2 }]
```

**响应示例**:
```json
[{ "Id": 1 }, { "Id": 2 }]
```

### 5. 读取表格记录 (Read Table Record)

**端点**: `GET /api/v2/tables/{tableId}/records/{recordId}`

**描述**: 读取指定表格中的单个记录。

**路径参数**:
- `tableId` (string, required): 表格标识符
- `recordId` (string, required): 记录ID

**查询参数**:
- `fields` (string): 指定返回字段，逗号分隔

**请求头**:
- `xc-token` (string, required): API令牌

**响应示例**:
```json
{
  "Id": 1,
  "SingleLineText": "David",
  "CreatedAt": "2023-10-16 08:27:59+00:00",
  "UpdatedAt": "2023-10-16 10:05:41+00:00",
  "Year": 2023,
  "URL": "www.google.com",
  "SingleSelect": "Jan",
  "Email": "a@b.com",
  "Duration": 74040,
  "Decimal": 23.658,
  "Currency": 23,
  "Barcode": "David",
  "JSON": { "name": "John Doe", "age": 30 },
  "QRCode": "David",
  "Rollup": 3,
  "Date": "2023-10-16",
  "Time": "06:02:00",
  "Rating": 1,
  "Percent": 55,
  "Formula": 10,
  "Checkbox": true,
  "Attachment": [{ "url": "", "title": "2 be loved.jpeg", "mimetype": "image/jpeg", "size": 146143 }],
  "MultiSelect": "Jan,Feb",
  "DateTime": "2023-10-19 08:56:32+00:00",
  "LongText": "The sunsets in the small coastal town...",
  "Geometry": "23.232, 36.542",
  "PhoneNumber": "123456789",
  "Number": 52482,
  "Links:has-many": 2,
  "Links:many-many": 3,
  "Links:belongs-to": { "Id": 1, "Title": "a" },
  "Lookup": "a"
}
```

### 6. 统计表格记录 (Count Table Records)

**端点**: `GET /api/v2/tables/{tableId}/records/count`

**描述**: 统计指定表格或视图中的记录数量。

**路径参数**:
- `tableId` (string, required): 表格标识符

**查询参数**:
- `viewId` (string): 视图标识符
- `where` (string): 过滤条件

**请求头**:
- `xc-token` (string, required): API令牌

**响应示例**:
```json
{ "count": 3 }
```

### 7. 列出链接记录 (List Linked Records)

**端点**: `GET /api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}`

**描述**: 检索特定链接字段和记录ID的链接记录列表。

**路径参数**:
- `tableId` (string, required): 表格标识符
- `linkFieldId` (string, required): 链接字段标识符
- `recordId` (string, required): 记录标识符

**查询参数**:
- `fields` (string): 指定返回字段
- `sort` (string): 排序字段
- `where` (string): 过滤条件
- `offset` (integer): 跳过记录数
- `limit` (integer): 返回记录数限制

**请求头**:
- `xc-token` (string, required): API令牌

**响应示例**:
```json
{
  "list": [
    { "Id": 1, "SingleLineText": "David" },
    { "Id": 2, "SingleLineText": "Jane" },
    { "Id": 3, "SingleLineText": "Dave" },
    { "Id": 4, "SingleLineText": "Martin" }
  ],
  "pageInfo": {
    "totalRows": 4,
    "page": 1,
    "pageSize": 25,
    "isFirstPage": true,
    "isLastPage": true
  }
}
```

### 8. 链接记录 (Link Records)

**端点**: `POST /api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}`

**描述**: 将记录链接到特定的链接字段和记录ID。

**路径参数**:
- `tableId` (string, required): 表格标识符
- `linkFieldId` (string, required): 链接字段标识符
- `recordId` (string, required): 记录标识符

**请求头**:
- `xc-token` (string, required): API令牌

**请求体**: 相邻表格的记录ID数组

**请求示例**:
```json
[{ "Id": 4 }, { "Id": 5 }]
```

**响应示例**:
```json
true
```

### 9. 取消链接记录 (Unlink Records)

**端点**: `DELETE /api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}`

**描述**: 从特定的链接字段和记录ID取消链接记录。

**路径参数**:
- `tableId` (string, required): 表格标识符
- `linkFieldId` (string, required): 链接字段标识符
- `recordId` (string, required): 记录标识符

**请求头**:
- `xc-token` (string, required): API令牌

**请求体**: 相邻表格的记录ID数组

**请求示例**:
```json
[{ "Id": 1 }, { "Id": 2 }]
```

**响应示例**:
```json
true
```

### 10. 附件上传 (Attachment Upload)

**端点**: `POST /api/v2/storage/upload`

**描述**: 上传附件文件。

**查询参数**:
- `path` (string, required): 目标文件路径
- `scope` (string): 附件范围（workspacePics, profilePics, organizationPics）

**请求头**:
- `xc-token` (string, required): API令牌

**请求体** (multipart/form-data):
- `mimetype` (string): 附件MIME类型
- `path` (string): 附件文件路径
- `size` (number): 附件大小
- `title` (string): 附件标题
- `url` (string): 通过URL上传的附件URL

**请求示例**:
```json
{
  "mimetype": "image/jpeg",
  "path": "download/noco/jango_fett/Table1/attachment/uVbjPVQxC_SSfs8Ctx.jpg",
  "size": 13052,
  "title": "22bc-kavypmq4869759 (1).jpg"
}
```

## 注意事项

1. **认证**: 所有API请求都需要有效的`xc-token`认证头
2. **只读字段**: 某些字段类型（如查找、汇总、公式、自动编号等）在创建和更新操作中会被忽略
3. **链接字段**: 对于"链接到另一个记录"字段类型，应使用专门的链接API进行操作
4. **分页**: 列表查询支持分页，响应中包含分页信息
5. **错误处理**: API返回标准HTTP状态码，错误信息在响应体中提供

## 版本信息

- **API版本**: V2
- **文档来源**: [NocoDB官方文档](https://nocodb.com/apis/v2/data)
- **更新时间**: 2025-12-07