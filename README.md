# Django用户管理API项目

这是一个使用Django和Django REST Framework构建的用户管理API项目，使用SQLite数据库和uv包管理器。

## 项目结构

- `myproject/` - Django项目配置
- `users/` - 用户管理应用
- `manage.py` - Django管理脚本

## 安装和运行

1. 安装依赖（如果需要）：
   ```bash
   uv pip install Django djangorestframework
   ```

2. 运行数据库迁移：
   ```bash
   uv run python manage.py migrate
   ```

3. 启动开发服务器：
   ```bash
   uv run python manage.py runserver
   ```

4. 创建超级用户（可选）：
   ```bash
   # 使用脚本创建
   uv run python create_superuser.py
   ```

## API端点

- `GET /api/users/` - 获取所有用户列表
- `POST /api/users/` - 创建新用户
- `GET /api/users/<id>/` - 获取特定用户详情
- `PUT /api/users/<id>/` - 更新特定用户
- `DELETE /api/users/<id>/` - 删除特定用户

## 管理界面

- 访问 `http://localhost:8000/admin/` 进入管理界面
- 使用创建的超级用户凭据登录

## 数据库

- 默认使用SQLite数据库 (`db.sqlite3`)
- 可以在 `myproject/settings.py` 中修改数据库配置

## 包管理

- 使用 `uv` 作为包管理器
- Django版本: 3.2.25
- Django REST Framework版本: 3.15.1