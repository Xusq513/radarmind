## 新增需求

### 需求：CLI 入口
CLI 工具 SHALL 通过 `python -m radar_mind` 或 `radarmind` 命令调用，带 `--config` 参数指向 JSON 配置文件。

#### 场景：CLI 帮助显示
- **WHEN** 用户运行 `python -m radar_mind --help`
- **THEN** 系统显示包含可用选项的使用说明

#### 场景：配置文件加载
- **WHEN** 用户通过 `--config config.json` 提供有效配置路径
- **THEN** 系统加载并解析 JSON 配置

#### 场景：无效配置处理
- **WHEN** 用户提供了无效的配置文件（格式错误的 JSON）
- **THEN** 系统退出并显示错误信息，非零退出码

### 需求：环境变量替换
系统 SHALL 支持在配置值中使用 `${VAR_NAME}` 语法进行环境变量替换。

#### 场景：从环境读取 API Key
- **WHEN** 配置包含 `"api_key": "${OPENAI_API_KEY}"`
- **THEN** 系统将其替换为实际的环境变量值

#### 场景：缺失的环境变量
- **WHEN** 配置引用 `${NONEXISTENT_VAR}` 但该变量未设置
- **THEN** 系统使用空字符串或根据字段类型报告错误

### 需求：日志输出
系统 SHALL 在执行期间向 stderr 输出进度和状态信息。

#### 场景：运行状态输出
- **WHEN** 系统正在处理订阅源
- **THEN** 它打印当前状态（如 "正在获取 RSS: 36kr"）