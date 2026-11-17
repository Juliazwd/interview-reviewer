"""面试复盘助手 - 小窗口界面（Gradio）

运行: python app.py  然后浏览器打开提示的本地地址
"""
import gradio as gr

import src.config as config
from src.pipeline import run_pipeline

# ---------- 报告渲染 ----------

_VERDICT_CHIP = {
    "good": '<span style="background:#e7f6ec;color:#1a7f37;padding:2px 10px;border-radius:12px;font-size:13px;font-weight:600">✅ 答得好</span>',
    "ok": '<span style="background:#fff8e6;color:#9a6700;padding:2px 10px;border-radius:12px;font-size:13px;font-weight:600">🟡 一般</span>',
    "weak": '<span style="background:#fdeef0;color:#cf222e;padding:2px 10px;border-radius:12px;font-size:13px;font-weight:600">🔴 待改进</span>',
}


def render_report(result) -> str:
    """把 PipelineResult 渲染成界面上的 Markdown 报告。"""
    items = result.report.items
    n_good = sum(1 for i in items if i.verdict == "good")
    n_ok = sum(1 for i in items if i.verdict == "ok")
    n_weak = sum(1 for i in items if i.verdict == "weak")

    stats_row = (
        f"| 📊 共 {len(items)} 题 | ✅ 答得好 {n_good} | 🟡 一般 {n_ok} | 🔴 待改进 {n_weak} |"
        f" ⏱ {result.stats['elapsed_sec']}s |\n"
        f"|:---:|:---:|:---:|:---:|:---:|\n"
    )

    lines = [f"## 📋 总体复盘\n\n{result.report.summary}\n", "---\n", stats_row]

    for idx, item in enumerate(items, 1):
        chip = _VERDICT_CHIP.get(item.verdict, item.verdict)
        lines.append(f"### Q{idx} · {item.topic} &nbsp; {chip}\n")
        lines.append(f"**🎯 考察点**：{item.intent}\n")
        if item.evidence:
            lines.append(f"> 💬 **回答原话**：{item.evidence}\n")
        if item.resume_quote:
            lines.append(f"> 📄 **关联简历**：{item.resume_quote}\n")
        if item.issues:
            lines.append("**⚠️ 发现的问题**\n" + "\n".join(f"- {x}" for x in item.issues) + "\n")
        if item.suggestions:
            lines.append("**💡 改进建议**\n" + "\n".join(f"- {x}" for x in item.suggestions) + "\n")
        lines.append("\n---\n")

    lines.append("<sub>报告由 AI 生成，供复盘参考；你的材料仅用于本次分析，生成后即删除。</sub>")
    return "\n".join(lines)


def run(resume_pdf, audio_url, api_key_text, consent, progress=gr.Progress()):
    """Gradio 回调：串起整条流水线并返回可读报告 + docx 文件。"""
    if resume_pdf is None:
        raise gr.Error("请上传简历 PDF")
    if not audio_url.strip():
        raise gr.Error("请填写录音的公网 URL（DashScope 录音文件识别要求音频可公网访问）")
    if not consent:
        raise gr.Error("请先勾选知情同意与隐私声明，再生成报告")

    if api_key_text.strip():
        config.DASHSCOPE_API_KEY = api_key_text.strip()

    result = run_pipeline(resume_pdf.name, audio_url.strip())
    return render_report(result), result.docx_path


# ---------- 界面 ----------

_CUSTOM_CSS = """
#hero h1 { margin-bottom: 4px; }
#hero p { font-size: 15px; opacity: .85; }
footer { visibility: hidden; }
#footer-note { text-align: center; opacity: .6; font-size: 12px; }
"""

_PRIVACY_NOTE = (
    "> 🔒 **隐私承诺**：简历与录音仅用于生成本次复盘报告，经 API 处理后**立即删除**——"
    "不存储、不复用、不向任何第三方提供。生成前请确保已获得录音中所有对话者的知情同意。"
)

with gr.Blocks(
    title="面试复盘助手",
    css=_CUSTOM_CSS,
    theme=gr.themes.Soft(
        primary_hue="indigo",
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Noto Sans SC"), "system-ui", "sans-serif"],
        font_mono=[gr.themes.GoogleFont("IBM Plex Mono"), "monospace"],
    ),
) as demo:
    gr.Markdown(
        "# 🎙️ 面试复盘助手\n"
        "**问了什么 → 答得怎样 → 下次怎么改** · 上传简历和面试录音，几分钟拿到一份有据可查的复盘报告",
        elem_id="hero",
    )
    gr.Markdown(_PRIVACY_NOTE)

    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### ①️ 上传材料")
            resume_pdf = gr.File(label="简历 PDF", file_types=[".pdf"])
            audio_url = gr.Textbox(
                label="面试录音 URL（公网可访问，如 OSS 直链）",
                placeholder="https://your-bucket.oss-cn-hangzhou.aliyuncs.com/interview.mp3",
            )
            api_key_text = gr.Textbox(
                label="DashScope API Key（可选，留空使用服务端配置）",
                type="password",
                info="自备 Key = 数据只经过你自己的阿里云账号，多一层保障",
            )
            consent = gr.Checkbox(label="我已获得录音知情同意，并接受上述隐私声明")
            btn = gr.Button("🚀 生成复盘报告", variant="primary", size="lg")

        with gr.Column(scale=3):
            gr.Markdown("### ②️ 复盘报告")
            report_md = gr.Markdown(
                "报告将在这里生成——包含逐题考察点、回答原话摘录、问题诊断与改进建议。"
            )
            docx_out = gr.File(label="📥 下载 Word 版报告")

    gr.Markdown(
        "面试复盘助手 v0.1 · AI 生成内容仅供复盘参考 · 数据处理：阿里云百炼（处理后即删）",
        elem_id="footer-note",
    )

    btn.click(run, inputs=[resume_pdf, audio_url, api_key_text, consent], outputs=[report_md, docx_out])

if __name__ == "__main__":
    demo.launch(inbrowser=True)
