# 可复用代码模块

> 本目录收录了在 4S 店售后知识库项目中验证有效的可复用代码组件

---

## 📋 目录索引

| 模块 | 文件 | 说明 |
|------|------|------|
| 配置管理 | [config.py](./config.py) | 环境变量配置 |
| 数据库 | [database.py](./database.py) | 数据库连接与会话 |
| 认证 | [security.py](./security.py) | JWT 认证与密码加密 |
| API 基础 | [api_base.py](./api_base.py) | API 路由基础类 |
| 文件处理 | [file_handler.py](./file_handler.py) | 文件上传与验证 |
| 查重服务 | [deduplication.py](./deduplication.py) | FuzzyWuzzy 查重 |
| 分类服务 | [classifier.py](./classifier.py) | AI 分类调用 |

---

## 🎯 使用方式

### 直接复制
```python
# 复制所需模块到你的项目
from app.core.config import settings
from app.core.database import get_db
```

### 完整引入
```python
# 在 requirements.txt 添加依赖
# fuzzywuzzy>=0.18.0
# python-multipart>=0.0.6
# passlib[bcrypt]>=1.7.4

# 复制 core/ 目录到你的项目
```

---

## 📦 依赖清单

```
# 核心依赖
fastapi>=0.100.0
uvicorn>=0.22.0
pydantic>=2.0.0
pydantic-settings>=2.0.0

# 数据库
sqlalchemy>=2.0.0
python-sqlite>=0.0.3

# 认证
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6

# AI 服务
openai>=1.0.0

# 文档处理
python-docx>=0.8.11
openpyxl>=3.1.0
pdfplumber>=0.10.0

# 文本处理
fuzzywuzzy>=0.18.0
aiofiles>=23.0.0

# 配置
python-dotenv>=1.0.0
```

---

## ⚠️ 使用注意事项

1. **安全检查**：部署前确认 SECRET_KEY 已配置
2. **CORS 配置**：生产环境请指定具体域名
3. **数据库**：SQLite 仅适合开发， 生产请用 PostgreSQL
4. **文件存储**：生产环境请配置 OSS/S3 等对象存储

---

## 📝 版本记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-04-08 | 初始版本，包含核心模块 |
