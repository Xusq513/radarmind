"""HTTP 客户端模块 - 使用 httpx 获取订阅源内容"""
import httpx
from typing import Optional


class Fetcher:
    """HTTP 内容获取器"""

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self._client: Optional[httpx.Client] = None

    def __enter__(self):
        self._client = httpx.Client(timeout=self.timeout)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            self._client.close()

    def fetch(self, url: str) -> bytes:
        """获取 URL 内容

        Args:
            url: 目标 URL

        Returns:
            响应内容（bytes）

        Raises:
            httpx.HTTPError: 请求失败时
        """
        if not self._client:
            raise RuntimeError("Fetcher must be used as context manager")
        response = self._client.get(url)
        response.raise_for_status()
        return response.content