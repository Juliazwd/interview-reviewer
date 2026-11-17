"""LLM-as-Judge 自动评测。

流程：
1. 人工标注 ground truth（evaluation/data/ 下每场面试一份标注 JSON）
2. judge prompt 对照标注给 AI 复盘结果打分
3. 先验证 judge 与人工评分的一致性，再用于 prompt 迭代的回归测试
   （把人工从"每轮迭代重听 20 场录音"中解放出来）

待实现（D6-D11）。指标定义：
- 问题召回率：AI 切出的题目数与标注题目数的对齐覆盖度
- 点评命中率：AI 指出的弱点与标注弱点的重合度
- 幻觉率：evidence/resume_quote 无法在原文中找到的比例
"""
