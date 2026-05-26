"""RSS 订阅源解析器"""
import feedparser
import re
from datetime import datetime, timezone, timedelta
from typing import Optional

from .article import Article


def parse_rss(url: str, source_name: str) -> list[Article]:
    """解析 RSS 2.0 订阅源

    Args:
        url: RSS 订阅源 URL
        source_name: 来源名称

    Returns:
        Article 列表
    """
    feed = feedparser.parse(url)
    articles = []

    for entry in feed.entries:
        pub_date = _parse_date(entry.get("published") or entry.get("updated"))
        article = Article(
            title=entry.get("title", ""),
            link=entry.get("link", ""),
            description=_clean_html(entry.get("summary") or entry.get("description", "")),
            pub_date=pub_date,
            source=source_name,
        )
        articles.append(article)

    return articles


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
        if '+00:00' in date_str:
            dt = datetime.fromisoformat(date_str.replace('+00:00', '+00:00'))
            return dt.replace(tzinfo=timezone.utc)
        elif date_str.endswith('Z'):
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.replace(tzinfo=timezone.utc)
        elif 'T' in date_str:
            return datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
    except Exception:
        pass

    # 尝试解析非标准格式，如 "2026-05-26 10:48:03 +0800"
    try:
        match = re.match(r"(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})\s*([+\-]\d{4})?", date_str)
        if match:
            date_part, time_part, tz_part = match.groups()
            dt = datetime.strptime(f"{date_part} {time_part}", "%Y-%m-%d %H:%M:%S")
            if tz_part:
                sign = 1 if tz_part[0] == '+' else -1
                hours, mins = int(tz_part[1:3]), int(tz_part[3:5])
                dt = dt.replace(tzinfo=timezone.utc)
                dt = dt - timedelta(hours=sign * hours, minutes=sign * mins)
            return dt
    except Exception:
        pass

    return None


def _clean_html(text: str) -> str:
    """清理 HTML 标签"""
    import re
    text = re.sub(r"<[^>]+>", "", text)
    text = text.strip()
    return text