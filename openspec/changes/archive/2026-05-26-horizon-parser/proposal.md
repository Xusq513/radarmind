## Why

Horizon 是一个每日信息汇总服务，它的 Atom feed 中每个 entry 包含当天全部内容，但 entry 里的 `<content>` 是一个 HTML 页面嵌入了多篇文章（通过 `<hr />` 分隔）。现有的 `atom.py` 解析器把每个 entry 当作一篇 Article，导致标题错误、内容混淆，无法正确提取每篇独立文章。

## What Changes

- 新增 `sources/horizon.py` 专用解析器，按 `<hr />` 分割 content，每段提取为独立 Article
- 在 `sources/factory.py` 中增加 `type: "horizon"` 支持
- `config.json` 中 Horizon 源的 `type` 改为 `"horizon"`
- 支持从 h2 标题中提取真实链接和标题（去掉评分后缀）

## Capabilities

### New Capabilities

- `horizon-parsing`: 专用解析器，将 Horizon daily summary 中的嵌入文章拆解为独立 Article 对象
- `horizon-title-extraction`: 从 `<h2 id="item-N">` 中提取真实文章标题和链接

## Impact

- 新增 `src/radar_mind/sources/horizon.py`
- 修改 `src/radar_mind/sources/factory.py` 增加 horizon type
- 修改 `config.json` 中 Horizon 源的 type 字段
- 无新增依赖