# 服务器更新指南

## 📋 快速更新（推荐）

### 方式一：使用更新脚本

```bash
# SSH 登录服务器
ssh user@your-server-ip

# 进入项目目录
cd /path/to/store-knowledge-base

# 运行更新脚本
python update_server.py

# 重启服务
# 如果使用 systemd:
sudo systemctl restart store-knowledge-base

# 如果直接运行:
# 先停止当前服务 (Ctrl+C)
# 然后重新运行:
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 方式二：手动更新

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 安装依赖
pip install -r requirements.txt

# 3. 数据库迁移（如果需要）
python migrate_db.py

# 4. 重启服务
sudo systemctl restart store-knowledge-base
```

---

## 🔄 完整更新流程

### 1. 备份数据（重要！）

```bash
# 备份数据库
cp knowledge_base_local.db knowledge_base_local.db.backup.$(date +%Y%m%d)

# 备份上传的文件
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/
```

### 2. 停止服务

```bash
# systemd 方式
sudo systemctl stop store-knowledge-base

# 或直接停止运行的进程
# 按 Ctrl+C
```

### 3. 更新代码

```bash
# 拉取最新代码
git pull origin main

# 查看更新内容
git log --oneline -10
```

### 4. 安装依赖

```bash
# 激活虚拟环境（如果使用）
source .venv/bin/activate  # Linux
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 5. 数据库迁移

```bash
# 运行迁移脚本
python migrate_db.py
```

### 6. 启动服务

```bash
# systemd 方式
sudo systemctl start store-knowledge-base

# 或直接运行
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 7. 验证更新

```bash
# 检查服务状态
sudo systemctl status store-knowledge-base

# 查看日志
sudo journalctl -u store-knowledge-base -f

# 测试访问
curl http://localhost:8000/api/admin/stats
```

---

## 📊 更新内容说明

### 最新版本：2026-04-07

#### 新增功能
1. **回收站恢复功能**
   - 批量恢复已删除的 QA
   - 回收站标签页

2. **查重功能**
   - 基于 fuzzywuzzy 的文本相似度检测
   - 85% 相似度阈值
   - 审核时自动检测重复

3. **文档解析增强**
   - 修复 DocumentQA 表缺失问题
   - 自动解析 PDF/Word/TXT 文档
   - 提取 Q&A 并自动分类

#### 修复问题
1. 数据库表结构不完整
2. 文档解析功能异常
3. 管理员端看不到已解析文档

#### 新增文件
- `update_server.py` - 服务器更新脚本
- `migrate_db.py` - 数据库迁移脚本
- `check_documents.py` - 文档数据检查工具
- `DEPLOY.md` - 详细部署文档

---

## 🔧 常见问题

### 1. 更新后服务无法启动

```bash
# 查看错误日志
sudo journalctl -u store-knowledge-base -n 50

# 检查依赖
pip install -r requirements.txt

# 检查数据库
python migrate_db.py
```

### 2. 数据库迁移失败

```bash
# 备份数据库
cp knowledge_base_local.db knowledge_base_local.db.backup

# 手动执行迁移
python migrate_db.py

# 如果仍然失败，恢复备份
cp knowledge_base_local.db.backup knowledge_base_local.db
```

### 3. 代码冲突

```bash
# 查看冲突文件
git status

# 手动解决冲突
# 编辑冲突文件，解决 <<<<<<< 和 >>>>>>> 之间的内容

# 提交解决
git add <冲突文件>
git commit -m "解决冲突"
git push origin main
```

---

## 📝 更新检查清单

- [ ] 备份数据库和上传文件
- [ ] 停止服务
- [ ] 拉取最新代码
- [ ] 安装依赖
- [ ] 运行数据库迁移
- [ ] 启动服务
- [ ] 检查服务状态
- [ ] 测试前端功能
- [ ] 测试 API 接口
- [ ] 查看日志无错误

---

## 🎯 回滚方案

如果更新后出现问题，可以快速回滚：

```bash
# 1. 停止服务
sudo systemctl stop store-knowledge-base

# 2. 恢复数据库
cp knowledge_base_local.db.backup.$(date +%Y%m%d) knowledge_base_local.db

# 3. 回滚代码
git revert HEAD  # 回滚上一次提交
# 或
git reset --hard <previous-commit-hash>

# 4. 启动服务
sudo systemctl start store-knowledge-base
```

---

## 📞 技术支持

如有问题，请查看：
- 完整部署文档：`DEPLOY.md`
- 项目 Issues：https://github.com/linxiangxuan9876/-.git/issues
