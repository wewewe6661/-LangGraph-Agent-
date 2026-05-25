# Smart Data Agent

基于 **LangGraph + FastAPI + Streamlit + MySQL** 的智能数据分析 Agent 系统。用户可以输入中文自然语言问题，系统会自动完成业务意图理解、Schema 上下文获取、Text-to-SQL、SQL 安全校验、MySQL 查询、结果解释和图表推荐。

当前项目使用模拟电商订单数据，适合用于演示自然语言数据分析、Text-to-SQL 工程落地和 LangGraph 多节点 Agent 编排。

---

## 功能特性

- 支持中文自然语言数据查询
- 基于业务 Schema 生成 MySQL 查询 SQL
- 使用 LangGraph 编排多节点 Agent 工作流
- SQL 安全校验：只允许执行 `SELECT` 查询
- 支持 MySQL 业务数据查询和分析结果生成
- 自动推荐折线图、柱状图、饼图或表格
- 使用 Streamlit 构建可视化交互页面
- 左侧会话记忆：支持新建、切换、删除会话
- 每个会话独立保存历史查询记录
- 提供 FastAPI 接口和 Swagger 文档
- 使用 Docker Compose 管理 MySQL 服务

---

## 技术栈

| 层级 | 技术 |
| --- | --- |
| 后端服务 | Python, FastAPI, Pydantic, Uvicorn |
| Agent 编排 | LangGraph, LangChain |
| 大模型接口 | OpenAI-compatible API, DeepSeek |
| 数据库 | MySQL 8.0 |
| 数据库访问 | SQLAlchemy, PyMySQL |
| 前端页面 | Streamlit, Pandas, Plotly |
| 部署与运行 | Docker, Docker Compose |
| 测试 | Pytest, FastAPI TestClient |

---

## 项目结构

```text
smart-data-agent/
├── app/
│   ├── main.py                    # FastAPI 应用入口
│   ├── api/
│   │   ├── routes.py              # API 路由
│   │   └── schemas.py             # 请求与响应模型
│   ├── core/
│   │   ├── config.py              # 环境变量配置
│   │   └── database.py            # 数据库连接与查询工具
│   ├── agent/
│   │   ├── graph.py               # LangGraph 工作流定义
│   │   ├── state.py               # Agent 状态定义
│   │   ├── nodes.py               # Agent 节点实现
│   │   └── prompts.py             # Prompt 模板
│   ├── tools/
│   │   ├── sql_tool.py            # SQL 校验与执行辅助函数
│   │   ├── schema_tool.py         # 业务 Schema 描述
│   │   └── chart_tool.py          # 图表推荐逻辑
│   └── services/
│       └── analysis_service.py    # API 与 Agent 之间的服务层
├── streamlit_app/
│   └── app.py                     # Streamlit 前端页面
├── sql/
│   └── init.sql                   # MySQL 表结构与模拟数据
├── tests/
│   ├── test_sql_validate.py       # SQL 安全校验测试
│   └── test_api.py                # API 接口测试
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## 系统流程

```text
用户输入中文问题
  ↓
Streamlit 前端页面
  ↓
FastAPI /api/analyze
  ↓
AnalysisService
  ↓
LangGraph Agent
  ↓
understand_question：识别业务分析意图
  ↓
retrieve_schema：获取业务 Schema 上下文
  ↓
generate_sql：生成 MySQL SELECT SQL
  ↓
validate_sql：校验 SQL 安全性
  ↓
execute_sql：执行 MySQL 查询
  ↓
analyze_result：生成中文业务分析结论
  ↓
recommend_chart：推荐图表类型
  ↓
