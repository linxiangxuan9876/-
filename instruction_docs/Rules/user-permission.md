# 用户与权限规则

## 用户类型

| 角色 | 标识 | 权限等级 | 可操作 |
|------|------|----------|--------|
| 管理员 | admin | HIGH | 审核、删除、管理用户 |
| 门店用户 | store | NORMAL | 上传、查询、提交 |

## 用户创建规则

### 默认用户初始化
```python
# 应用启动时自动创建
def init_default_users():
    # 管理员账号
    admin = User(
        username="admin",
        hashed_password=get_password_hash("admin123"),
        store_id="HQ001",
        store_name="总部",
        role=UserRole.admin
    )

    # 门店账号
    store_user = User(
        username="store1",
        hashed_password=get_password_hash("store123"),
        store_id="STORE001",
        store_name="北京朝阳区门店",
        role=UserRole.store
    )
```

## 密码规则

### 密码要求
- 最少 6 字符
- 无复杂度要求（当前实现）
- 建议：字母+数字组合

### 密码存储
- 使用 bcrypt 加密
- 不得明文存储
- 不得日志输出

## 权限校验规则

### API 权限层级
```python
# 公开接口
/auth/login - 无需认证

# 门店接口
/store/* - 需要 store 或 admin 角色

# 管理员接口
/admin/* - 仅限 admin 角色
```

### 权限检查流程
```
1. 验证 Token 有效性
2. 检查 Token 是否过期
3. 验证用户是否存在
4. 检查用户角色是否匹配
5. 通过则继续，失败则返回 401/403
```

## Session 管理

### Token 有效期
- 默认：1440 分钟（24 小时）
- 可配置
- 过期后需重新登录

### Token 结构
```json
{
  "sub": "user_id",
  "role": "admin/store",
  "store_id": "STORE001",
  "exp": 1775724438
}
```
