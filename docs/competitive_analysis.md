# 竞品调研与差异化策略（2026-11-13）

## 调研范围

GitHub 上同类"AI 面试助手/复盘"开源项目 8 个，重点深挖 2 个：
- [EasyWork-Interview](https://github.com/fuhuonvshen/EasyWork-Interview)（最直接竞品）
- [dovics/interview_agent](https://github.com/dovics/interview_agent)（agent 方向参考）

其他同类项目（Recruitify、AI-Interview-System、Interview Buddy 等）多为
Streamlit/Flask + LLM 的简历问答或模拟面试 demo，结构雷同，不展开。

## 关键竞品：EasyWork-Interview

功能覆盖求职全链路：系统音频环回录制 → 本地转写（whisper.cpp/SenseVoice + VAD + 降噪）
→ 声纹说话人区分 → AI 复盘（五维评分）→ 题库归档 → 四种 AI 角色 → 投递看板。
技术栈：Tauri2(Rust) + React + Python FastAPI sidecar（ReAct + 工具调用 + 长期记忆）+ SQLite。

**结论：市场方向已被验证（有人做了完整实现），但其成熟度低（2 star、无 Release、
无测试与评测说明），且存在明显空白——这些空白就是本项目的机会。**

## 行业空白（所有同类开源项目的共同短板）

| 同类项目都有 | 同类项目几乎都没做 |
|---|---|
| 转写 → LLM 总结 → 导出 | 评测体系（无 ground truth、无量化指标） |
| 功能持续堆叠 | 防幻觉机制（点评不引用原文，无法验证） |
| prompt 一次性写完 | 失败案例驱动的 prompt 迭代记录 |
| 无真实用户验证 | 合规设计（录音知情同意、隐私声明） |

## 差异化策略：不拼功能广度，拼工程深度

1. **评测流水线（最硬的护城河）**：20+ 场真实面试 + 人工标注 ground truth
   → 问题召回率/点评命中率/幻觉率三指标 → LLM-as-Judge 回归。
   对应大厂 AI 团队 eval-driven development 的真实工作方式。
2. **引用溯源防幻觉**：每条点评强制摘录转写原话 + 简历原话（JSON Schema 校验）。
3. **合规设计**：录音知情同意提示、转写数据不落盘说明——产品成熟度的信号。
4. **复盘追问 Agent（面向 agent 岗的背书）**：报告生成后可追问，
   Agent 通过工具调用（定位转写原文时间点、检索简历章节）回答，
   每个回答必须带出处。设计原则：不是"什么都要 agent"，
   而是在"用户对报告有疑问、需要溯源"这个真实场景用 agent。
5. 不做：多 Agent 框架、向量数据库、模型微调（理由见 README 决策表）。

## 从竞品吸收进 roadmap（MVP 之后）

- 历史复盘对比 → 弱点趋势/进步曲线（留存与付费钩子）
- 五维能力评分雷达图（报告可视化）
- 本地转写降级选项（隐私敏感用户）

## 对本项目的启示

- 选题（面试复盘）已被验证有真实需求，无需换方向
- 竞争维度切换：别人卷功能，我们卷「可验证的效果」和「工程与产品判断」
- 面试叙事："我调研了 8 个同类开源项目，发现没有人做评测——
  而评测恰恰是大厂 AI 团队区分'能用'和'敢上线'的标准，所以我把两周时间
  花在了别人不愿意花的地方。"
