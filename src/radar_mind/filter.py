"""主题过滤模块 - 基于阈值过滤文章"""
from typing import Any

from .sources import Article


class ArticleWithScores:
    """带分数的文章"""
    def __init__(self, article: Article, scores: dict[str, int]):
        self.article = article
        self.scores = scores

    def meets_threshold(self, topic: str, threshold: int) -> bool:
        score = self.scores.get(topic, 0)
        return score >= threshold


def filter_articles(
    articles_with_scores: list[ArticleWithScores],
    topics: list[str],
    categories: dict[str, dict[str, Any]],
) -> list[ArticleWithScores]:
    """根据配置的主题和阈值过滤文章

    保留条件：任何一个 topic 的 score >= 其 threshold

    Args:
        articles_with_scores: 带分数的文章列表
        topics: 主题列表
        categories: 分类配置

    Returns:
        过滤后的文章列表
    """
    filtered = []
    for aws in articles_with_scores:
        if _should_keep(aws, topics, categories):
            filtered.append(aws)
    return filtered


def _should_keep(
    aws: ArticleWithScores,
    topics: list[str],
    categories: dict[str, dict[str, Any]],
) -> bool:
    """判断文章是否应该保留"""
    for topic in topics:
        threshold = categories.get(topic, {}).get("threshold", 6)
        if aws.meets_threshold(topic, threshold):
            return True
    return False