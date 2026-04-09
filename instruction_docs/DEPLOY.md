# 4S 店售后知识库 - 部署指南

## 📋 目录
- [本地测试](#本地测试)
- [Render 云平台部署](#render-云平台部署)
- [Linux 服务器部署](#linux-服务器部署)
- [Windows 服务器部署](#windows-服务器部署)

---

## 🖥️ 本地测试

### 方法一：使用启动脚本
```bash
# Windows
.\start_local.bat

# 或直接运行
python run_simple.py
```

### 方法二：手动启动
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化数据库
python init_db.py

# 3. 启动服务
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

访问地址：
- 前端：http://localhost:8000
- API 文档：http://localhost:8000/docs

---

## ☁️ Render 云平台部署

### 步骤：

1. **连接 GitHub 仓库**
   - 登录 [Render](https://render.com)
   - 点击 "New +" → "Web Service"
   - 连接你的 GitHub 仓库

2. **配置服务**
   ```yaml
   # render.yaml 已包含配置
   - 名称：store-knowledge-base
   - 环境：Python 3
   - 构建命令：pip install -r requirements.txt
   - 启动命令：uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

3. **设置环境变量**
   在 Render Dashboard 中添加：
   ```
   DATABASE_URL=postgresql://...  # Render PostgreSQL 连接字符串
   SECRET_KEY=your-production-secret-key
   UPLOAD_DIR=/tmp/uploads/docs
   QA_UPLOAD_DIR=/tmp/uploads/qa
   ```

4. **部署**
   - 点击 "Create Web Service"
   - 等待自动构建和部署
   - 获取 Render 分配的域名

---

## 🐧 Linux 服务器部署

### 系统要求：
- Ubuntu 20.04+ / CentOS 7+
- Python 3.8+
- Git
- Nginx（可选，用于反向代理）

### 快速部署（使用部署脚本）

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/your-repo.git
cd your-repo

# 2. 运行部署脚本
python3 deploy.py

# 3. 按照提示启动服务
```

### 手动部署

#### 1. 安装依赖
```bash
# 安装系统依赖
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx

# 安装 Python 依赖
pip3 install -r requirements.txt
```

#### 2. 配置数据库
```bash
# 使用 SQLite（测试环境）
python3 init_db.py

# 或使用 PostgreSQL（生产环境）
sudo apt install -y postgresql postgresql-contrib
sudo -u postgres psql
# 创建数据库和用户...
```

#### 3. 配置 systemd 服务

```bash
# 复制服务配置文件
sudo cp store-knowledge-base.service /etc/systemd/system/

# 编辑配置（修改路径和环境变量）
sudo nano /etc/systemd/system/store-knowledge-base.service

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable store-knowledge-base
sudo systemctl start store-knowledge-base

# 查看状态
sudo systemctl status store-knowledge-base
```

#### 4. 配置 Nginx（可选）

```nginx
# /etc/nginx/sites-available/store-knowledge-base
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 100M;  # 允许上传大文件
}
```

```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/store-knowledge-base /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

#### 5. 配置防火墙

```bash
# Ubuntu (UFW)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

---

## 🪟 Windows 服务器部署

### 使用 IIS + HttpPlatformHandler

1. **安装组件**
   - IIS
   - HttpPlatformHandler
   - Python 3.8+

2. **配置站点**
   - 在 IIS 中创建网站
   - 设置物理路径为项目根目录
   - 配置处理程序映射

3. **web.config 配置**
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <configuration>
     <system.webServer>
       <handlers>
         <add name="PythonFastCGI" path="*" verb="*" modules="FastCgiModule" 
              scriptProcessor="C:\Python39\python.exe|C:\path\to\app\main.py" 
              resourceType="Unspecified" />
       </handlers>
     </system.webServer>
   </configuration>
   ```

### 使用简单方式（推荐）

```batch
# 1. 运行启动脚本
start.bat

# 或使用 NSSM 创建 Windows 服务
nssm install StoreKnowledgeBase "C:\Python39\python.exe" "-m uvicorn app.main:app --host 0.0.0.0 --port 8000"
nssm start StoreKnowledgeBase
```

---

## 🔧 环境变量配置

### 必需的环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `DATABASE_URL` | 数据库连接字符串 | `sqlite:///./knowledge_base.db` |
| `SECRET_KEY` | JWT 密钥（生产环境必须修改） | `your-secret-key` |
| `UPLOAD_DIR` | 文档上传目录 | `/var/uploads/docs` |
| `QA_UPLOAD_DIR` | QA 上传目录 | `/var/uploads/qa` |

### 可选的环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `PORT` | 服务端口 | `8000` |
| `HOST` | 服务主机 | `0.0.0.0` |
| `DEBUG` | 调试模式 | `False` |

---

## 📊 生产环境建议

### 1. 数据库
- 使用 PostgreSQL 代替 SQLite
- 配置数据库连接池
- 定期备份数据库

### 2. 安全性
- 修改默认管理员密码
- 设置强 SECRET_KEY
- 配置 HTTPS
- 限制上传文件大小
- 配置 CORS

### 3. 性能优化
- 使用 Gunicorn/Uvicorn workers
- 配置 Redis 缓存（可选）
- 启用 Gzip 压缩
- 配置 CDN（静态资源）

### 4. 监控
- 配置日志记录
- 使用 Sentry 错误追踪
- 配置健康检查端点
- 设置告警通知

---

## 🐛 常见问题

### 1. 端口被占用
```bash
# 查看占用端口的进程
lsof -i :8000
# 或
netstat -tulpn | grep 8000

# 杀死进程
kill -9 <PID>
```

### 2. 权限问题
```bash
# 修改目录权限
sudo chown -R www-data:www-data /var/www/store-knowledge-base
sudo chmod -R 755 /var/www/store-knowledge-base
```

### 3. 依赖安装失败
```bash
# 升级 pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. 数据库迁移
```bash
# 如果需要迁移数据
python manage.py db migrate
python manage.py db upgrade
```

---

## 📞 技术支持

如有问题，请提交 Issue 或联系开发团队。
