# 4S店售后知识库系统

> 基于 FastAPI + SQLAlchemy 的企业级知识管理平台

## 📖 项目概述

### 核心价值
- **问题解决**：帮助门店员工快速查找标准售后问题答案
- **知识沉淀**：将分散的售后经验转化为可复用的知识库
- **效率提升**：减少重复咨询，提升服务响应速度

### 目标用户
| 角色 | 权限 | 核心功能 |
|------|------|----------|
| 门店员工 | 上传文档、查询知识、提交 Q&A | 日常知识获取与贡献 |
| 管理员 | 审核内容、管理用户、数据分析 | 质量把控与运营分析 |

---

## 🏗️ 系统架构

### 技术栈

```
┌─────────────────────────────────────────────────────────┐
│                      前端层                              │
│  HTML5 + Jinja2 Templates + Vanilla JavaScript         │
├─────────────────────────────────────────────────────────┤
│                      API 层                             │
│         FastAPI + Pydantic + OAuth2 + JWT              │
├─────────────────────────────────────────────────────────┤
│                      业务层                             │
│  DocumentParser | QADeduplication | AutoClassify       │
├─────────────────────────────────────────────────────────┤
│                      数据层                             │
│       SQLAlchemy 2.0 + SQLite/PostgreSQL              │
├─────────────────────────────────────────────────────────┤
│                      AI 服务                            │
│        OpenAI GPT-3.5 + SiliconFlow API               │
└─────────────────────────────────────────────────────────┘
```

### 目录结构

```
├── app/                          # 应用代码
│   ├── api/                      # API 路由
│   │   ├── admin/                # 管理员接口
│   │   ├── store/                # 门店接口
│   │   └── auth.py               # 认证接口
│   ├── core/                     # 核心配置
│   │   ├── config.py             # 配置管理
│   │   ├── database.py           # 数据库连接
│   │   ├── security.py           # 安全认证
│   │   └── logging_config.py     # 日志配置
│   ├── models/                   # 数据模型
│   ├── schemas/                  # Pydantic 模型
│   ├── services/                 # 业务逻辑
│   │   ├── auto_classify.py      # AI 自动分类（关键词匹配 + LLM）
│   │   ├── document_parser.py    # 文档解析
│   │   ├── qa_deduplication.py   # Q&A 查重
│   │   ├── llm_service.py        # LLM 调用服务
│   │   └── kb_categories.py      # 知识库分类体系
│   ├── templates/                # 前端页面
│   └── main.py                   # 应用入口
├── config/                       # 项目配置和启动脚本
│   ├── .env.example              # 环境变量模板
│   ├── .gitignore                # Git 忽略配置
│   ├── requirements.txt          # 依赖清单
│   ├── render.yaml               # Render 部署配置
│   ├── run.py                    # 生产环境启动脚本
│   ├── run_local.py              # 本地开发启动脚本
│   ├── run_simple.py             # 简化启动脚本
│   └── start_local.bat           # Windows 本地启动批处理
├── instruction_docs/             # 项目文档
├── scripts/                      # 工具脚本
│   ├── db/                       # 数据库脚本
│   ├── deploy/                   # 部署脚本
│   └── dev/                      # 开发脚本
├── tests/                        # 测试脚本
├── uploads/                      # 文件上传目录
└── knowledge_base.db             # SQLite 数据库
```

---

## 🚀 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+ (可选)

### 安装步骤

```bash
# 1. 克隆代码
git clone <repository-url>
cd 门店知识库

# 2. 创建虚拟环境
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 3. 安装依赖
pip install -r config/requirements.txt

# 4. 配置环境变量
cp config/.env.example .env
# 编辑 .env 填入实际值

# 5. 启动服务
python config/run.py
```

### 默认账号
| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 门店 | store1 | store123 |

---

## 📝 核心功能

### 1. 文档上传与管理
- 支持 PDF、Word、Excel、TXT 等格式
- 自动解析提取 Q&A 内容
- 文档状态跟踪（待解析、解析中、已解析）

### 2. Q&A 知识库
- 批量导入 Q&A（Excel/CSV）
- AI 自动分类（主分类 + 子分类）
- 智能查重（85% 相似度阈值）

