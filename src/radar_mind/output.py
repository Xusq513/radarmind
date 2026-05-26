"""输出模块 - 将日报写入文件"""
import os
from pathlib import Path
from datetime import date


def write_report(content: str, output_dir: str = "output", report_date: date = None) -> Path:
    """将日报内容写入文件

    Args:
        content: Markdown 格式的日报内容
        output_dir: 输出目录
        report_date: 报告日期，默认今天

    Returns:
        写入的文件路径
    """
    if not report_date:
        report_date = date.today()

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    filename = f"{report_date.isoformat()}.md"
    file_path = output_path / filename

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    return file_path