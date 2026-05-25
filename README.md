# Smart Data Agent：基于 LangGraph 的智能数据分析助手

这是我做的一个大模型数据分析项目，目标是把“业务人员问问题 → 数据分析师写 SQL → 查询数据库 → 做图表 → 写结论”这条流程做成一个可运行的 Agent Demo。

用户只需要在页面里输入中文问题，例如“哪个城市的订单量最高？”、“按商品类别统计销售额占比”，系统就会自动生成 SQL、校验 SQL、查询 MySQL，并把结果解释成业务结论，同时推荐合适的图表展示。

> 说明：当前项目使用的是模拟电商订单数据，重点展示 LangGraph Agent 编排、Text-to-SQL、SQL 安全控制和前后端完整闭环。

---

## 项目效果

项目启动后，前端页面支持：

- 中文自然语言提问
- 展示大模型生成的 SQL
- 展示 MySQL 查询结果表格
- 生成中文业务分析结论
- 自动推荐折线图、柱状图、饼图或表格
- 左侧会话记忆，支持新建、切换、删除会话
- 每个会话保留独立的历史查询记录

可以用来演示这些问题：

```text
哪个城市的订单量最高？
按商品类别统计销售额占比。
最近 30 天销售额趋势怎么样？
不同渠道的销售额排名如何？
上个月销售额下降的原因可能是什么？
```

---

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 后端接口 | FastAPI、Pydantic、Uvicorn |
| Agent 编排 | LangGraph、LangChain |
| 大模型调用 | OpenAI-compatible API，默认可接 DeepSeek |
| 数据库 | MySQL 8.0 |
| ORM / 数据库访问 | SQLAlchemy、PyMySQL |
| 前端展示 | Streamlit、Pandas、Plotly |
| 部署 | Docker、Docker Compose |
| 测试 | Pytest、FastAPI TestClient |

---

## 项目目录

```text
smart-data-agent/
├── app/
│   ├── main.py                    # FastAPI 应用入口
│   ├── api/
│   │   ├── routes.py              # API 路由
│   │   └── schemas.py             # 请求和响应模型
│   ├── core/
│   │   ├── config.py              # 环境变量配置
│   │   └── database.py            # 数据库连接和通用查询
│   ├── agent/
│   │   ├── graph.py               # LangGraph 工作流定义
│   │   ├── state.py               # Agent 状态结构
│   │   ├── nodes.py               # Agent 节点实现
│   │   └── prompts.py             # Prompt 模板
│   ├── tools/
│   │   ├── sql_tool.py            # SQL 安全校验和执行
│   │   ├── schema_tool.py         # 业务 Schema 描述
│   │   └── chart_tool.py          # 图表推荐逻辑
│   └── services/
│       └── analysis_service.py    # 业务服务层
├── streamlit_app/
│   └── app.py                     # Streamlit 前端
├── sql/
│   └── init.sql                   # MySQL 表结构和模拟数据
├── tests/
│   ├── test_sql_validate.py       # SQL 安全测试
│   └── test_api.py                # API 基础测试
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## 核心流程

一次完整分析请求的链路如下：

```text
用户输入中文问题
  ↓
Streamlit 调用 FastAPI /api/analyze
  ↓
AnalysisService 调用 LangGraph
  ↓
understand_question：识别问题意图
  ↓
retrieve_schema：获取业务表结构说明
  ↓
generate_sql：调用大模型生成 SQL
  ↓
validate_sql：校验 SQL 安全，只允许 SELECT
  ↓
execute_sql：查询 MySQL
  ↓
analyze_result：生成中文业务分析结论
  ↓
recommend_chart：推荐图表类型
  ↓
