# 协作规范

## 分支模型

- `main`：稳定分支，**只通过 Pull Request 合入**，任何人不得直接 push
- 功能分支：从最新 `main` 拉出，命名 `feature/<简短描述>`，例如 `feature/asr-local-upload`
- 修复分支：`fix/<简短描述>`，例如 `fix/qa-split-missing-item`
- 一个分支只做一件事，做完就发 PR，合并后删除分支

## 提交流程

```bash
# 1. 同步主干
git checkout main
git pull origin main

# 2. 开新分支
git checkout -b feature/your-feature

# 3. 开发 + 提交（commit 信息说清"做了什么、为什么"）
git add <文件>
git commit -m "feat: 简历解析支持 docx 格式"

# 4. 推送并发起 PR
git push -u origin feature/your-feature
```

然后在 GitHub 上发起 Pull Request，描述中写清：
- 改了什么
- 为什么这么改
- 怎么验证（跑了什么命令 / 看到了什么结果）

## Commit 信息约定

```
feat: 新功能
fix: 修复问题
docs: 文档
refactor: 重构（不改行为）
eval: 评测相关（测试集、指标、prompt 对比）
chore: 杂项（依赖、配置）
```

## 环境

```powershell
.\scripts\setup.ps1      # 创建 .venv 并安装依赖
copy .env.example .env    # 填入自己的 DASHSCOPE_API_KEY
.\.venv\Scripts\Activate.ps1
python app.py
```

## 🔒 数据红线（重要）

- **绝不提交** `.env`、API Key、真实简历、真实面试录音、生成的复盘报告
- 这些已在 `.gitignore` 中排除，新增文件类型时请同步更新 `.gitignore`
- 演示数据只能用 `demo/` 下的仿真数据（已脱敏、无真实个人信息）
- 提交前自检：`git status` 里不应出现任何 `.env`、音频文件、docx 报告

## 代码风格

- 新增模块在文件头写清"这个模块解决什么问题、为什么这么设计"
- prompt 修改请同步在 PR 描述里说明改动理由（便于评测对比）
- 不引入新依赖前先说明理由（避免依赖膨胀）
