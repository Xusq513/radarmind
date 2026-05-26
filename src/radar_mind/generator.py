"""日报生成模块 - 使用 LLM 生成 Markdown 格式日报"""
import sys
from datetime import date
from typing import Any

from openai import OpenAI

from .sources import Article
from .filter import ArticleWithScores


class Generator:
    """日报生成器"""

    def __init__(self, base_url: str, api_key: str, model: str):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    def generate(
        self,
        articles: list[ArticleWithScores],
        topics: list[str],
        prompt_template: str,
        report_date: date = None,
    ) -> str:
        """生成 Markdown 日报

        Args:
            articles: 过滤后的文章列表
            topics: 主题列表
            prompt_template: 生成提示词模板
            report_date: 报告日期，默认今天

        Returns:
            Markdown 格式的日报内容
        """
        if not report_date:
            report_date = date.today()

        if not articles:
            return f"# {report_date.isoformat()} 日报\n\n今日无相关更新。"

        articles_data = [
            {
                "title": aws.article.title,
                "link": aws.article.link,
                "description": aws.article.description[:100] if aws.article.description else "",
                "scores": aws.scores,
            }
            for aws in articles
        ]

        prompt = self._build_prompt(topics, articles_data, prompt_template, report_date)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional industry newsletter assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            extra_body={"reasoning_split": False},
        )
        content = response.choices[0].message.content
        return self._remove_thinking_tags(content)

    def _remove_thinking_tags(self, content: str) -> str:
        """去除思考过程标签及其内容"""
        import re
        # 1. 先去除完整的<think>...<eod_thinking>标签对
        cleaned = re.sub(r'<think>[\s\S]*?<eod_thinking>', '', content)
        # 2. 再去除完整的<think>...</think>标签对
        cleaned = re.sub(r'<think>[\s\S]*?</think>', '', cleaned)
        # 3. 再去除只有开始标签没有结束标签的（比如thinking被截断的情况）
        #    匹配开始标签到下一个换行符或字符串末尾
        cleaned = re.sub(r'<think>[^\n]*\n?', '', cleaned)
        return cleaned.strip()

    def _build_prompt(
        self,
        topics: list[str],
        articles: list[dict[str, Any]],
        prompt_template: str,
        report_date: date,
    ) -> str:
        """构建生成提示词"""
        # 只提供标题和链接，简化输入
        articles_text = "\n".join(
            f"- {a['title']} | {a['link']}"
            for i, a in enumerate(articles)
        )

        topics_str = "、".join(topics)
        date_str = report_date.strftime("%Y-%m-%d")

        # 替换 prompt 中的 {日期} 占位符
        prompt_template = prompt_template.replace("{日期}", date_str)

        return f"""{prompt_template}

关注主题：{topics_str}

新闻列表：
{articles_text}

日期：{date_str}

请直接输出简报内容，不要输出任何思考过程、分析或解释。"""