"""主流水线：简历 PDF + 录音 -> 结构化复盘报告 -> Word 导出。

架构（README 里放这张图）：
  简历 PDF --docling--> 结构化章节 --embedding--> 简历段落索引
                                                    | (对齐)
  录音 --ASR(说话人分离)--> 转写 --QA切分--> 逐题点评 --汇总--> Word 报告
"""
import re
import time
from dataclasses import dataclass
from pathlib import Path

from .qa_splitter import split_qa
from .resume_aligner import align_question, build_section_index
from .resume_parser import parse_resume
from .reviewer import ReviewReport, review_one, summarize
from .exporter import export_report
from .transcriber import transcribe


@dataclass
class PipelineResult:
    docx_path: str
    report: ReviewReport
    stats: dict  # 题目数、耗时等，供评测和展示用


def _safe_filename(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', "_", name) or "report"


def run_pipeline(
    resume_pdf_path: str,
    audio_url: str,
    output_dir: str = "outputs",
) -> PipelineResult:
    """执行完整流水线。audio_url 必须是公网可访问的录音地址。"""
    t0 = time.time()

    # 1. 简历解析（docling）
    sections = parse_resume(resume_pdf_path)

    # 2. 语音转写（ASR + 说话人分离）
    transcript = transcribe(audio_url)

    return _run_core(sections, transcript.dialogue, output_dir)


def run_pipeline_from_text(
    resume_path: str,
    transcript_text: str,
    output_dir: str = "outputs",
) -> PipelineResult:
    """演示/评测专用：跳过 ASR，直接从转写文本开始。

    评测时用固定文本可以排除 ASR 变量、节省转写额度，
    让指标只反映"切题-对齐-点评"链路的质量。
    """
    sections = parse_resume(resume_path)
    return _run_core(sections, transcript_text, output_dir)


def _run_core(sections, dialogue: str, output_dir: str) -> PipelineResult:
    t0 = time.time()

    # 3. QA 切分（两阶段流水线第一段）
    qa_units = split_qa(dialogue)

    # 4. 简历-问题对齐（轻量 RAG，一次向量化，逐题检索）
    texts, vectors = build_section_index(sections)

    # 5. 逐题点评（两阶段流水线第二段）
    items = []
    for unit in qa_units:
        aligned = align_question(unit.question, texts, vectors)
        items.append(review_one(unit, aligned))

    # 6. 汇总
    report = ReviewReport(items=items, summary=summarize(items))

    # 7. 导出 Word
    ts = time.strftime("%Y%m%d_%H%M%S")
    docx_path = str(Path(output_dir) / f"复盘报告_{ts}.docx")
    export_report(report, docx_path)

    stats = {
        "resume_sections": len(sections),
        "qa_count": len(qa_units),
        "elapsed_sec": round(time.time() - t0, 1),
    }
    return PipelineResult(docx_path=docx_path, report=report, stats=stats)
