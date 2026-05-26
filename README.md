# RadarMind

信息源 → AI 评分 → 过滤 → 行业简报生成

## 快速启动

### 1. 安装依赖

```bash
uv sync
```

### 2. 配置环境变量

```bash
export MINIMAX_API_KEY="your_api_key_here"
```

### 3. 修改配置

编辑 `config.json`，调整 `sources`（信息源）、`categories`（分类）和 `topics`（关注领域）。

### 4. 运行

```bash
uv run radarmind
```

## 工程结构

```
radarmind/
├── src/radar_mind/          # 主包
│   ├── cli.py               # 命令行入口
│   ├── config.py            # 配置加载
│   ├── fetcher.py           # RSS/Atom 获取
│   ├── filter.py            # 阈值过滤
│   ├── generator.py         # 简报生成
│   ├── scorer.py            # AI 评分
│   └── sources/             # 信息源抽象
│       ├── article.py       # 文章模型
│       ├── atom.py          # Atom 解析
│       ├── rss.py           # RSS 解析
│       └── factory.py       # 工厂方法
├── tests/                   # 测试
├── prompts/                 # Jinja2 模板
├── output/                  # 生成结果
└── config.json              # 配置文件
```

## 配置说明

`config.json` 核心字段：

| 字段 | 说明 |
|------|------|
| `llm.base_url` | LLM API 地址 |
| `llm.model` | 模型名称 |
| `sources` | 信息源列表（RSS/Atom） |
| `categories` | 分类及评分阈值 |
| `topics` | 关注领域 |