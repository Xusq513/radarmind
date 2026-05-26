"""Horizon 每日摘要专用解析器

Horizon 的 Atom feed 中每个 entry 包含当天全部内容，通过 <hr /> 分隔多篇文章。
每个 entry 需要被拆分为多个独立的 Article 对象。
"""
import re
from typing import Optional
from datetime import datetime

import feedparser

from .article import Article
from .atom import _parse_date


def parse_horizon(url: str, source_name: str) -> list[Article]:
    """解析 Horizon 每日摘要

    Args:
        url: Horizon Atom feed URL
        source_name: 来源名称

    Returns:
        Article 列表（每个 entry 中的每篇文章一个 Article）
    """
    feed = feedparser.parse(url)
    articles = []

    for entry in feed.entries:
        pub_date = _parse_date(entry.get("published") or entry.get("updated"))

        # 获取 content HTML
        content = _get_entry_content(entry)
        if not content:
            continue

        # 按 <hr /> 分割 segments
        segments = split_by_hr(content)
        if not segments:
            # fallback: 整个 entry 当一篇文章
            segments = [content]

        for segment in segments:
            article = _parse_segment(segment, pub_date, source_name)
            if article:
                articles.append(article)

    return articles


def split_by_hr(html_content: str) -> list[str]:
    """按 <hr /> 分隔符分割 HTML 内容

    Args:
        html_content: HTML 字符串

    Returns:
        分割后的片段列表
    """
    # 处理 <hr /> 和 <hr> 两种形式
    parts = re.split(r'<hr\s*/?>', html_content, flags=re.IGNORECASE)
    # 过滤空片段
    segments = [p.strip() for p in parts if p.strip()]
    return segments


def _get_entry_content(entry) -> str:
    """获取 entry 的 content HTML"""
    content = entry.get("content")
    if isinstance(content, list):
        return content[0].get("value", "")
    return content or ""


def _parse_segment(segment: str, pub_date: Optional[datetime], source: str) -> Optional[Article]:
    """解析单个文章 segment

    Args:
        segment: HTML 片段
        pub_date: 发布日期
        source: 来源名称

    Returns:
        Article 对象，解析失败返回 None
    """
    # 提取 link 和 title（从 h2 中）
    link = extract_link_from_h2(segment)
    title = extract_title_from_h2(segment)
    description = extract_body_from_segment(segment)

    if not link and not title:
        return None

    return Article(
        title=title or "无标题",
        link=link or "",
        description=description,
        pub_date=pub_date,
        source=source,
    )


def extract_link_from_h2(html: str) -> str:
    """从 h2 中提取第一个 anchor 的 href

    Args:
        html: HTML 片段

    Returns:
        链接 URL
    """
    # 查找 h2 标签内容
    h2_match = re.search(r'<h2[^>]*>(.*?)</h2>', html, re.DOTALL | re.IGNORECASE)
    if not h2_match:
        return ""

    h2_content = h2_match.group(1)
    # 提取第一个 <a href="..."> 的 href
    link_match = re.search(r'<a\s+[^>]*href=["\']([^"\']+)["\']', h2_content, re.IGNORECASE)
    if link_match:
        return link_match.group(1)
    return ""


def extract_title_from_h2(html: str) -> str:
    """从 h2 中提取标题文本，去掉评分后缀

    Args:
        html: HTML 片段

    Returns:
        标题文本
    """
    # 查找 h2 标签内容
    h2_match = re.search(r'<h2[^>]*>(.*?)</h2>', html, re.DOTALL | re.IGNORECASE)
    if not h2_match:
        return ""

    h2_content = h2_match.group(1)
    # 提取纯文本（去掉所有 HTML 标签）
    text = re.sub(r'<[^>]+>', '', h2_content)
    text = text.strip()

    # 去掉评分后缀，如 " ⭐️ 9.0/10" 或 " ⭐️ 8.0/10"
    text = re.sub(r'\s*⭐️\s*\d+\.\d+/10\s*$', '', text)
    text = text.strip()

    return text


def extract_body_from_segment(html: str) -> str:
    """从 segment 中提取正文（p 元素）

    Args:
        html: HTML 片段

    Returns:
        拼接的正文文本
    """
    # 找到 h2 之后的内容
    h2_match = re.search(r'</h2>(.*)', html, re.DOTALL | re.IGNORECASE)
    if not h2_match:
        return ""

    body_html = h2_match.group(1)

    # 移除 tags 部分（<p><strong>Tags</strong>...</p>）
    tags_match = re.search(r'<p><strong>Tags</strong>.*?</p>', body_html, re.DOTALL | re.IGNORECASE)
    if tags_match:
        body_html = body_html[:tags_match.start()]

    # 移除 details/references 部分
    details_match = re.search(r'<details>.*?</details>', body_html, re.DOTALL | re.IGNORECASE)
    if details_match:
        body_html = body_html[:details_match.start()]

    # 提取所有 p 元素文本
    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', body_html, re.DOTALL | re.IGNORECASE)
    texts = []
    for p in paragraphs:
        # 去掉 p 内的 HTML 标签
        text = re.sub(r'<[^>]+>', '', p)
        text = text.strip()
        if text:
            texts.append(text)

    return "\n\n".join(texts)