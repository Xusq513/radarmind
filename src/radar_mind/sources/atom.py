"""ATOM 订阅源解析器"""
import feedparser
from datetime import datetime, timezone
from typing import Optional

from .article import Article


def parse_atom(url: str, source_name: str) -> list[Article]:
    """解析 ATOM 1.0 订阅源

    Args:
        url: ATOM 订阅源 URL
        source_name: 来源名称

    Returns:
        Article 列表
    """
    feed = feedparser.parse(url)
    articles = []

    for entry in feed.entries:
        link = _get_atom_link(entry)
        pub_date = _parse_date(entry.get("published") or entry.get("updated"))
        article = Article(
            title=entry.get("title", ""),
            link=link,
            description=_clean_html(entry.get("summary") or entry.get("content", "")),
            pub_date=pub_date,
            source=source_name,
        )
        articles.append(article)

    return articles


def _get_atom_link(entry) -> str:
    """获取 ATOM 条目的链接，优先选择 rel=alternate"""
    links = entry.get("links", [])
    for link in links:
        if link.get("rel") == "alternate":
            return link.get("href", "")
    if links:
        return links[0].get("href", "")
    return entry.get("link", "")


def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """解析日期字符串"""
    if not date_str:
        return None
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_str)
    except Exception:
        pass

    # 尝试解析 ISO 8601 格式，如 "2026-05-26T00:00:00+00:00"
    try:
        from datetime import datetime
        # 移除 timezone info 然后手动处理
        if '+00:00' in date_str:
            # UTC 时间
            dt = datetime.fromisoformat(date_str.replace('+00:00', '+00:00'))
            return dt.replace(tzinfo=timezone.utc)
        elif date_str.endswith('Z'):
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.replace(tzinfo=timezone.utc)
        else:
            # 其他 ISO 格式
            return datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
    except Exception:
        pass

    return None


def _clean_html(text: str) -> str:
    """清理 HTML 标签"""
    import re
    text = re.sub(r"<[^>]+>", "", text)
    text = text.strip()
    return text