"""AI 评分模块 - 批量评分优化"""
import json
import re
import sys
from typing import Any

from openai import OpenAI

from .sources import Article


class ScoringError(Exception):
    """评分异常基类"""
    pass


class Scorer:
    """AI 评分器 - 批量评分版本"""

    MAX_RETRIES = 3
    BATCH_CHAR_LIMIT = 1000  # 每批标题总字符数限制

    def __init__(self, base_url: str, api_key: str, model: str):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    def score_batch(
        self, articles: list[Article], categories: dict[str, dict[str, Any]]
    ) -> list[dict[str, int]]:
        """批量评分：所有文章按批次评分

        Args:
            articles: 文章列表
            categories: 分类配置 {分类名: {threshold, prompt}}

        Returns:
            评分结果列表，每个元素对应一篇文章的分数 {分类: 分数}
        """
        if not articles:
            return []

        categories_list = list(categories.keys())
        batches = self._split_batches(articles)
        all_scores = []

        for batch_idx, batch in enumerate(batches):
            batch_scores = self._score_single_batch_with_retry(
                batch, categories_list, batch_idx
            )
            all_scores.extend(batch_scores)

        return all_scores

    def _split_batches(self, articles: list[Article]) -> list[list[Article]]:
        """按字符数限制拆分批次"""
        batches = []
        current_batch = []
        current_chars = 0

        for article in articles:
            title_chars = len(article.title)
            if current_chars + title_chars > self.BATCH_CHAR_LIMIT and current_batch:
                batches.append(current_batch)
                current_batch = []
                current_chars = 0
            current_batch.append(article)
            current_chars += title_chars

        if current_batch:
            batches.append(current_batch)

        return batches

    def _score_single_batch_with_retry(
        self, batch: list[Article], categories_list: list[str], batch_idx: int
    ) -> list[dict[str, int]]:
        """单批次评分，支持重试"""
        prompt = self._build_batch_prompt(batch, categories_list)

        for attempt in range(self.MAX_RETRIES):
            try:
                result = self._call_llm(prompt)
                return self._parse_batch_result(result, categories_list, len(batch))
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(
                    f"批次 {batch_idx + 1} 第 {attempt + 1} 次失败，LLM 返回:\n{result}",
                    file=sys.stderr
                )
                if attempt == self.MAX_RETRIES - 1:
                    raise ScoringError(
                        f"批次 {batch_idx + 1} 评分失败，已重试 {self.MAX_RETRIES} 次: {e}"
                    )
                # 重试

        raise ScoringError("不应到达此处")

    def _call_llm(self, prompt: str) -> str:
        """调用 LLM 获取响应"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个专业的新闻评分助手。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            extra_body={"reasoning_split": False},
        )
        content = response.choices[0].message.content
        return self._remove_thinking_tags(content)

    def _remove_thinking_tags(self, content: str) -> str:
        """去除思考过程标签及其内容"""
        import re
        cleaned = re.sub(r'<think>[\s\S]*?', '', content)
        return cleaned.strip()

    def _build_batch_prompt(self, batch: list[Article], categories_list: list[str]) -> str:
        """构建批量评分 prompt"""
        news_list = "\n".join(
            f"{i+1}. {article.title}"
            for i, article in enumerate(batch)
        )

        categories_text = "\n".join(f"- {cat}" for cat in categories_list)

        return f"""请分析以下新闻列表，判断每条新闻与各分类的相关度。

新闻列表:
{news_list}

分类说明:
{categories_text}

请只返回 JSON 数组格式，不要包含其他文字。返回格式：
[{{"分类1": 分数, "分类2": 分数, ...}}, ...]

分数范围 1-10，1表示完全无关，10表示高度相关。
JSON 数组中每个元素对应一条新闻，按顺序排列。"""

    def _parse_batch_result(
        self, content: str, categories_list: list[str], expected_count: int
    ) -> list[dict[str, int]]:
        """解析批量评分结果"""
        content = content.strip()

        # 提取 JSON 部分
        if content.startswith("```"):
            lines = content.split("\n")
            json_lines = []
            in_json = False
            for line in lines:
                if line.startswith("```"):
                    in_json = not in_json
                    continue
                if in_json:
                    json_lines.append(line)
            content = "\n".join(json_lines)
        elif "[" in content:
            start = content.find("[")
            end = content.rfind("]") + 1
            content = content[start:end]

        data = json.loads(content)

        if not isinstance(data, list):
            raise ValueError(f"期望 JSON 数组，得到 {type(data)}")

        if len(data) != expected_count:
            raise ValueError(f"期望 {expected_count} 个评分结果，得到 {len(data)}")

        results = []
        for item in data:
            if not isinstance(item, dict):
                raise ValueError(f"期望 JSON 对象，得到 {type(item)}")
            scores = {}
            for cat in categories_list:
                scores[cat] = self._parse_score(item.get(cat, 0))
            results.append(scores)

        return results

    def _parse_score(self, value: Any) -> int:
        """解析单个分数"""
        if isinstance(value, int):
            return max(1, min(10, value))
        if isinstance(value, float):
            return max(1, min(10, int(value)))
        if isinstance(value, str):
            numbers = re.findall(r"\d+", value)
            if numbers:
                return max(1, min(10, int(numbers[0])))
        return 0