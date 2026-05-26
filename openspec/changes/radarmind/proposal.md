## 为什么需要这个项目

手动刷行业新闻耗时且低效。技术从业者需要每天快速了解AI、自动驾驶、半导体等领域动态，但筛选RSS源、抓取内容、判断相关性、生成简报这一链路完全依赖人工。需要一个本地CLI工具，把这套流程自动化，每天跑一次，5分钟看完前日动态。

## 要做什么

- **新增 RadarMind CLI 工具**：Python包，本地运行，无前端界面
- **多源订阅支持**：RSS、ATOM订阅源解析，预留自定义API/爬取扩展位
- **AI多分类评分**：每个分类配置独立提示词，LLM打1-10相关性分数
- **规则过滤**：根据配置的topics和阈值，保留高相关性新闻
- **LLM生成日报**：固定提示词模板，输入新闻标题/描述/链接，输出Markdown格式简报
- **本地文件输出**：配置JSON化，内容和配置都落磁盘，无数据库依赖

## 能力范围

### 新增能力

- **radarmind-core**：核心CLI入口，配置加载，命令行参数解析
- **feed-parsing**：RSS/ATOM订阅源解析，获取文章列表和基础信息
- **ai-scoring**：LLM多分类评分，每个分类独立prompt，输出1-10分数
- **topic-filtering**：基于配置的topics和阈值过滤新闻
- **report-generation**：LLM生成Markdown日报，整合筛选后的新闻
- **config-schema**：JSON配置结构定义（订阅源、分类、提示词、过滤规则）

### 修改的能力

无

## 影响范围

- 新增 `src/radar_mind/` Python包
- 新增 `prompts/` 目录存放提示词模板（Jinja2）
- 新增 `output/` 目录存放生成的日报
- 依赖：`httpx`（HTTP客户端）、`feedparser`（RSS解析）、`jinja2`（模板）、`openai` SDK
- 使用 `uv` 进行包管理和构建
- 支持任意OpenAI API协议兼容的LLM（通过base_url配置）