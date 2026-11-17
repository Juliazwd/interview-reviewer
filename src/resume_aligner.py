"""简历-问题对齐（轻量 RAG）。

为什么做这一层（真实 grounding 需求）：
AI 点评时必须引用"你简历里这段经历的原话"才有说服力，同时把
幻觉率压下来——点评引用要有出处，而不是凭空编造。
一份简历只有十几个章节，直接内存算余弦相似度即可，
不需要引入向量数据库（过度设计）。
"""
import numpy as np

from .llm import embed


def build_section_index(sections: list) -> tuple[list[str], np.ndarray]:
    """把简历章节向量化，返回 (章节文本列表, 向量矩阵)。"""
    texts = [f"{s.title}\n{s.content}" for s in sections]
    vectors = np.array(embed(texts))
    return texts, vectors


def align_question(question: str, texts: list[str], vectors: np.ndarray, top_k: int = 2) -> list[str]:
    """把一道面试题对齐到最相关的简历章节，返回 top_k 章节文本。"""
    q_vec = np.array(embed([question])[0])
    sims = vectors @ q_vec / (np.linalg.norm(vectors, axis=1) * np.linalg.norm(q_vec) + 1e-8)
    top_idx = np.argsort(sims)[::-1][:top_k]
    return [texts[i] for i in top_idx]
