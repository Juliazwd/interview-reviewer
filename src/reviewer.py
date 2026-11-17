"""逐题点评 + 总体复盘：本产品的核心 prompt 模块（评测迭代的主要对象）。

设计决策：
- 逐题点评而非一次性输出全文——这是两阶段流水线的第二段
- 强制 JSON Schema 输出（question/evidence/issues/suggestions 四元组），
  因为报告要导出 Word、要算评测指标，自由文本无法机器校验
- 点评必须引用转写原文（evidence）和简历原文（resume_quote），防幻觉
"""
from dataclasses import dataclass, field

from .llm import chat_json

_REVIEW_SYSTEM = """你是一位严格但建设性的面试复盘教练。输入是一道面试问答单元
（面试官提问 + 候选人回答），以及与该问题最相关的候选人简历章节。

你的任务：点评这道题答得如何，并给出可操作的改进建议。

规则（每条都是为了防幻觉、保证可验证）：
1. evidence: 必须摘录候选人回答中的原话作为证据，不得编造
2. resume_quote: 如果点评涉及简历内容，必须引用简历章节中的原话；与简历无关时留空字符串
3. issues: 每个问题都要具体可改进（如"缺少量化数据"、"归因不清晰"），
   不要输出"回答不够好"这类空泛评价
4. suggestions: 对应每个 issue 给出具体怎么改，最好附上示例表述
5. verdict 只能是: good / ok / weak

输出 JSON：
{
  "verdict": "good|ok|weak",
  "intent": "面试官问这个问题的考察点",
  "evidence": "候选人回答原话摘录",
  "resume_quote": "简历原话摘录或空串",
  "issues": ["具体问题1", "具体问题2"],
  "suggestions": ["对应改进1", "对应改进2"]
}"""


@dataclass
class ReviewItem:
    topic: str
    question: str
    answer: str
    verdict: str
    intent: str
    evidence: str
    resume_quote: str
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


@dataclass
class ReviewReport:
    items: list[ReviewItem]
    summary: str = ""  # 整场复盘总结


def review_one(qa_unit, aligned_sections: list[str]) -> ReviewItem:
    """点评一道问答单元。aligned_sections 为对齐到的简历章节文本。"""
    resume_ctx = "\n---\n".join(aligned_sections) if aligned_sections else "（无相关简历内容）"
    result = chat_json(
        [
            {"role": "system", "content": _REVIEW_SYSTEM},
            {
                "role": "user",
                "content": f"【面试官提问】\n{qa_unit.question}\n\n【候选人回答】\n{qa_unit.answer}\n\n【相关简历章节】\n{resume_ctx}",
            },
        ]
    )
    return ReviewItem(
        topic=qa_unit.topic,
        question=qa_unit.question,
        answer=qa_unit.answer,
        verdict=result.get("verdict", "ok"),
        intent=result.get("intent", ""),
        evidence=result.get("evidence", ""),
        resume_quote=result.get("resume_quote", ""),
        issues=result.get("issues", []),
        suggestions=result.get("suggestions", []),
    )


_SUMMARY_SYSTEM = """你是面试复盘教练。输入是整场面试的逐题点评结果（JSON）。
请输出一段 300 字以内的总体复盘：本场面试的强项、最需要优先改进的 2-3 件事、
以及一个总体评分(1-10)。直接输出文本，不要 JSON。"""


def summarize(items: list[ReviewItem]) -> str:
    payload = "\n".join(
        f"题目:{i.topic} | 评价:{i.verdict} | 问题:{';'.join(i.issues)}" for i in items
    )
    from .llm import chat
    return chat(
        [
            {"role": "system", "content": _SUMMARY_SYSTEM},
            {"role": "user", "content": payload},
        ]
    )
