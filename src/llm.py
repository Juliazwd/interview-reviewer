"""统一的 LLM 调用层：通义千问（OpenAI 兼容模式）。

所有 prompt 迭代都在各自的业务模块里，这一层只负责"怎么调"，不管"调什么"。
"""
import json
from openai import OpenAI

from .config import DASHSCOPE_API_KEY, QWEN_MODEL, DASHSCOPE_BASE_URL, ensure_api_key

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=ensure_api_key(),
            base_url=DASHSCOPE_BASE_URL,
        )
    return _client


def chat(
    messages: list[dict],
    json_mode: bool = False,
    temperature: float = 0.3,
    model: str | None = None,
) -> str:
    """调用通义千问。json_mode=True 时强制 JSON 输出（用于结构化点评）。"""
    kwargs = {"response_format": {"type": "json_object"}} if json_mode else {}
    resp = get_client().chat.completions.create(
        model=model or QWEN_MODEL,
        messages=messages,
        temperature=temperature,
        **kwargs,
    )
    return resp.choices[0].message.content


def chat_json(messages: list[dict], temperature: float = 0.3) -> dict:
    """chat() 的便捷封装：返回解析后的 dict，失败时抛出带原文的异常便于定位 bad case。"""
    raw = chat(messages, json_mode=True, temperature=temperature)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM 返回的不是合法 JSON，原始输出:\n{raw}") from e


def embed(texts: list[str]) -> list[list[float]]:
    """批量文本向量化（简历-问题对齐用）。"""
    resp = get_client().embeddings.create(
        model="text-embedding-v3",
        input=texts,
    )
    return [item.embedding for item in resp.data]
