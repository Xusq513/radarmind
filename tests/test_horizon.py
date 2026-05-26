"""Horizon 解析器单元测试"""
import pytest
from datetime import datetime, timezone

from radar_mind.sources.horizon import (
    split_by_hr,
    extract_link_from_h2,
    extract_title_from_h2,
    extract_body_from_segment,
)


class TestSplitByHr:
    """测试 split_by_hr 函数"""

    def test_split_with_hr(self):
        """测试正常的 <hr /> 分割"""
        html = "<p>第一篇</p><hr /><p>第二篇</p><hr /><p>第三篇</p>"
        result = split_by_hr(html)
        assert len(result) == 3
        assert "第一篇" in result[0]
        assert "第二篇" in result[1]
        assert "第三篇" in result[2]

    def test_split_with_hr_no_space(self):
        """测试 <hr> 没有空格的情况"""
        html = "<p>第一篇</p><hr><p>第二篇</p>"
        result = split_by_hr(html)
        assert len(result) == 2

    def test_split_with_hr_uppercase(self):
        """测试 <HR /> 大写"""
        html = "<p>第一篇</p><HR /><p>第二篇</p>"
        result = split_by_hr(html)
        assert len(result) == 2

    def test_split_no_hr(self):
        """测试没有 <hr /> 的情况"""
        html = "<p>整篇内容</p><p>没有分隔符</p>"
        result = split_by_hr(html)
        assert len(result) == 1
        assert "整篇内容" in result[0]

    def test_split_empty_content(self):
        """测试空内容"""
        result = split_by_hr("")
        assert result == []

    def test_split_only_hr(self):
        """测试只有 <hr /> 的内容"""
        html = "<hr /><hr />"
        result = split_by_hr(html)
        assert result == []


class TestExtractTitleFromH2:
    """测试 extract_title_from_h2 函数"""

    def test_title_with_rating(self):
        """测试带评分后缀的标题"""
        html = '<h2><a href="https://example.com">Spyware Backdoor Found</a> ⭐️ 9.0/10</h2>'
        result = extract_title_from_h2(html)
        assert result == "Spyware Backdoor Found"

    def test_title_with_rating_8(self):
        """测试带 8.0/10 评分的标题"""
        html = '<h2><a href="https://example.com">Memory Cost Rising</a> ⭐️ 8.0/10</h2>'
        result = extract_title_from_h2(html)
        assert result == "Memory Cost Rising"

    def test_title_without_rating(self):
        """测试没有评分的标题"""
        html = "<h2>Simple Title</h2>"
        result = extract_title_from_h2(html)
        assert result == "Simple Title"

    def test_title_with_real_format(self):
        """测试真实 Horizon 格式：标题后只有评分后缀"""
        html = '<h2><a href="https://example.com">Article Title</a> ⭐️ 9.0/10</h2>'
        result = extract_title_from_h2(html)
        assert result == "Article Title"

    def test_no_h2(self):
        """测试没有 h2 标签"""
        html = "<p>No h2 here</p>"
        result = extract_title_from_h2(html)
        assert result == ""


class TestExtractLinkFromH2:
    """测试 extract_link_from_h2 函数"""

    def test_link_in_first_anchor(self):
        """测试第一个 anchor 的链接"""
        html = '<h2><a href="https://x.com/status/123">Title</a> ⭐️ 9.0/10</h2>'
        result = extract_link_from_h2(html)
        assert result == "https://x.com/status/123"

    def test_link_multiple_anchors(self):
        """测试 h2 内有多个 anchor，只取第一个"""
        html = '<h2><a href="https://first.com">Title</a><a href="https://second.com">Discussion</a></h2>'
        result = extract_link_from_h2(html)
        assert result == "https://first.com"

    def test_link_no_href(self):
        """测试 anchor 没有 href"""
        html = "<h2><a>No href</a></h2>"
        result = extract_link_from_h2(html)
        assert result == ""

    def test_no_h2(self):
        """测试没有 h2 标签"""
        html = "<p>No h2 here</p>"
        result = extract_link_from_h2(html)
        assert result == ""


class TestExtractBodyFromSegment:
    """测试 extract_body_from_segment 函数"""

    def test_extract_basic_paragraphs(self):
        """测试提取基本段落"""
        html = """
        <h2><a href="https://example.com">Title</a> ⭐️ 9.0/10</h2>
        <p>First paragraph content.</p>
        <p>Second paragraph content.</p>
        """
        result = extract_body_from_segment(html)
        assert "First paragraph content" in result
        assert "Second paragraph content" in result

    def test_exclude_tags_section(self):
        """测试排除 Tags 部分"""
        html = """
        <h2><a href="https://example.com">Title</a> ⭐️ 9.0/10</h2>
        <p>Main content.</p>
        <p><strong>Tags</strong>: #tag1, #tag2</p>
        """
        result = extract_body_from_segment(html)
        assert "Main content" in result
        assert "Tags" not in result

    def test_exclude_details(self):
        """测试排除 Details/References 部分"""
        html = """
        <h2><a href="https://example.com">Title</a> ⭐️ 9.0/10</h2>
        <p>Main content.</p>
        <details><summary>References</summary><ul><li>Link</li></ul></details>
        """
        result = extract_body_from_segment(html)
        assert "Main content" in result
        assert "References" not in result

    def test_no_h2(self):
        """测试没有 h2 的情况"""
        html = "<p>Just paragraph</p>"
        result = extract_body_from_segment(html)
        assert result == ""