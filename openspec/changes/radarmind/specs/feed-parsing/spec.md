## 新增需求

### 需求：RSS 订阅源解析
系统 SHALL 解析 RSS 2.0 格式订阅源，提取标题、链接、描述和发布日期。

#### 场景：有效 RSS 订阅源解析
- **WHEN** 系统接收到有效的 RSS 2.0 feed XML
- **THEN** 它提取所有包含 title、link、description 和 pubDate 字段的 `<item>` 元素

#### 场景：RSS 条目缺失字段
- **WHEN** RSS 条目缺少 description 或 pubDate
- **THEN** 系统对缺失字段使用空字符串

#### 场景：RSS 获取失败
- **WHEN** RSS 端点不可达或返回非 200 状态
- **THEN** 系统记录警告并继续处理下一个订阅源

### 需求：ATOM 订阅源解析
系统 SHALL 解析 ATOM 1.0 格式订阅源，提取标题、链接、摘要和发布日期。

#### 场景：有效 ATOM 订阅源解析
- **WHEN** 系统接收到有效的 ATOM 1.0 feed XML
- **THEN** 它提取所有包含 title、link (href)、summary 和 published 字段的 `<entry>` 元素

#### 场景：ATOM 链接处理
- **WHEN** ATOM 条目有多个不同 rel 属性的链接
- **THEN** 系统优先选择 rel="alternate" 的链接，若无则选第一个链接

### 需求：订阅源类型抽象
系统 SHALL 支持可插拔的订阅源架构，新订阅源类型可在不修改核心逻辑的情况下添加。

#### 场景：订阅源注册
- **WHEN** 实现了新的订阅源类型（如 "api" 或 "web"）
- **THEN** 它可通过订阅源工厂注册并统一调用

#### 场景：统一文章格式
- **WHEN** 从任何订阅源类型返回文章
- **THEN** 它们都符合标准 Article 模型（title, link, description, pub_date）