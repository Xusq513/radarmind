"""CLI 入口模块"""
import argparse
import sys
from datetime import date

from .config import Config
from .sources import fetch_all_sources, Article
from .scorer import Scorer, ScoringError
from .filter import filter_articles, ArticleWithScores
from .generator import Generator
from .output import write_report


def main():
    parser = argparse.ArgumentParser(description="RadarMind - 信息源 → AI评分 → 生成日报")
    parser.add_argument("--config", default="config.json", help="配置文件路径")
    args = parser.parse_args()

    try:
        print(f"加载配置: {args.config}", file=sys.stderr)
        config = Config(args.config)

        print(f"开始获取订阅源...", file=sys.stderr)
        articles = fetch_all_sources(config.sources)
        print(f"获取到 {len(articles)} 篇文章", file=sys.stderr)

        if not articles:
            print("未获取到任何文章", file=sys.stderr)
            sys.exit(1)

        scorer = Scorer(
            base_url=config.llm.get("base_url", "https://api.openai.com/v1"),
            api_key=config.llm.get("api_key", ""),
            model=config.llm.get("model", "gpt-4o"),
        )

        print(f"开始 AI 批量评分...", file=sys.stderr)
        scores_list = scorer.score_batch(articles, config.categories)

        articles_with_scores = [
            ArticleWithScores(article, scores)
            for article, scores in zip(articles, scores_list)
        ]
        print(f"评分完成", file=sys.stderr)

        print(f"开始过滤...", file=sys.stderr)
        filtered = filter_articles(articles_with_scores, config.topics, config.categories)
        print(f"过滤后保留 {len(filtered)} 篇文章", file=sys.stderr)

        generator = Generator(
            base_url=config.llm.get("base_url", "https://api.openai.com/v1"),
            api_key=config.llm.get("api_key", ""),
            model=config.llm.get("model", "gpt-4o"),
        )

        print(f"生成日报...", file=sys.stderr)
        report = generator.generate(
            articles=filtered,
            topics=config.topics,
            prompt_template=config.generation_prompt,
            report_date=date.today(),
        )

        output_path = write_report(report)
        print(f"日报已生成: {output_path}", file=sys.stderr)

    except ScoringError as e:
        print(f"评分失败: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()