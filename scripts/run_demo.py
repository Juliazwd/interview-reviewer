"""端到端演示：示例简历 + 仿真转写文本 -> 复盘报告 Word。

用法: .\\.venv\\Scripts\\python.exe scripts\\run_demo.py
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")

from src.pipeline import run_pipeline_from_text

with open("demo/sample_transcript.txt", encoding="utf-8") as f:
    transcript_text = f.read()

result = run_pipeline_from_text(
    resume_path="demo/sample_resume.docx",
    transcript_text=transcript_text,
    output_dir="outputs",
)

print(f"统计: {result.stats}")
print(f"Word 报告: {result.docx_path}\n")
print("=" * 60)
print(f"总体复盘:\n{result.report.summary}\n")
for i, item in enumerate(result.report.items, 1):
    print(f"[{i}] {item.topic} -> {item.verdict}")
    print(f"    考察点: {item.intent[:50]}")
    for issue in item.issues[:3]:
        print(f"    · {issue[:60]}")
    print()