Streamlit 展示 SQL、表格、结论和图表
```

LangGraph 的节点定义在：

```text
app/agent/graph.py
app/agent/nodes.py
```

---

## 我重点实现的部分

### 1. LangGraph 多节点 Agent

我把一个数据分析任务拆成多个节点，而不是写成一个大函数：

```text
understand_question
retrieve_schema
generate_sql
validate_sql
execute_sql
analyze_result
recommend_chart
```

这样做的好处是每个节点职责比较清楚，后续如果要加 SQL 自动修复、权限控制、缓存、RAG 检索，都可以继续往图里加节点。

### 2. Schema 上下文增强 Text-to-SQL

项目没有让模型凭空写 SQL，而是在 `schema_tool.py` 里维护了业务 Schema：

- 有哪些表
- 每张表的含义
- 每个字段的含义
- 表之间如何关联
- 销售额、订单量等业务口径

生成 SQL 时会把这些 Schema 信息注入 Prompt，降低模型编造字段的概率。

> 当前实现更准确地说是 Schema-Augmented Text-to-SQL，不是完整 RAG。完整 RAG 可以在后续加入 Embedding 和向量库实现。

### 3. SQL 安全校验

Text-to-SQL 最大的风险是模型可能生成危险 SQL，所以我在执行 SQL 前做了安全校验：

- 只允许 `SELECT`
- 禁止多语句
- 禁止 SQL 注释绕过
- 禁止 `DELETE / UPDATE / INSERT / DROP / ALTER / TRUNCATE` 等关键字
- 没有 `LIMIT` 时自动补充默认限制

相关代码在：

```text
app/tools/sql_tool.py
```

### 4. Streamlit 会话记忆

前端左侧做了一个类似 ChatGPT / DeepSeek 的会话记忆：

- 新建会话
- 切换会话
- 删除会话
- 每个会话保存自己的输入问题
- 每个会话保存最近一次分析结果
- 每个会话有独立历史查询记录

相关代码在：

```text
streamlit_app/app.py
```

---

## 数据从哪里来

项目自带 MySQL 初始化脚本：

```text
sql/init.sql
```

里面创建了 4 张表：

| 表名 | 说明 |
| --- | --- |
| customers | 客户表，包含城市、年龄、会员等级等信息 |
| products | 商品表，包含商品名称、类别、价格、成本 |
| orders | 订单表，核心事实表，用于销售额、订单量、趋势、排行分析 |
| analysis_logs | 分析日志表，保存每次问题、SQL、分析结论和图表类型 |

当前数据是模拟电商订单数据，主要用于演示城市排行、销售额趋势、商品类别占比、渠道分析等场景。

---

## 环境变量

复制示例配置：

```bash
cp .env.example .env
```

Windows PowerShell 可以使用：

```powershell
copy .env.example .env
```

然后配置大模型 API：

```env
LLM_PROVIDER=openai-compatible
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

注意：

- `.env` 不要提交到 GitHub
- `.env.example` 可以提交
- 演示时不要打开 `.env`，避免泄露 API Key

---

## 本地启动方式

我本地演示时采用的是：

```text
Docker 启动 MySQL
本地虚拟环境启动 FastAPI
本地虚拟环境启动 Streamlit
```

因为国内网络环境下 Docker 构建 Python 镜像有时会拉取失败，这种方式更稳定。

### 1. 启动 MySQL

```powershell
cd E:\TSDK\smart-data-agent
docker compose up -d mysql
```

项目中 MySQL 映射到宿主机端口 `3307`，避免和本机已有 MySQL 的 `3306` 冲突。

### 2. 启动 FastAPI

```powershell
cd E:\TSDK\smart-data-agent
.venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

后端接口文档：

```text
http://localhost:8000/docs
```

健康检查：

```text
http://localhost:8000/health
```

### 3. 启动 Streamlit

新开一个终端：

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

## Docker Compose 说明

项目也保留了完整 Docker 配置：

```bash
docker compose up --build
```

包含服务：

```text
mysql
api
streamlit
```

如果本地 Docker Hub 网络正常，可以直接使用完整 Docker Compose 启动。

---

## API 接口

### 健康检查

```http
GET /health
```

### 自然语言分析

```http
POST /api/analyze
Content-Type: application/json

{
  "question": "哪个城市的订单量最高？"
}
```

响应中会包含：

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

### 后端分析日志

```http
GET /api/history?limit=20
```

说明：前端页面里的会话历史是基于 `st.session_state` 的前端会话记忆；后端 `/api/history` 返回的是数据库里的全局分析日志。

---

## 测试

运行测试：

```powershell
cd E:\TSDK\smart-data-agent
.venv\Scripts\python -m pytest tests
```

当前测试覆盖：

- SQL 只允许 SELECT
- 危险 SQL 会被拒绝
- 多语句会被拒绝
- SQL 自动补 LIMIT
- 健康检查接口
- 分析接口基础结构

---

## 已知限制

1. 当前数据是模拟数据，不是真实业务库。
2. Schema 是代码内置描述，不是自动从数据库动态生成。
3. 当前不是完整 RAG，只是 Schema 上下文增强。
4. 前端会话记忆保存在 `st.session_state`，刷新或重启后会丢失。
5. Text-to-SQL 依赖大模型能力，复杂问题可能生成不准确 SQL。
6. 目前 SQL 安全校验基于规则，生产环境建议接入 SQL AST 解析和只读数据库账号。

---

## 后续计划

如果继续完善，我会优先做这些：

- 增加 SQL 自动修复节点
- 增加基于 FAISS / Chroma 的 Schema RAG 检索
- 将前端会话记忆持久化到 MySQL
- 增加字段级白名单和表级权限控制
- 增加查询缓存，减少重复大模型调用
- 增加更多模拟数据和复杂业务指标
- 增加 Docker 镜像国内源或离线依赖安装方案

---

## 简历描述参考

> 基于 FastAPI、LangGraph、MySQL 和 Streamlit 实现智能数据分析 Agent，支持用户通过中文自然语言查询业务数据。系统将分析流程拆分为问题理解、Schema 获取、Text-to-SQL、SQL 安全校验、SQL 执行、结果解释和图表推荐等节点，并通过 Streamlit 实现可视化展示和多会话记忆。项目重点解决大模型生成 SQL 的安全性、业务 Schema 上下文注入和分析结果可视化展示问题。
