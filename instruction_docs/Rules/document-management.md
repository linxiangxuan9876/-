# 文档管理规则

## 支持的文件格式

| 格式 | 扩展名 | 解析支持 |
|------|--------|----------|
| PDF | .pdf | PyPDF2, pdfplumber |
| Word | .docx, .doc | python-docx |
| Excel | .xlsx, .xls | openpyxl, xlrd |
| 文本 | .txt | 内置支持 |
| CSV | .csv | pandas |

## 文件大小限制

```python
# 配置项
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# 验证逻辑
if file_size > MAX_FILE_SIZE:
    raise HTTPException(status_code=400, detail="文件大小超过限制")
```

## 文档状态流转

```
┌──────────┐    上传    ┌──────────┐
│ pending  │ ────────→ │ parsing  │
└──────────┘           └──────────┘
      ↑                      │
      │ 解析完成              │ 解析失败
      │                      ↓
      │               ┌──────────────┐
      │               │ parse_error  │
      │               └──────────────┘
      │
      ↓                      ↓
┌──────────┐  审核通过  ┌──────────┐
│ approved │ ←───────── │  parsed   │
└──────────┘           └──────────┘
                             │
                        审核拒绝
                             ↓
                       ┌──────────┐
                       │ rejected │
                       └──────────┘
```

## 文档元数据

```python
class Document:
    store_id: str        # 上传门店ID
    store_name: str      # 上传门店名称
    filename: str       # 存储文件名(UUID)
    original_filename: str  # 原始文件名
    file_path: str      # 存储路径
    file_size: int      # 文件大小(字节)
    file_type: str      # 文件扩展名
    car_model: str      # 车型
    category: str       # 文档分类
    status: DocStatus   # 当前状态
    parsed_content: str # 解析内容
    parse_error: str    # 解析错误信息
```

## 文档删除规则

### 软删除
- 删除时设置 `is_deleted = True`
- 同时记录 `deleted_at` 时间戳
- 数据库保留记录

### 物理删除
- 仅在回收站彻底删除时执行
- 同时删除物理文件
- 不可恢复

## 自动解析规则

### 触发条件
- 文档状态变为 `parsing` 时自动触发
- 使用后台任务异步处理

### 解析内容
- 提取纯文本内容
- 识别 Q&A 结构（可选）
- 生成文档摘要

### 错误处理
- 解析失败记录 `parse_error`
- 状态更新为 `parse_error`
- 不阻塞其他文档处理