### 3. 审核工作流
- 待审核队列
- 查重检测提醒
- 批量审核操作

### 4. 回收站
- 软删除机制
- 恢复功能
- 彻底删除

---

## 🔐 安全配置

### 生产环境必做

1. **设置强密钥**
   ```env
   SECRET_KEY=your-32-char-strong-key-here
   ```

2. **配置 API Key（SiliconFlow）**
   ```env
   OPENAI_API_KEY=sk-your-actual-key
   OPENAI_MODEL=gpt-3.5-turbo
   OPENAI_BASE_URL=https://api.siliconflow.cn/v1
   ```

3. **限制 CORS**
   ```env
   CORS_ORIGINS=https://your-domain.com
   ```

4. **使用 PostgreSQL**
   ```env
   DATABASE_URL=postgresql://user:pass@host:5432/dbname
   ```

---

## 📋 环境变量说明

| 环境变量 | 默认值 | 必填 | 说明 |
|----------|--------|------|------|
| `SECRET_KEY` | - | 是 | JWT 签名密钥（至少32字符） |
| `DATABASE_URL` | sqlite:///./knowledge_base.db | 否 | 数据库连接地址 |
| `OPENAI_API_KEY` | - | 是 | SiliconFlow API 密钥 |
| `OPENAI_MODEL` | gpt-3.5-turbo | 否 | 模型名称 |
| `OPENAI_BASE_URL` | https://api.siliconflow.cn/v1 | 否 | API 地址 |
| `CORS_ORIGINS` | * | 否 | 允许的跨域域名 |
| `MAX_FILE_SIZE` | 52428800 | 否 | 文件大小限制（字节） |
| `UPLOAD_DIR` | ./uploads/docs | 否 | 文档上传目录 |
| `QA_UPLOAD_DIR` | ./uploads/qa | 否 | Q&A 上传目录 |

---

## 🌐 API 接口

### 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/auth/login | 用户登录 |

### 门店端
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/store/info | 获取门店信息 |
| POST | /api/store/upload_document | 上传文档 |
| POST | /api/store/upload_qa_batch | 批量导入 Q&A |
| GET | /api/store/my_docs | 我的文档 |

### 管理员端
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/admin/stats | 看板统计 |
| GET | /api/admin/all_docs | 所有文档 |
| GET | /api/admin/all_qa | 所有 Q&A |
| PUT | /api/admin/review_qa/{id} | 审核 Q&A |
| POST | /api/admin/check_duplicates | 查重检测 |
| GET | /api/admin/recycle_bin | 回收站 |
| POST | /api/admin/restore_qa/{id} | 恢复 Q&A |

---

## 📊 数据模型

### User（用户）
```python
- id: int
- username: str
- hashed_password: str
- store_id: str
- store_name: str
- role: enum(admin/store)
```

### Document（文档）
```python
- id: int
- store_id: str
- filename: str
- file_path: str
- file_size: int
- car_model: str
- category: str
- status: enum(pending/parsing/parsed/approved/rejected)
```

### QA_Item（知识条目）
```python
- id: int
- store_id: str
- main_category: str
- sub_category: str
- question: str
- answer: str
- status: enum(published/pending_review/rejected)
- is_deleted: bool
```

---

## 🔧 开发指南

### 添加新功能
1. 在 `app/models/` 添加数据模型
2. 在 `app/schemas/` 添加 Pydantic 模型
3. 在 `app/api/` 添加 API 路由
4. 在 `app/services/` 添加业务逻辑
5. 更新数据库：`python migrate_db.py`

### 测试
```bash
# 运行测试
pytest

# 测试特定模块
pytest tests/test_api.py -v
```

---

## 📦 部署

### Docker（推荐）
```bash
docker build -t knowledge-base .
docker run -d -p 8000:8000 --env-file .env knowledge-base
```

### Render 部署
1. 连接 GitHub 仓库
2. 设置环境变量
3. 启用 Auto Deploy

---

## 📄 许可证

MIT License

---

## 👥 团队

技术部 - 2026
