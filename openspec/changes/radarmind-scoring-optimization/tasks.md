## 1. scorer.py 重写

- [x] 1.1 删除原有的 score_article() 和 score_categories() 方法
- [x] 1.2 新增 score_batch(articles, categories) 方法
- [x] 1.3 实现批量评分 prompt 构建
- [x] 1.4 实现 JSON 响应解析和验证
- [x] 1.5 实现重试逻辑（最多 3 次）
- [x] 1.6 添加自定义异常类 ScoringError

## 2. cli.py 适配

- [x] 2.1 修改评分调用方式，从串行改为批量
- [x] 2.2 更新结果处理逻辑，适配新的返回格式
- [x] 2.3 移除原有的评分进度日志（单次调用无需进度）

## 3. 提示词模板更新

- [x] 3.1 更新 prompts/scoring.j2 为批量评分模板
- [x] 3.2 更新默认分类提示词说明

## 4. 测试验证

- [ ] 4.1 使用真实 API Key 运行完整流程
- [ ] 4.2 验证评分结果正确性
- [ ] 4.3 验证失败重试机制