Streamlit 展示 SQL、表格、结论和图表
```

LangGraph 工作流主要位于：

```text
app/agent/graph.py
app/agent/nodes.py
app/agent/state.py
```

---

## 核心模块

### 1. LangGraph Agent 工作流

Agent 被拆分为多个职责明确的节点：

```text
understand_question      # 识别分析意图
retrieve_schema          # 加载业务 Schema
generate_sql             # 生成 MySQL SELECT SQL
validate_sql             # 校验 SQL 安全性
execute_sql              # 查询 MySQL
analyze_result           # 生成业务分析结论
recommend_chart          # 推荐图表类型
```

这种拆分方式便于调试、扩展和定位问题。

### 2. Schema-Augmented Text-to-SQL

项目在以下文件中维护业务 Schema 描述：

```text
app/tools/schema_tool.py
```

Schema 内容包括：

- 表名
- 字段名
- 字段含义
- 表关系
- 常用业务指标口径，例如销售额、订单量、成交订单

生成 SQL 时会把这些 Schema 信息注入 Prompt，减少模型生成不存在表名或字段名的概率。

### 3. SQL 安全校验

每一条模型生成的 SQL 在执行前都会经过安全校验：

```text
app/tools/sql_tool.py
```

当前规则包括：

- 只允许 `SELECT` 查询
- 禁止多条 SQL 语句
- 禁止 SQL 注释
- 禁止 `DELETE`、`UPDATE`、`INSERT`、`DROP`、`ALTER`、`TRUNCATE` 等危险关键字
- 如果缺少 `LIMIT`，自动追加默认限制

### 4. Streamlit 会话记忆

前端左侧提供类似对话应用的会话列表：

- 新建会话
- 切换会话
- 删除会话
- 保留每个会话最近一次分析结果
- 保留每个会话独立的历史查询记录

前端实现文件：

```text
streamlit_app/app.py
```

---

## 数据来源

项目使用模拟电商订单数据，初始化脚本位于：

```text
sql/init.sql
```

主要数据表如下：

| 表名 | 说明 |
| --- | --- |
| customers | 客户信息，包括城市、年龄、会员等级等 |
| products | 商品信息，包括商品名称、品类、价格、成本等 |
| orders | 订单事实表，用于销售额、订单量、趋势、排行分析 |
| analysis_logs | 后端分析日志，记录问题、SQL、分析结论等 |

模拟数据覆盖城市排行、销售趋势、品类占比、渠道分析等常见业务分析场景。

---

## 环境变量

复制示例配置文件：

```bash
cp .env.example .env
```

Windows PowerShell：

```powershell
copy .env.example .env
```

配置大模型服务：

```env
LLM_PROVIDER=openai-compatible
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

注意事项：

- 不要提交 `.env` 文件
- 不要把真实 API Key 写入 README、截图或演示材料
- 公开仓库只保留 `.env.example` 作为配置模板

---

## 快速启动

### 1. 安装依赖

```powershell
cd E:\TSDK\smart-data-agent
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

### 2. 启动 MySQL

```powershell
docker compose up -d mysql
```

当前 MySQL 容器端口映射为：

```text
localhost:3307 -> container:3306
```

### 3. 启动 FastAPI 后端

```powershell
.venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

接口文档：

```text
http://localhost:8000/docs
```

健康检查：

```text
http://localhost:8000/health
```

### 4. 启动 Streamlit 前端

打开另一个终端：

```powershell
cd E:\TSDK\smart-data-agent
$env:API_BASE_URL="http://localhost:8000"
.venv\Scripts\python -m streamlit run streamlit_app/app.py --server.port 8501
```

前端页面：

```text
http://localhost:8501
```

---

## Docker Compose

项目也提供完整 Docker Compose 配置：

```bash
docker compose up --build
```

包含服务：

```text
mysql
api
streamlit
```

本地开发时，通常可以只用 Docker 启动 MySQL，然后在本地虚拟环境中运行 FastAPI 和 Streamlit，这样更方便调试。

---

## API 接口

### 健康检查

```http
GET /health
```

响应示例：

```json
{
  "status": "ok",
  "app_name": "Smart Data Agent"
}
```

### 自然语言分析

```http
POST /api/analyze
Content-Type: application/json

{
  "question": "哪个城市的订单量最高？"
}
```

响应字段示例：

```json
{
  "question": "哪个城市的订单量最高？",
  "intent": "ranking_analysis",
  "generated_sql": "SELECT ...",
  "validated_sql": "SELECT ... LIMIT 100",
  "columns": ["city", "order_count"],
  "rows": [],
  "analysis": "中文业务分析结论",
  "chart": {
    "chart_type": "bar",
    "x": "city",
    "y": "order_count",
    "title": "city 与 order_count 对比"
  },
  "error": null
}
```

### 历史记录

```http
GET /api/history?limit=20
```

说明：Streamlit 左侧会话历史保存在浏览器会话状态中，`/api/history` 返回的是后端写入 MySQL 的分析日志。

---

## 演示问题

```text
哪个城市的订单量最高？
按商品类别统计销售额占比。
最近 30 天销售额趋势怎么样？
不同渠道的销售额排名如何？
上个月销售额下降的原因可能是什么？
```

---

## 测试

在项目根目录执行：

```powershell
cd E:\TSDK\smart-data-agent
.venv\Scripts\python -m pytest tests
```

当前测试覆盖：

- SELECT SQL 校验
- 危险 SQL 拒绝
- 多语句 SQL 拒绝
- 自动追加 `LIMIT`
- FastAPI 健康检查接口
- 基础 API 响应结构

---

## 注意事项

- 当前数据为模拟电商数据，主要用于项目演示。
- Schema 描述维护在代码中，并不是从数据库动态生成。
- 当前实现属于 Schema-Augmented Text-to-SQL，不是完整的向量数据库 RAG 系统。
- Streamlit 会话记忆保存在浏览器会话状态中，刷新页面或重启服务后不会持久化。
- Text-to-SQL 效果依赖大模型输出质量，复杂问题可能需要继续优化 Prompt 或 Schema 描述。
- SQL 校验目前基于规则实现，生产环境建议配合只读数据库账号和更严格的 SQL AST 校验。
