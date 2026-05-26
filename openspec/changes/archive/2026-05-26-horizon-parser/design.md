## Context

Horizon（`https://thysrael.github.io/Horizon/feed`）是一个每日信息汇总的 Atom feed。与普通 RSS/Atom 每条 entry 对应一篇文章不同，Horizon 的每个 entry 是"当天全部内容"，entry 下的 `<content>` 是一个 HTML 页面嵌入了多篇文章。

当前 `atom.py` 解析器把每个 entry 当作一篇 Article 处理：
- title → entry title（如 "Horizon Summary: 2026-05-25 (EN)"）
- description → 整个 content（包含目录 + 所有文章内容）
- 无法提取每篇独立文章的标题、链接、标签

## Goals / Non-Goals

**Goals:**
- 将 Horizon daily summary 中的嵌入文章拆解为独立 Article
- 保留每篇文章的原始链接、标题、正文、标签
- 通过 factory.py 的 `type: "horizon"` 无缝接入现有架构

**Non-Goals:**
- 不处理 Horizon 的中文版 feed（只有 EN）
- 不修改 Article 数据模型本身
- 不处理 h2 之外的嵌套结构

## Decisions

### 1. 独立 `horizon.py` 而非增强 `atom.py`

Horizon 的解析逻辑与通用 Atom 完全不同。通用 Atom 是"entry = 1 article"，而 Horizon 是"entry = n articles via `<hr />` split"。

强行在 `atom.py` 里加条件分支会导致职责混乱。独立文件让代码更清晰，也方便维护。

**Alternatives considered:**
- 在 `atom.py` 中加 `is_horizon` flag ❌ 违反单一职责
- 在 factory.py 里根据 URL 特征判断 ❌ 脆弱，URL 可能变

### 2. 按 `<hr />` 分割 content

Horizon 的 HTML 结构中，每篇文章以 `<hr />` 分隔。

**Decision:** 使用字符串 split 而非 HTML 解析器（BeautifulSoup）。
**Why:** content 已经是 CDATA 包裹的 HTML 字符串，结构简单，直接 split 足够。
**Alternatives:**
- BeautifulSoup 解析 ❌ 增加依赖，overkill
- lxml ❌ 同上

### 3. h2 提取策略

每篇文章的结构：
```html
<p><a id="item-1"></a></p>
<h2 id="spyware-backdoor-found-in-telegram-on-apkpure-️-9010">
  <a href="https://x.com/EricParker/status/...">Spyware Backdoor Found in Telegram on APKPure</a> ⭐️ 9.0/10
</h2>
```

**提取 link:** h2 内第一个 `<a href="...">` 的 href
**提取 title:** h2 内文本，去掉 ` ⭐️ X.X/10` 后缀

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Horizon HTML 结构变化（`<hr />` 位置变了） | 解析失败时回退到整个 entry 作为一篇文章 |
| h2 内有多余的 `<a>`（如 discussion link） | 只取第一个 `<a>` 作为 link |
| 评分后缀格式变化（`⭐️ 9.0/10` 非标准） | 用正则 ` ⭐️ \d+\.\d+/10$` 匹配并移除 |

## Open Questions

- 是否需要处理 `<ol>` 目录中的锚点映射（目前目录信息被丢弃）？
- 如果某篇文章没有 `<h2>`（极端情况），是否跳过？
- 是否支持中文版 Horizon feed（`summary-cn.html`）？