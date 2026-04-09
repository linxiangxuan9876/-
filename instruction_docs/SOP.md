# AI 开发标准操作流程

> 本文档定义了基于 AI Agent 的项目开发标准流程，适用于 FastAPI + SQLAlchemy 技术栈的知识库类应用

---

## 📋 目录

1. [项目启动流程](#1-项目启动流程)
2. [需求分析流程](#2-需求分析流程)
3. [架构设计流程](#3-架构设计流程)
4. [编码开发流程](#4-编码开发流程)
5. [测试验证流程](#5-测试验证流程)
6. [部署上线流程](#6-部署上线流程)
7. [运维监控流程](#7-运维监控流程)
8. [知识沉淀流程](#8-知识沉淀流程)

---

## 1. 项目启动流程

### 1.1 环境准备

```bash
# 1. 创建项目目录
mkdir project-name
cd project-name

# 2. 初始化 Git
git init

# 3. 创建虚拟环境
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 4. 安装核心依赖
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings
pip install python-jose passlib python-multipart
pip install openai fuzzywuzzy python-dotenv
pip install python-docx openpyxl pdfplumber aiofiles

# 5. 创建目录结构
mkdir -p app/api app/core app/models app/schemas app/services app/templates
mkdir -p uploads tests docs
```

### 1.2 配置文件初始化

```bash
# 创建 .env.example
cat > .env.example << EOF
SECRET_KEY=your-secret-key-at-least-32-chars
DATABASE_URL=sqlite:///./knowledge_base.db
OPENAI_API_KEY=sk-your-api-key
CORS_ORIGINS=*
ACCESS_TOKEN_EXPIRE_MINUTES=1440
MAX_FILE_SIZE=52428800
ALLOWED_FILE_EXTENSIONS=.pdf,.docx,.doc,.xlsx,.xls,.txt,.csv
EOF

# 复制为本地配置
cp .env.example .env
```

### 1.3 Git 忽略文件

```bash
# 创建 .gitignore
cat > .gitignore << EOF
venv/
__pycache__/
*.pyc
.env
uploads/
*.db
.DS_Store
*.log
.pytest_cache/
EOF
```

---

## 2. 需求分析流程

### 2.1 需求收集

| 来源 | 方式 | 记录格式 |
|------|------|----------|
| 用户访谈 | 会议纪要 | 用户故事 |
| 业务文档 | 文档审阅 | 功能清单 |
| 竞品分析 | 体验报告 | 差异点 |
| 技术调研 | 研究报告 | 可行性 |

### 2.2 需求分类

```
┌─────────────────────────────────────────┐
│              需求分类                    │
├─────────────┬─────────────┬─────────────┤
│  业务需求    │  用户体验   │   技术需求   │
│ Business    │    UX       │   Tech      │
├─────────────┼─────────────┼─────────────┤
│ 功能清单    │  界面交互   │  性能要求    │
│ 业务流程    │  响应速度   │  安全合规    │
│ 数据规范    │  易用性    │  扩展性      │
└─────────────┴─────────────┴─────────────┘
```

### 2.3 需求文档模板

```markdown
## 功能编号：F-001

### 功能名称
[简洁的功能描述]

### 用户故事
作为 [角色]，我希望 [功能]，以便 [价值]。

### 业务规则
- 规则1
- 规则2

### 输入输出
- 输入：xxx
- 输出：xxx

### 验收标准
- [ ] 标准1
- [ ] 标准2

### 优先级
- [ ] P0 - 核心功能
- [ ] P1 - 重要功能
- [ ] P2 - 优化功能
```

---

## 3. 架构设计流程

### 3.1 技术选型

| 层级 | 技术选型 | 选型理由 |
|------|----------|----------|
| 后端框架 | FastAPI | 高性能、自动文档、类型安全 |
| ORM | SQLAlchemy 2.0 | 成熟稳定、异步支持 |
| 数据库 | SQLite (Dev) / PostgreSQL (Prod) | 开发便捷、生产可靠 |
| 认证 | JWT + bcrypt | 标准方案、安全可靠 |
| AI 服务 | OpenAI API | 成熟稳定、成本可控 |

### 3.2 目录结构规范

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py              # 应用入口
│   ├── api/                 # API 路由
│   │   ├── __init__.py
│   │   ├── admin/          # 管理员接口
│   │   ├── store/          # 门店接口
│   │   └── auth.py          # 认证接口
│   ├── core/               # 核心配置
│   │   ├── __init__.py
│   │   ├── config.py       # 配置管理
│   │   ├── database.py     # 数据库连接
│   │   ├── security.py     # 安全认证
│   │   └── logging_config.py # 日志配置
│   ├── models/             # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── document.py
│   │   └── qa_item.py
│   ├── schemas/             # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── document.py
│   │   └── qa_item.py
│   ├── services/            # 业务逻辑
│   │   ├── __init__.py
│   │   ├── auto_classify.py      # AI 自动分类
│   │   ├── document_parser.py     # 文档解析
│   │   ├── qa_deduplication.py   # Q&A 查重
│   │   ├── llm_service.py        # LLM 调用服务
│   │   └── kb_categories.py      # 知识库分类体系
│   └── templates/           # 前端模板
├── config/                  # 项目配置
│   ├── .env.example         # 环境变量模板
│   ├── .gitignore           # Git 忽略配置
│   ├── requirements.txt     # 依赖清单
│   ├── render.yaml          # Render 部署配置
│   ├── run.py               # 生产环境启动
│   ├── run_local.py         # 本地开发启动
│   ├── run_simple.py        # 简化启动
│   └── start_local.bat      # Windows 启动
├── scripts/                 # 工具脚本
│   ├── db/                  # 数据库脚本
│   ├── deploy/              # 部署脚本
│   └── dev/                 # 开发脚本
├── tests/                   # 测试用例
├── instruction_docs/        # 项目文档
├── uploads/                 # 上传文件
└── knowledge_base.db        # SQLite 数据库
```

### 3.3 API 设计规范

```python
# API 命名规范
@router.post("/items")           # 创建
@router.get("/items")             # 列表
@router.get("/items/{item_id}")   # 获取单个
@router.put("/items/{item_id}")   # 更新
@router.delete("/items/{item_id}") # 删除

# 响应格式规范
{
    "code": 200,
    "message": "success",
    "data": {...}
}
```

---

## 4. 编码开发流程

### 4.1 数据模型开发

```python
# 步骤 1: 定义枚举
class DocStatus(str, Enum):
    pending = "pending"
    parsing = "parsing"
    parsed = "parsed"
    approved = "approved"
    rejected = "rejected"

# 步骤 2: 定义模型
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String(50), index=True)
    filename = Column(String(255))
    file_path = Column(String(500))
    status = Column(Enum(DocStatus), default=DocStatus.pending)

    # 软删除支持
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 步骤 3: 定义关系
    store = relationship("User", back_populates="documents")
```

### 4.2 Schema 定义

```python
# Pydantic 模型
class DocumentCreate(BaseModel):
    store_id: str
    filename: str
    file_path: str
    file_size: int
    car_model: Optional[str] = None
    category: Optional[str] = None

class DocumentResponse(BaseModel):
    id: int
    store_id: str
    filename: str
    status: DocStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

### 4.3 API 开发

```python
@router.post("/documents", response_model=DocumentResponse)
async def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. 权限校验
    if current_user.role != "admin" and current_user.store_id != document.store_id:
        raise HTTPException(status_code=403)

    # 2. 业务逻辑
    db_document = Document(**document.model_dump())
    db.add(db_document)
    db.commit()
    db.refresh(db_document)

    # 3. 返回响应
    return db_document
```

### 4.4 错误处理

```python
# 统一异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "Internal server error"}
    )
```

---

## 5. 测试验证流程

### 5.1 单元测试

```bash
# 安装测试依赖
pip install pytest pytest-asyncio httpx

# 运行测试
pytest tests/ -v
```

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_success():
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_failure():
    response = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "wrong"
    })
    assert response.status_code == 401
```

### 5.2 API 端点测试

```python
# 测试用例模板
class TestDocumentAPI:
    def setup_method(self):
        """每个测试方法前执行"""
        self.client = TestClient(app)
        self.token = self.get_token()

    def get_token(self):
        response = self.client.post("/api/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        return response.json()["access_token"]

    def test_upload_document(self):
        files = {"file": ("test.pdf", b"fake pdf content", "application/pdf")}
        response = self.client.post(
            "/api/store/upload_document",
            files=files,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        assert response.status_code == 200
```

### 5.3 质量检查清单

- [ ] 所有 API 端点有对应测试
- [ ] 边界条件有测试覆盖
- [ ] 错误处理有测试验证
- [ ] 无硬编码敏感信息
- [ ] 代码通过 lint 检查

---

## 6. 部署上线流程

### 6.1 生产环境检查

```bash
# 检查清单
[ ] SECRET_KEY 已配置（至少 32 字符）
[ ] DATABASE_URL 使用 PostgreSQL
[ ] CORS_ORIGINS 指定具体域名
[ ] OPENAI_API_KEY 已配置
[ ] DEBUG = False
[ ] 日志级别设置合理
```

### 6.2 数据库迁移

```python
# migrate_db.py
def migrate():
    """数据库迁移脚本"""
    inspector = inspect(engine)

    # 检查并添加缺失列
    existing_columns = [col["name"] for col in inspector.get_columns("qa_items")]

    if "is_deleted" not in existing_columns:
        # 添加列
        ...

    if "deleted_at" not in existing_columns:
        # 添加列
        ...
```

### 6.3 Render 部署

```
1. 连接 GitHub 仓库
2. 设置环境变量：
   - SECRET_KEY
   - OPENAI_API_KEY
   - DATABASE_URL
   - CORS_ORIGINS
3. 配置构建命令：
   pip install -r requirements.txt
4. 配置启动命令：
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
5. 启用 Auto Deploy
```

---

## 7. 运维监控流程

### 7.1 日志配置

```python
# logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            RotatingFileHandler("app.log", maxBytes=10*1024*1024),
            logging.StreamHandler()
        ]
    )
```

### 7.2 健康检查

```python
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.utcnow().isoformat()
    }
```

### 7.3 监控指标

| 指标 | 告警阈值 | 处理方式 |
|------|----------|----------|
| API 响应时间 > 5s | 发送告警 | 检查慢查询 |
| 错误率 > 5% | 发送告警 | 检查服务状态 |
| 数据库连接 > 80% | 发送告警 | 连接池扩容 |
| 磁盘使用 > 90% | 发送告警 | 清理日志/文件 |

---

## 8. 知识沉淀流程

### 8.1 沉淀内容

| 类型 | 内容 | 存储位置 |
|------|------|----------|
| README | 项目概述、架构、使用 | docs/README.md |
| agent.md | AI 技能、规则 | docs/agent.md |
| Rules | 业务规则 | docs/Rules/*.md |
| Prompts | 优质 Prompt | docs/prompts/*.md |
| Code | 可复用代码 | docs/code/*.py |
| SOP | 开发流程 | docs/SOP.md |

### 8.2 沉淀时机

```
开发完成 → 立即沉淀
  ↓
代码审查 → 补充规则
  ↓
问题解决 → 记录方案
  ↓
项目复盘 → 总结经验
```

### 8.3 沉淀检查清单

- [ ] 每次功能开发后更新 README
- [ ] 遇到的问题及解决方案记录
- [ ] 有效的 Prompt 模板保存
- [ ] 可复用代码及时抽取
- [ ] 项目复盘后更新 SOP

---

## 📝 版本记录

| 版本 | 日期 | 变更内容 | 作者 |
|------|------|----------|------|
| v1.0 | 2026-04-08 | 初始版本 | AI Assistant |
