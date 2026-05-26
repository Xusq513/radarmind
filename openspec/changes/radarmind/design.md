## 背景

RadarMind 是一个本地 CLI 工具，每天手动运行一次，从订阅源抓取新闻，AI 评分后过滤，最终生成 Markdown 日报。

**当前状态**：全新项目，无现有代码。

**约束条件**：
- Python 技术栈，使用 uv 管理依赖
- 无前端，配置通过 JSON 文件
- 无数据库，所有内容落磁盘
- 支持任意 OpenAI API 兼容模型（通过 base_url 配置）
- 每天处理几百条新闻，支持手动触发

**利益相关方**：个人技术从业者，需要快速了解特定行业动态

## 目标 / 非目标

**目标：**
- 从 RSS/ATOM 订阅源获取文章列表和基础信息
- 对每条新闻进行多分类评分（AI相关度1-10）
- 根据配置的 topics 和阈值过滤新闻
- 使用 LLM 生成 Markdown 格式日报
- 配置灵活可扩展，支持多分类独立提示词

**非目标：**
- 定时自动调度（用户手动触发）
- 持久化存储（每次运行独立）
- 前端界面
- 复杂去重（生成日报时自然去重）
- 网页爬取（预留扩展位，初期只支持RSS/ATOM）

## 关键设计决策

### 1. 项目结构

```
radarmind/
├── config.json              # 全部配置
├── prompts/                  # 提示词模板
│   ├── scoring.j2            # AI评分提示词
│   └── generation.j2         # 日报生成提示词
├── src/radar_mind/           # Python源码
│   ├── __init__.py
│   ├── cli.py               # CLI入口
│   ├── config.py            # 配置加载
│   ├── sources/             # 订阅源解析
│   │   ├── rss.py
│   │   └── atom.py
│   ├── fetcher.py           # 内容抓取
│   ├── scorer.py            # AI评分
│   ├── filter.py            # 规则过滤
│   ├── generator.py         # 日报生成
│   └── output.py            # 文件输出
├── output/                  # 生成的日报
├── requirements.txt
└── pyproject.toml
```

**为什么**：模块化拆分，每个 capability 独立文件，便于后续扩展和维护。

### 2. 配置结构

```json
{
  "llm": {
    "base_url": "https://api.openai.com/v1",
    "api_key": "${OPENAI_API_KEY}",
    "model": "gpt-4o"
  },
  "sources": [
    { "type": "rss", "url": "...", "name": "36kr" },
    { "type": "atom", "url": "...", "name": "TechCrunch" }
  ],
  "categories": {
    "AI": { "threshold": 6 },
    "自动驾驶": { "threshold": 6 },
    "新能源": { "threshold": 6 },
    "半导体": { "threshold": 6 },
    "软件": { "threshold": 6 },
    "政策": { "threshold": 6 }
  },
  "topics": ["AI", "自动驾驶"],
  "generation_prompt": "你是行业简报助手..."
}
```

**为什么**：JSON 配置直观，categories 和 topics 分离，阈值独立配置。

### 3. AI 评分流程

```
对每条新闻：
  遍历 categories 中的每个分类
  → 构建 prompt（新闻标题+描述+链接+分类提示词）
  → 调用 LLM，解析返回的分数（1-10）
  → 记录 score_map（分类名: 分数）
```

**为什么**：串行评分简单可靠，N篇文章 × M个分类 = N×M次调用，需要考虑批处理优化。

### 4. 过滤逻辑

```python
# 保留条件：任何一个 topic 的 score >= 其 threshold
any(score[topic] >= categories[topic]["threshold"] for topic in topics)
```

**为什么**：OR 逻辑确保不遗漏，用户配置灵活。阈值在 categories 中定义。

### 5. 日报生成

```python
# 输入给 LLM：
{
  "date": "2026-05-26",
  "topics": ["AI", "自动驾驶"],
  "news": [
    {"title": "...", "description": "...", "link": "...", "scores": {...}},
    ...
  ],
  "prompt_template": "你是行业简报助手..."
}
```

**为什么**：结构化输入 + 模板 prompt，生成内容稳定可预测。

### 6. 依赖选择

- `httpx`：异步 HTTP 客户端（支持连接池、超时）
- `feedparser`：RSS/ATOM 解析
- `jinja2`：提示词模板渲染
- `openai` SDK：LLM 调用（base_url 可配置）

**为什么**：轻量级、无复杂依赖，满足当前需求。

## 风险与权衡

| 风险 | 缓解措施 |
|------|----------|
| LLM 调用量大（每篇评多个分类） | 串行调用，简单可靠；后续可加批处理 |
| LLM 返回格式不稳定（分数解析失败） | prompt 设计明确要求返回纯数字，加错误处理 |
| RSS 源结构不一致导致解析失败 | 捕获异常，单个源失败不影响其他源 |
| API Key 暴露在配置文件中 | 支持环境变量引用 `${VAR}` 形式 |

## 待解决问题

1. **评分 prompt 默认值**：需要为每个分类提供默认提示词，用户可覆盖
2. **生成日报去重**：提到"生成时自然去重"，具体算法待定（按标题相似度？）
3. **错误恢复**：LLM 调用失败后的重试策略
4. **日志输出**：CLI 运行时的进度展示（rich/typer 增强体验）