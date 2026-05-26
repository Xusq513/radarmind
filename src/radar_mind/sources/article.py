"""订阅源解析模块"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Article:
    """新闻文章数据类"""
    title: str
    link: str
    description: str
    pub_date: Optional[datetime]
    source: str

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "link": self.link,
            "description": self.description,
            "pub_date": self.pub_date.isoformat() if self.pub_date else "",
            "source": self.source,
        }