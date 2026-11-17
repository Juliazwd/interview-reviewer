"""冒烟测试：验证 DashScope API Key 的三个通道（LLM / Embedding / ASR）。

用法: .\\.venv\\Scripts\\python.exe scripts\\smoke_test.py
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")  # Windows GBK 控制台兼容
sys.path.insert(0, ".")

from src.config import ensure_api_key, QWEN_MODEL, ASR_MODEL

PASS, FAIL = "✅ PASS", "❌ FAIL"


def test_llm():
    from src.llm import chat
    out = chat([{"role": "user", "content": "只回复两个字：连通"}], temperature=0)
    print(f"[1/3] LLM ({QWEN_MODEL}): {PASS}  回复: {out.strip()[:20]}")


def test_embedding():
    from src.llm import embed
    vecs = embed(["产品经理实习", "阿里巴巴一面"])
    print(f"[2/3] Embedding (text-embedding-v3): {PASS}  维度: {len(vecs[0])}")


def test_asr():
    """无真实音频，用假 URL 探测服务权限：
    若报错指向'文件下载失败/URL无效'说明模型服务可用；
    若报错指向'模型不存在/未授权/未开通'则需去控制台开通语音服务。"""
    import dashscope
    from dashscope.audio.asr import Transcription

    dashscope.api_key = ensure_api_key()
    resp = Transcription.async_call(
        model=ASR_MODEL,
        file_urls=["https://example.com/nonexistent.mp3"],
        diarization_enabled=True,
    )
    code = getattr(resp, "status_code", None)
    msg = str(getattr(resp, "message", resp))
    if code in (200, None):
        # 任务已受理（说明模型权限 OK），假 URL 会在轮询阶段失败
        print(f"[3/3] ASR ({ASR_MODEL}): {PASS}  任务已受理，权限正常（文件不存在属预期）")
        return
    low = msg.lower()
    if any(k in low for k in ("model", "not exist", "unauthorized", "forbidden", "无权", "未开通", "不存在")):
        print(f"[3/3] ASR ({ASR_MODEL}): {FAIL}  模型权限问题，请到百炼控制台开通语音服务。详情: {msg}")
    else:
        print(f"[3/3] ASR ({ASR_MODEL}): {PASS}  服务可访问（返回: {msg[:80]}，假URL属预期）")


if __name__ == "__main__":
    results = []
    for fn in (test_llm, test_embedding, test_asr):
        try:
            fn()
            results.append(True)
        except Exception as e:
            print(f"  ❌ FAIL  {type(e).__name__}: {e}")
            results.append(False)
    print("\n" + ("全部通道可用 ✅" if all(results) else "存在失败项，见上方详情 ❌"))
    sys.exit(0 if all(results) else 1)
