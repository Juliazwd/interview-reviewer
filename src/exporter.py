"""Word 报告导出：python-docx 生成三段式复盘报告（问了什么/答得怎样/下次怎么改）。"""
from pathlib import Path

from docx import Document
from docx.shared import Pt

from .reviewer import ReviewReport

_VERDICT_LABEL = {"good": "✅ 答得好", "ok": "⚠️ 一般", "weak": "❌ 待改进"}


def export_report(report: ReviewReport, output_path: str) -> str:
    doc = Document()
    doc.add_heading("面试复盘报告", level=0)

    doc.add_heading("总体复盘", level=1)
    doc.add_paragraph(report.summary or "（无）")

    for idx, item in enumerate(report.items, 1):
        doc.add_heading(f"第{idx}题：{item.topic}  [{_VERDICT_LABEL.get(item.verdict, item.verdict)}]", level=1)

        p = doc.add_paragraph()
        p.add_run("面试官提问：").bold = True
        p.add_run(item.question)

        p = doc.add_paragraph()
        p.add_run("考察点：").bold = True
        p.add_run(item.intent)

        if item.evidence:
            p = doc.add_paragraph()
            p.add_run("回答证据（原文摘录）：").bold = True
            run = p.add_run(item.evidence)
            run.italic = True

        if item.resume_quote:
            p = doc.add_paragraph()
            p.add_run("关联简历原话：").bold = True
            run = p.add_run(item.resume_quote)
            run.italic = True

        if item.issues:
            doc.add_paragraph("发现的问题：", style="List Bullet")
            for issue in item.issues:
                doc.add_paragraph(issue, style="List Bullet 2")

        if item.suggestions:
            doc.add_paragraph("改进建议：", style="List Number")
            for sug in item.suggestions:
                doc.add_paragraph(sug, style="List Number 2")

    # 全文默认字体微调，中文更易读
    for para in doc.paragraphs:
        for run in para.runs:
            run.font.size = Pt(11)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)
    return output_path
