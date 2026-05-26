## 1. 项目初始化

- [x] 1.1 使用 `pyproject.toml` 和 uv 初始化 Python 项目
- [x] 1.2 创建目录结构 (src/radar_mind/, prompts/, output/)
- [x] 1.3 添加依赖：httpx, feedparser, jinja2, openai

## 2. 配置模块

- [x] 2.1 实现 config.py：加载和解析 JSON 配置
- [x] 2.2 添加环境变量替换功能（`${VAR}` 语法）
- [x] 2.3 验证必填字段（llm, sources, categories, topics）
- [x] 2.4 创建带默认分类的示例 config.json

## 3. 订阅源解析

- [x] 3.1 实现 rss.py：解析 RSS 2.0 订阅源
- [x] 3.2 实现 atom.py：解析 ATOM 1.0 订阅源
- [x] 3.3 创建基础 Article 数据类
- [x] 3.4 添加订阅源工厂以支持可插拔的订阅源类型

## 4. 内容获取

- [x] 4.1 实现 fetcher.py：使用 httpx 的 HTTP 客户端
- [x] 4.2 每个订阅源添加超时和错误处理
- [x] 4.3 获取订阅源时的进度日志

## 5. AI 评分

- [x] 5.1 实现 scorer.py：LLM 客户端封装
- [x] 5.2 创建评分提示词模板 (prompts/scoring.j2)
- [x] 5.3 实现多分类评分循环
- [x] 5.4 添加分数解析和验证（1-10）
- [x] 5.5 评分时的进度日志

## 6. 主题过滤

- [x] 6.1 实现 filter.py：基于阈值的过滤
- [x] 6.2 根据配置的主题过滤文章
- [x] 6.3 日志：过滤前后数量

## 7. 日报生成

- [x] 7.1 实现 generator.py：使用结构化输入的 LLM 生成
- [x] 7.2 创建生成提示词模板 (prompts/generation.j2)
- [x] 7.3 处理无文章的情况

## 8. 输出模块

- [x] 8.1 实现 output.py：写入 output/ 目录的文件
- [x] 8.2 自动创建不存在的输出目录
- [x] 8.3 文件名格式：YYYY-MM-DD.md

## 9. CLI 入口

- [x] 9.1 实现 cli.py：参数解析（--config）
- [x] 9.2 编排完整流程：配置 → 获取 → 评分 → 过滤 → 生成 → 输出
- [x] 9.3 添加执行期间的日志输出
- [x] 9.4 错误处理和退出码

## 10. 默认提示词

- [x] 10.1 为每个标准分类创建默认评分提示词
- [x] 10.2 创建默认生成提示词模板