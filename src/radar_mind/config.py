"""配置加载和解析模块"""
import json
import os
import re
from pathlib import Path
from typing import Any


class Config:
    """雷达新闻配置类"""

    REQUIRED_FIELDS = ["llm", "sources", "categories", "topics"]

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self._raw_config = self._load_json()
        self._config = self._substitute_env_vars(self._raw_config)
        self._validate()

    def _load_json(self) -> dict[str, Any]:
        """加载 JSON 配置文件"""
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _substitute_env_vars(self, obj: Any) -> Any:
        """递归替换配置值中的 ${VAR} 为环境变量"""
        if isinstance(obj, str):
            pattern = r"\$\{([^}]+)\}"
            matches = re.findall(pattern, obj)
            for var in matches:
                obj = obj.replace(f"${{{var}}}", os.environ.get(var, ""))
            return obj
        elif isinstance(obj, dict):
            return {k: self._substitute_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_env_vars(item) for item in obj]
        return obj

    def _validate(self) -> None:
        """验证必填字段"""
        missing = [f for f in self.REQUIRED_FIELDS if f not in self._config]
        if missing:
            raise ValueError(f"缺少必填字段: {', '.join(missing)}")

        if not self._config.get("llm", {}).get("api_key"):
            raise ValueError("llm.api_key 不能为空")

    @property
    def llm(self) -> dict[str, Any]:
        return self._config.get("llm", {})

    @property
    def sources(self) -> list[dict[str, Any]]:
        return self._config.get("sources", [])

    @property
    def categories(self) -> dict[str, dict[str, Any]]:
        return self._config.get("categories", {})

    @property
    def topics(self) -> list[str]:
        return self._config.get("topics", [])

    @property
    def generation_prompt(self) -> str:
        return self._config.get(
            "generation_prompt",
            "你是行业简报助手。请根据以下新闻列表，生成一份简短的Markdown格式日报。"
        )