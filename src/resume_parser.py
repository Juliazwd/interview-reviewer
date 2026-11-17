"""简历解析：docling 结构化解析 PDF，保留章节结构。

为什么不用普通 PDF 抽文本：复盘需要知道面试官深挖的是简历里
"哪一段经历"，纯文本流没有段落边界，无法做简历-问题对齐。
"""
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ResumeSection:
    title: str    # 章节标题，如 "项目经历" / "实习经历"
    content: str  # 该章节正文


def parse_resume(pdf_path: str) -> list[ResumeSection]:
    """解析简历 PDF -> 按标题切分的章节列表。"""
    from docling.document_converter import DocumentConverter

    result = DocumentConverter().convert(Path(pdf_path))
    md = result.document.export_to_markdown()

    sections: list[ResumeSection] = []
    title, buf = "基本信息", []

    for line in md.splitlines():
        if line.startswith("#"):
            if any(s.strip() for s in buf):
                sections.append(ResumeSection(title, "\n".join(buf).strip()))
            title, buf = line.lstrip("# ").strip(), []
        else:
            buf.append(line)

    if any(s.strip() for s in buf):
        sections.append(ResumeSection(title, "\n".join(buf).strip()))

    sections = [s for s in sections if s.content]
    if not sections:
        raise ValueError("简历解析结果为空，请确认上传的是文本型 PDF（非扫描件）。")
    return sections
