"""Generator 模块单元测试"""
import pytest
from datetime import date
from unittest.mock import MagicMock, patch

from radar_mind.generator import Generator
from radar_mind.filter import ArticleWithScores
from radar_mind.sources import Article


class TestRemoveThinkingTags:
    """测试 _remove_thinking_tags 方法"""

    def setup_method(self):
        """每个测试方法前创建 Generator 实例"""
        self.generator = Generator(
            base_url="https://api.test.com",
            api_key="test-key",
            model="test-model"
        )

    def test_remove_complete_thinking_tags(self):
        """测试去除完整的<think>...<eod_thinking>标签"""
        content = "<think>这个问题需要分析一下。<eod_thinking>这是正文内容。"
        result = self.generator._remove_thinking_tags(content)
        assert result == "这是正文内容。"

    def test_remove_truncated_thinking_tag(self):
        """测试去除只有开始标签没有结束标签的截断情况"""
        content = "<think>这个问题需要分析一下。这是正文内容。"
        result = self.generator._remove_thinking_tags(content)
        assert result == "这是正文内容。"

    def test_normal_thinking_tag(self):
        """测试去除只有开始标签没有结束标签的截断情况"""
        content = """<think>这个问题需要分析一下。这是正文内容。
                  dddd
                  </think>
                  你弟弟
                  """
        result = self.generator._remove_thinking_tags(content)
        assert result == "你弟弟。"

    def test_remove_multiple_complete_thinking_tags(self):
        """测试去除多个完整的thinking标签"""
        content = "<think>第一个分析。<eod_thinking>正文1<think>第二个分析。<eod_thinking>正文2"
        result = self.generator._remove_thinking_tags(content)
        assert result == "正文1正文2"

    def test_no_thinking_tags(self):
        """测试没有thinking标签的内容"""
        content = "这是纯正文内容，没有任何思考标签。"
        result = self.generator._remove_thinking_tags(content)
        assert result == "这是纯正文内容，没有任何思考标签。"

    def test_empty_content(self):
        """测试空内容"""
        content = ""
        result = self.generator._remove_thinking_tags(content)
        assert result == ""

    def test_only_thinking_tags(self):
        """测试只有thinking标签的内容"""
        content = "<think>只有思考标签，没有正文。<eod_thinking>"
        result = self.generator._remove_thinking_tags(content)
        assert result == ""

    def test_whitespace_handling(self):
        """测试空白字符处理"""
        content = "<think>思考内容。<eod_thinking>  \n\n  正文内容  "
        result = self.generator._remove_thinking_tags(content)
        assert result == "正文内容"

    def test_multiline_truncated_thinking(self):
        """测试多行截断的thinking标签"""
        content = """<think>第一行思考
第二行思考
第三行思考
正文内容"""
        result = self.generator._remove_thinking_tags(content)
        assert result == "正文内容"

    def test_mixed_complete_and_truncated(self):
        """测试混合完整和截断的thinking标签"""
        content = "<think>完整标签。<eod_thinking>正文1<think>截断标签正文2"
        result = self.generator._remove_thinking_tags(content)
        assert result == "正文1正文2"


class TestGenerator:
    """测试 Generator 主类 """

    def setup_method(self):
        """每个测试方法前创建 Generator 实例"""
        self.generator = Generator(
            base_url="https://api.test.com",
            api_key="test-key",
            model="test-model"
        )

    def test_remove_thinking_tags_integrated(self):
        """集成测试：验证 generate 方法正确去除 thinking 标签"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "<think>思考过程。<eod_thinking>实际输出"

        with patch.object(self.generator.client.chat, 'completions', 'create') as mock_create:
            mock_create.return_value = mock_response

            article = Article(title="Test", link="http://test.com", description="desc")
            article_with_scores = ArticleWithScores(article=article, scores={"cat1": 8})
            topics = ["topic1"]
            prompt_template = "生成{日期}的日报"

            result = self.generator.generate(
                articles=[article_with_scores],
                topics=topics,
                prompt_template=prompt_template,
                report_date=date(2024, 1, 15)
            )

            assert result == "实际输出"
            mock_create.assert_called_once()