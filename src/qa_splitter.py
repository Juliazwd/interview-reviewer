"""QA 切分：把 40-60 分钟的转写对话切成"一道面试题 + 对应回答"的单元。

为什么需要（两阶段流水线的第一段）：整场录音直接丢给 LLM 做复盘，
又贵又容易丢失细节。先切题，再逐题分析，最后汇总——长文本产品的标配架构。
"""
from dataclasses import dataclass

from .llm import chat_json

_SPLIT_SYSTEM = """你是一位资深面试官助手。输入是一段带说话人标签的面试转写文本
([interviewer] 为面试官，[candidate] 为候选人)。你的任务是把整场对话切成一道道独立的问答单元。

规则：
1. 面试官的连续发言（提问 + 追问前的过渡）属于同一道题的开头
2. 候选人回答后，如果面试官是针对同一问题追问（澄清、深挖），仍算同一道题
3. 面试官切换到新话题/新问题时，开启新的问答单元
4. 开场白（自我介绍环节）也算一道题；结尾的"你有什么想问的"也算
5. text 必须保留原文，不要改写、不要遗漏

输出 JSON：
{"qa_list": [{"topic": "题目的简短概括", "question": "面试官的完整提问(含追问)", "answer": "候选人的完整回答"}]}"""


@dataclass
class QAUnit:
    topic: str       # 题目概括，如 "简历项目深挖"
    question: str    # 面试官提问原文（含追问）
    answer: str      # 候选人回答原文
    aligned_sections: list = None  # 由 resume_aligner 填充：对齐到的简历章节


def split_qa(dialogue: str) -> list[QAUnit]:
    result = chat_json(
        [
            {"role": "system", "content": _SPLIT_SYSTEM},
            {"role": "user", "content": dialogue},
        ],
        temperature=0.1,
    )
    units = []
    for item in result.get("qa_list", []):
        units.append(
            QAUnit(
                topic=item.get("topic", ""),
                question=item.get("question", ""),
                answer=item.get("answer", ""),
            )
        )
    if not units:
        raise ValueError("QA 切分结果为空，请检查转写文本质量。")
    return units
