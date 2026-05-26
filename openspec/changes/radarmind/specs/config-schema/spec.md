## 新增需求

### 需求：LLM 配置
系统 SHALL 支持 LLM 配置，包含 base_url、api_key 和 model 名称。

#### 场景：完整 LLM 配置
- **WHEN** 配置包含 `"llm": {"base_url": "https://api.openai.com/v1", "api_key": "${OPENAI_API_KEY}", "model": "gpt-4o"}`
- **THEN** 系统使用这些值进行所有 LLM 调用

### 需求：订阅源配置
系统 SHALL 支持多个订阅源条目，每个包含 type、url 和 name 字段。

#### 场景：RSS 订阅源配置
- **WHEN** 配置包含 `"sources": [{"type": "rss", "url": "https://feeds.example.com/rss", "name": "示例RSS"}]`
- **THEN** 系统获取并解析该订阅源

### 需求：分类配置
系统 SHALL 支持分类定义，包含 threshold 和 prompt 字段。

#### 场景：带阈值的分类配置
- **WHEN** 配置包含 `"categories": {"AI": {"threshold": 6}}`
- **THEN** AI 分数 >= 6 的文章被视为与该分类相关

### 需求：主题配置
系统 SHALL 支持主题数组，定义哪些分类与日报相关。

#### 场景：主题选择
- **WHEN** 配置包含 `"topics": ["AI", "自动驾驶"]`
- **THEN** 过滤保留在任何这些主题上分数 >= 阈值的文章

### 需求：JSON Schema 验证
系统 SHALL 验证配置 JSON 符合 schema，对无效结构报错。

#### 场景：无效配置结构
- **WHEN** 配置 JSON 缺少必填字段（如无 llm.api_key）
- **THEN** 系统报告验证错误并退出

### 需求：默认评分提示词
系统 SHALL 为每个标准分类提供默认评分提示词。

#### 场景：默认 AI 提示词
- **WHEN** 分类 "AI" 使用时无显式 prompt
- **THEN** 系统使用默认：`"判断新闻是否与人工智能、大模型、机器学习相关。返回1-10分，1表示完全无关，10表示高度相关。"`

#### 场景：默认分类
- **WHEN** 未配置分类
- **THEN** 系统支持默认分类：`["AI", "自动驾驶", "新能源", "半导体", "软件", "政策"]`