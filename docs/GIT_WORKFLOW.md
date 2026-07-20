# Git 工作流

## 分支

- `main`：始终保持可运行
- `develop`：日常集成
- `feature/*`：单个功能

初始创建：

```powershell
git checkout -b develop
git push -u origin develop
```

开发新功能示例：

```powershell
git checkout develop
git pull
git checkout -b feature/image-upload
```

完成后：

```powershell
git add .
git commit -m "feat: add image upload preview"
git push -u origin feature/image-upload
```

## Commit 约定

- `feat:` 新功能
- `fix:` 修复
- `docs:` 文档
- `refactor:` 重构
- `test:` 测试
- `chore:` 工程配置

不要提交：

- API Key
- `.env`
- 数据库密码
- `node_modules`
- `.venv`
- 用户上传图片
- 大模型权重
