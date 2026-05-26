"""订阅源工厂 - 支持可插拔的订阅源类型"""
from datetime import datetime, timezone, timedelta
from typing import Callable

from .rss import parse_rss
from .atom import parse_atom
from .horizon import parse_horizon
from .article import Article


class SourceFactory:
    """订阅源工厂类"""

    _parsers: dict[str, Callable] = {
        "rss": parse_rss,
        "atom": parse_atom,
        "horizon": parse_horizon,
    }

    @classmethod
    def register(cls, source_type: str, parser: Callable) -> None:
        """注册新的订阅源类型"""
        cls._parsers[source_type] = parser

    @classmethod
    def parse(cls, source_type: str, url: str, name: str, days: int = 1) -> list[Article]:
        """解析指定类型的订阅源

        Args:
            source_type: 订阅源类型（rss/atom）
            url: 订阅源 URL
            name: 来源名称
            days: 抓取天数（默认1天）

        Returns:
            过滤后的 Article 列表
        """
        if source_type not in cls._parsers:
            raise ValueError(f"不支持的订阅源类型: {source_type}")

        articles = cls._parsers[source_type](url, name)
        filtered = filter_articles_by_days(articles, days, name)
        return filtered


def filter_articles_by_days(articles: list[Article], days: int, source_name: str) -> list[Article]:
    """按天数过滤文章（滚动窗口：当前时间往前推 N 天）

    Args:
        articles: 文章列表
        days: 天数
        source_name: 来源名称（用于日志）

    Returns:
        过滤后的文章列表
    """
    now = datetime.now(timezone.utc)

    # 滚动窗口：当前时间往前推 N 天
    window_end = now
    window_start = now - timedelta(days=days)

    filtered = []
    skipped_no_date = 0

    for article in articles:
        if article.pub_date is None:
            print(f"警告: {source_name} 有一篇文章缺少发布日期，已跳过: {article.title[:30]}...", file=__import__('sys').stderr)
            skipped_no_date += 1
            continue

        # 确保 pub_date 是 UTC
        if article.pub_date.tzinfo is None:
            pub_date_utc = article.pub_date.replace(tzinfo=timezone.utc)
        else:
            pub_date_utc = article.pub_date.astimezone(timezone.utc)

        if window_start <= pub_date_utc < window_end:
            filtered.append(article)

    if skipped_no_date > 0:
        print(f"警告: {source_name} 跳过了 {skipped_no_date} 篇缺少发布日期的文章", file=__import__('sys').stderr)

    return filtered


def fetch_all_sources(sources: list[dict[str, any]]) -> list[Article]:
    """从所有订阅源获取文章

    Args:
        sources: 订阅源配置列表 [{"type": "rss", "url": "...", "name": "...", "days": 1}]

    Returns:
        所有订阅源的文章列表
    """
    all_articles = []
    for source in sources:
        source_type = source.get("type", "rss")
        url = source.get("url", "")
        name = source.get("name", url)
        days = source.get("days", 1)  # 默认 1 天

        try:
            all_fetched = SourceFactory._parsers[source_type](url, name)
            articles = filter_articles_by_days(all_fetched, days, name)
            all_articles.extend(articles)

            # 打印抓取日志
            now = datetime.now(timezone.utc)
            window_start = now - timedelta(days=days)
            print(
                f"抓取完成: {name} | "
                f"时间范围: 最近 {days} 天 ({window_start.strftime('%Y-%m-%d %H:%M')} ~ {now.strftime('%Y-%m-%d %H:%M')} UTC) | "
                f"条数: {len(articles)}",
                file=__import__('sys').stderr
            )
        except Exception as e:
            print(f"获取订阅源失败 {name}: {e}", file=__import__('sys').stderr)

    return all_articles