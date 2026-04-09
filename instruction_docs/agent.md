# AI Agent 技能与规则

> 本文档沉淀了 4S 店售后知识库项目中 AI Agent 的行为规则、可复用技能和最佳实践

---

## 🎯 Agent 角色定义

### 系统角色
```yaml
角色: 企业知识库系统开发专家
专长:
  - FastAPI Web 开发
  - SQLAlchemy 数据库设计
  - Vue/React 前端开发
  - LLM 集成与应用
  - 系统架构设计

行为准则:
  - 代码优先：先实现再优化
  - 安全第一：不暴露敏感信息
  - 用户中心：理解真实需求再动手
  - 持续沉淀：总结可复用经验
```

### 技能等级
| 等级 | 描述 | 适用场景 |
|------|------|----------|
| L1 | 基础 CRUD | 简单增删改查 |
| L2 | 业务逻辑 | 复杂状态流转 |
| L3 | 系统设计 | 架构规划与优化 |
| L4 | 创新突破 | 新技术探索与应用 |

---

## 🛠️ 可复用技能

### 1. FastAPI 开发技能

#### 1.1 标准 API 结构
```python
@router.post("/endpoint")
async def create_item(
    item: ItemCreate,                          # Pydantic 模型验证
    current_user: User = Depends(get_current_user),  # 权限校验
    db: Session = Depends(get_db)               # 数据库连接
):
    """API 端点文档字符串"""
    # 业务逻辑
    return {"message": "success", "data": item}
```

#### 1.2 依赖注入模式
```python
# 通用依赖
async def get_current_user(token: str = Depends(oauth2_scheme), ...)

# 角色特定依赖
async def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403)
    return current_user
```

#### 1.3 错误处理模式
```python
@app.exception_handler(CustomException)
async def custom_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

### 2. 数据库设计技能

#### 2.1 SQLAlchemy 模型
```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(255))
    role = Column(Enum(UserRole))

    # 关系
    documents = relationship("Document", back_populates="owner")
```

#### 2.2 软删除模式
```python
class SoftDeleteMixin:
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)

# 使用
query.filter(Model.is_deleted == False)
```

#### 2.3 枚举状态模式
```python
class DocStatus(str, Enum):
    pending = "pending"
    parsing = "parsing"
    parsed = "parsed"
    approved = "approved"
    rejected = "rejected"
```

### 3. 前端交互技能

#### 3.1 Token 管理
```javascript
// 存储
localStorage.setItem('token', response.access_token)

// 请求头
headers: { 'Authorization': `Bearer ${token}` }

// 响应拦截
if (response.status === 401) {
    localStorage.removeItem('token');
    window.location.href = '/login';
}
```

#### 3.2 API 调用封装
```javascript
async function apiCall(url, method = 'GET', data = null) {
    const token = localStorage.getItem('token');
    const options = {
        method,
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    };
    if (data) options.body = JSON.stringify(data);

    const response = await fetch(url, options);
    if (!response.ok) throw new Error(await response.text());
    return response.json();
}
```

### 4. LLM 集成技能

#### 4.1 API 调用模式
```python
import openai

async def classify_with_llm(text: str) -> dict:
    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是一个分类助手"},
            {"role": "user", "content": f"分类以下文本: {text}"}
        ],
        temperature=0.3
    )
    return parse_response(response)
```

#### 4.2 Prompt 模板
```python
CLASSIFY_PROMPT = """
请为以下文本分类：

文本：{content}

要求：
1. 提取主分类（一个大类）
2. 提取子分类（一个具体小类）
3. 返回 JSON 格式

返回格式：
{{"main_category": "主分类", "sub_category": "子分类"}}
"""
```

### 5. 文本查重技能

#### 5.1 FuzzyWuzzy 查重
```python
from fuzzywuzzy import fuzz

def check_similarity(text1: str, text2: str) -> float:
    ratio = fuzz.ratio(text1.lower(), text2.lower())
    return ratio / 100.0

def find_duplicates(texts: list[str], threshold: float = 0.85) -> list[list[int]]:
    duplicates = []
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            if check_similarity(texts[i], texts[j]) >= threshold:
                duplicates.append([i, j])
    return duplicates
```

---

## 📋 Agent 行为规则

### 开发规则

#### 需求理解规则
1. **先确认再动手**：不理解需求不写代码
2. **追问细节**：数据类型、边界条件、异常处理
3. **原型验证**：复杂功能先做 MVP

#### 代码质量规则
1. **安全第一**：
   - 敏感信息绝不硬编码
   - 使用环境变量
   - SQL 参数化查询
2. **防御性编程**：
   - 输入验证
   - 空值检查
   - 异常捕获
3. **可维护性**：
   - 清晰的命名
   - 适当的注释
   - 模块化设计

#### 错误处理规则
```
优先级: 防御 > 捕获 > 记录 > 报告

1. 预期错误：用户输入验证 → 友好提示
2. 运行时错误：try-except → 日志记录 → 降级处理
3. 未知错误：全局捕获 → 通用响应 → 日志追踪
```

### 状态管理规则

#### 文档状态流转
```
pending → parsing → parsed → approved/rejected
  ↓
(如有错误) → parse_error
```

#### Q&A 状态流转
```
pending_review → published (审核通过)
                  ↓
            rejected (审核拒绝)
                  ↓
         (软删除) → is_deleted=true
```

### 安全规则

#### 认证与授权
```python
# JWT Token 有效期
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24小时

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"])

# 角色检查
def require_role(user: User, allowed_roles: list):
    if user.role not in allowed_roles:
        raise HTTPException(status_code=403)
```

#### CORS 配置
```python
# 生产环境：指定具体域名
allow_origins = ["https://your-domain.com"]

# 开发环境：允许所有
allow_origins = ["*"]
```

---

## 🔄 问题解决模式

### 1. Bug 排查模式
```
症状观察 → 日志分析 → 代码追踪 → 根因定位 → 修复验证
```

### 2. 性能优化模式
```
瓶颈识别 → 热点分析 → 方案设计 → 实施验证
```

### 3. 安全审计模式
```
敏感信息检查 → 权限验证 → 输入校验 → 日志审计
```

---

## 📚 经验沉淀清单

### 项目启动清单
- [ ] 需求文档评审
- [ ] 技术选型确认
- [ ] 目录结构规划
- [ ] 数据库设计评审
- [ ] API 接口设计评审

### 开发过程清单
- [ ] 代码规范检查
- [ ] 单元测试覆盖
- [ ] 安全漏洞扫描
- [ ] 性能基准测试
- [ ] 文档同步更新

### 部署上线清单
- [ ] 环境变量配置
- [ ] 数据库迁移
- [ ] 回滚方案准备
- [ ] 监控告警设置
- [ ] 验证测试执行

---

## 🎓 技能评估标准

### L1 - 基础
- [ ] 理解项目结构
- [ ] 完成简单 CRUD
- [ ] 阅读现有代码
- [ ] 修复简单 Bug

### L2 - 进阶
- [ ] 设计新功能模块
- [ ] 编写测试用例
- [ ] 优化查询性能
- [ ] 处理复杂业务逻辑

### L3 - 专家
- [ ] 系统架构设计
- [ ] 性能瓶颈诊断
- [ ] 安全方案制定
- [ ] 团队代码评审

### L4 - 大师
- [ ] 新技术探索
- [ ] 架构演进规划
- [ ] 技术难点攻关
- [ ] 知识传承分享

---

## 📝 变更记录

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|----------|------|
| 2026-04-08 | v1.0 | 初始版本 | AI Assistant |
