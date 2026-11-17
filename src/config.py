"""全局配置：从 .env 读取 API Key 和模型名。"""
import os
from dotenv import load_dotenv

load_dotenv()

DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")

# 通义千问 LLM（OpenAI 兼容模式）
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen-plus")
# DashScope ASR 模型（带说话人分离）
ASR_MODEL = os.getenv("ASR_MODEL", "paraformer-v2")
# Embedding 模型（简历-问题对齐用）
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-v3")

DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"


def ensure_api_key() -> str:
    key = DASHSCOPE_API_KEY
    if not key:
        raise RuntimeError(
            "未配置 DASHSCOPE_API_KEY。请复制 .env.example 为 .env 并填入你的阿里云百炼 API Key。"
        )
    return key
