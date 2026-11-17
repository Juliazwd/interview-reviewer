# 面试复盘助手 (Interview Reviewer)

把一场面试的**简历 PDF + 录音**丢进去，输出三段式复盘报告：**问了什么 → 答得怎样 → 下次怎么改**，一键导出 Word。

> 目标用户：正在找实习/校招的学生。面试后凭记忆复盘不系统，本工具基于转写原文和简历原话给出有据可查的点评。

## 产品架构

```
简历 PDF ──docling──▶ 结构化章节 ──embedding──▶ 简历段落索引
                                                    │ (对齐，轻量RAG)
录音 ──ASR(说话人分离)──▶ 转写 ──QA切分──▶ 逐题点评(JSON Schema) ──汇总──▶ Word 报告
```

技术选型的"为什么"（核心决策记录）：

| 决策 | 理由 |
|---|---|
| docling 解析简历（非普通抽文本） | 复盘需定位面试官深挖的是简历"哪一段经历"，纯文本流无段落边界 |
| 两阶段流水线（QA 切分 + 逐题点评） | 60 分钟录音直接总结会丢细节、成本高；先切题再逐题分析 |
| 轻量 RAG（内存余弦相似度） | 点评引用必须有出处（防幻觉）；一份简历十几个章节，无需向量数据库 |
| JSON Schema 强制输出 | 报告要导出 Word、要算评测指标，自由文本无法机器校验 |
| 通义千问 + Paraformer（同一家） | ASR/LLM/Embedding 共用一个 API Key，接入成本最低 |
| 不做多 Agent 框架 | 单条流水线可完成，多 agent 只增加不确定性 |

## 快速开始

```powershell
# 1. 一键初始化（创建隔离虚拟环境 .venv 并安装依赖，推荐）
.\scripts\setup.ps1

# 2. 配置 API Key（阿里云百炼，新用户有免费额度）
#    https://bailian.console.aliyun.com/ -> API-KEY 管理
copy .env.example .env   # 编辑 .env 填入 DASHSCOPE_API_KEY

# 3. 激活环境并启动
.\.venv\Scripts\Activate.ps1
python app.py
```

> 环境隔离说明：本项目依赖安装在项目目录内的 `.venv/`（已加入 `.gitignore`），与系统 Python 及其他项目完全隔离。IDE 使用时请把 Python 解释器指向 `.\.venv\Scripts\python.exe`。

**注意**：DashScope 录音文件识别要求音频可通过公网 URL 访问（如 OSS 直链）。本地文件请先上传到 OSS，或等待后续版本接入本地流式识别。

## 评测体系（进行中）

- 测试集：20+ 场真实模拟面试录音 + 人工标注 ground truth
- 指标：问题召回率 / 点评命中率 / 幻觉率
- 评测流水线：LLM-as-Judge + 人工标注回归（见 `evaluation/`）

## 路线图

- [x] 最小闭环：简历解析 → 转写 → QA 切分 → 逐题点评 → Word 导出
- [ ] 简历-问题对齐评测与调优
- [ ] LLM-as-Judge 自动评测流水线
- [ ] 合规设计：录音知情同意提示、转写数据不落盘
- [ ] 复盘追问 Agent：基于工具调用的报告追问，回答带原文出处
- [ ] 投递进度追踪 Agent：一句话自动归档进展（设计见 docs/application_tracker_design.md，MVP 后实现）
- [ ] 说话人身份确认/翻转 UI
- [ ] 本地音频流式识别（免 OSS 上传）
- [ ] 历史复盘对比（弱点趋势/进步曲线）
- [ ] 商业化方案（见 docs/，只做方案不做实现）

## 竞品分析与差异化

见 [docs/competitive_analysis.md](docs/competitive_analysis.md)：调研 8 个同类开源项目后的结论——
不拼功能广度，拼**可验证的效果**（评测体系）、**引用溯源防幻觉**、**合规设计**。

## License

MIT
