## 背景

当前 RadarMind 的 AI 评分采用串行方式：每篇文章对每个分类单独调用 LLM API。

**当前调用模式：**
```
30 篇文章 × 6 个分类 = 180 次 API 调用
每次调用耗时约 1-2 秒
总耗时：3-6 分钟
```

**问题：** 延迟太高，用户体验差。

## 目标 / 非目标

**目标：**
- 将 API 调用次数从 180 次降到 1 次
- 评分延迟从分钟级降到秒级
- 只使用新闻标题进行评分，减少 token 消耗
- 失败重试 3 次，超过则抛出异常

**非目标：**
- 不需要降级方案（失败则直接报错）
- 不支持部分成功（要么全部成功，要么重试到失败）

## 关键设计决策

### 1. 批量评分 Prompt 设计

```python
PROMPT_TEMPLATE = """请分析以下新闻列表，判断每条新闻与各分类的相关度。

新闻列表:
{news_list}

分类说明:
- AI: 与人工智能、大模型、机器学习相关
- 自动驾驶: 与自动驾驶、车载系统相关
- 新能源: 与新能源汽车、电池技术相关
- 半导体: 与芯片、半导体制造相关
- 软件: 与软件开发、SaaS、云计算相关
- 政策: 与政府政策、监管法规相关

返回格式（纯JSON数组，不要包含其他文字）:
[
  {{"AI": 8, "自动驾驶": 3, "新能源": 2, "半导体": 9, "软件": 4, "政策": 1}},
  {{"AI": 3, "自动驾驶": 7, ...}},
  ...
]
"""
```

**格式选择 JSON 数组而非对象：**
- 数组按索引对应文章，简洁明了
- 对象键需要与文章一一对应，容易出错

### 2. 重试策略

```python
MAX_RETRIES = 3

def score_batch(articles, categories):
    for attempt in range(MAX_RETRIES):
        try:
            result = call_llm(build_prompt(articles, categories))
            return parse_result(result)  # 验证格式
        except (ParseError, JSONDecodeError) as e:
            if attempt == MAX_RETRIES - 1:
                raise ScoringError(f"Failed after {MAX_RETRIES} attempts: {e}")
            continue  # 重试
```

**触发重试的条件：**
- LLM 返回格式错误（无法解析为 JSON）
- JSON 结构不符合预期（缺少字段、类型错误）
- 网络超时或其他异常

**不重试的条件：**
- API 返回 401/403 等认证错误（立即失败）

### 3. 分数解析与验证

```python
def parse_score(value) -> int:
    """将分数解析为 1-10 的整数"""
    if isinstance(value, int):
        return max(1, min(10, value))
    if isinstance(value, str):
        numbers = re.findall(r'\d+', value)
        if numbers:
            return max(1, min(10, int(numbers[0])))
    return 0  # 无效值返回 0
```

**验证规则：**
- 每个分类的分数必须在 1-10 范围内
- 缺失的分类默认分数为 0
- 返回的分类数量必须与配置的分类数量一致

### 4. 输入简化

**只用标题的理由：**
- 标题通常已经包含文章的核心主题
- 减少 token 消耗（从 title+description 200字 → 仅 title）
- 批量评分时，减少输入长度很重要

## 风险与权衡

| 风险 | 缓解措施 |
|------|----------|
| 单次调用内容过多超出 token 限制 | 目前 30 篇文章标题约 300-600 字，远低于限制 |
| LLM 忽略部分文章 | 提示词明确说明"共N条"，让其意识到完整性 |
| 返回格式不稳定 | 重试机制 + 最终抛出异常保证数据一致性 |

## 实现计划

```
scorer.py 重写:
  1. 删除 score_article() 和 score_categories()
  2. 新增 score_batch(articles, categories) 方法
  3. 实现重试逻辑和格式验证
  4. 返回 [{分类: 分数}, ...] 列表
```

## 待解决问题

无