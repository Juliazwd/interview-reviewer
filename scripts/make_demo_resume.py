"""生成演示用示例简历 demo/sample_resume.docx（docling 可直接解析 docx）。"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

from docx import Document

doc = Document()
doc.add_heading("李明", level=0)
doc.add_paragraph("XX大学 信息管理与信息系统专业 · 本科大三 · 2027届 | 求职意向：产品经理实习")

doc.add_heading("实习经历", level=1)
doc.add_paragraph("某互联网创业公司 · 用户增长实习生 · 2025.06 - 2025.09", style="List Bullet")
doc.add_paragraph(
    "负责策划并执行校园拉新活动，配合投放渠道完成获客目标；整理用户反馈并输出周报，"
    "协助产品经理完成需求池梳理。", style="List Bullet"
)

doc.add_heading("项目经历", level=1)
doc.add_paragraph("校园公众号运营项目 · 负责人 · 2024.09 - 2025.06", style="List Bullet")
doc.add_paragraph(
    "独立运营学院公众号，负责选题策划、内容撰写与数据分析，运营期间粉丝数从 800 增长到 3500，"
    "单篇最高阅读量 6000+。", style="List Bullet"
)
doc.add_paragraph("竞品分析报告：主流短视频App增长策略对比 · 2025.03", style="List Bullet")
doc.add_paragraph(
    "选取抖音、快手、小红书三款产品，从用户画像、内容分发机制、商业化路径三个维度"
    "输出 30 页竞品分析报告。", style="List Bullet"
)

doc.add_heading("技能", level=1)
doc.add_paragraph("SQL（基础查询与聚合）、Excel 数据透视表、Axure 原型、墨刀", style="List Bullet")
doc.add_paragraph("熟悉微信公众号后台、蝉妈妈等数据平台的使用", style="List Bullet")

doc.add_heading("其他", level=1)
doc.add_paragraph("英语 CET-6；长期撰写产品体验分析笔记，累计 20+ 篇", style="List Bullet")

doc.save("demo/sample_resume.docx")
print("OK: demo/sample_resume.docx")
