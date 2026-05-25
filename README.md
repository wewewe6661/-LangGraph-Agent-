# Smart Data Agent

这是我做的一个自然语言查数项目，主要解决一个很常见的问题：业务同学想临时看数据，但不一定会写 SQL。

项目的使用方式比较直接：在页面里输入中文问题，比如“哪个城市的订单量最高？”或者“最近 30 天销售额趋势怎么样？”，后端会生成 SQL、做安全校验、查询 MySQL，然后把结果整理成表格、分析结论和图表。

这个项目里我重点做了两件事：一是用 LangGraph 把一次分析请求拆成多个节点，方便调试和扩展；二是给 Text-to-SQL 加了一层 SQL 安全校验，避免模型生成危险语句后直接执行。

---

## 主要功能

- 中文自然语言查询 MySQL 数据
- 根据业务 Schema 生成查询 SQL
- 使用 LangGraph 编排分析流程
- 执行前校验 SQL，只允许 `SELECT`
- 查询结果自动生成中文分析结论
- 根据结果推荐折线图、柱状图、饼图或表格
- Streamlit 页面展示 SQL、结果表格、结论和图表
- 左侧支持多会话切换、删除和独立历史记录
- FastAPI 提供分析接口、历史记录接口和健康检查接口

---

## 技术栈

| 模块 | 技术 |
| --- | --- |
| 后端接口 | Python, FastAPI, Pydantic, Uvicorn |
| Agent 工作流 | LangGraph, LangChain |
| 大模型调用 | OpenAI-compatible API, DeepSeek |
| 数据库 | MySQL 8.0 |
| 数据库访问 | SQLAlchemy, PyMySQL |
| 前端页面 | Streamlit, Pandas, Plotly |
| 部署运行 | Docker, Docker Compose |
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
│   │   ├── config.py              # 配置读取
│   │   └── database.py            # MySQL 连接和查询封装
│   ├── agent/
│   │   ├── graph.py               # LangGraph 工作流
│   │   ├── state.py               # Agent 状态结构
│   │   ├── nodes.py               # 工作流节点
│   │   └── prompts.py             # Prompt 模板
│   ├── tools/
│   │   ├── sql_tool.py            # SQL 校验和安全执行
│   │   ├── schema_tool.py         # 业务 Schema 描述
│   │   └── chart_tool.py          # 图表推荐
│   └── services/
│       └── analysis_service.py    # API 与 Agent 的衔接层
├── streamlit_app/
│   └── app.py                     # 前端页面
├── sql/
│   └── init.sql                   # 表结构和样例数据
├── tests/
│   ├── test_sql_validate.py       # SQL 校验测试
│   └── test_api.py                # API 测试
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## 整体流程

```text
用户输入中文问题
  ↓
Streamlit 调用 FastAPI
  ↓
AnalysisService 调用 Agent
  ↓
LangGraph 按节点处理
  ↓
获取 Schema 上下文
  ↓
生成 SQL
  ↓
校验 SQL
  ↓
查询 MySQL
  ↓
生成分析结论
  ↓
推荐图表
  ↓
返回前端展示
```

LangGraph 节点顺序：

```text
understand_question
retrieve_schema
generate_sql
validate_sql
execute_sql
analyze_result
recommend_chart
```

---

## 关键实现

### 1. LangGraph 工作流

我没有把整个分析过程写成一个大函数，而是拆成了几个节点：

- `understand_question`：判断问题类型，比如趋势、排行、占比、明细查询
- `retrieve_schema`：读取业务表结构说明
- `generate_sql`：让模型根据问题和 Schema 生成 SQL
- `validate_sql`：执行前检查 SQL 是否安全
- `execute_sql`：查询 MySQL
- `analyze_result`：把结果整理成中文结论
- `recommend_chart`：根据字段推荐图表

这样做的好处是每一步都比较清楚，后面要加权限校验、SQL 自动修复、缓存或者 Schema RAG，也比较容易接进去。

### 2. Schema 约束

Schema 信息维护在 [app/tools/schema_tool.py](app/tools/schema_tool.py)。

里面写了表名、字段含义、表之间的关系，以及一些业务口径，比如销售额默认用哪个字段、订单量怎么算、趋势分析按哪个日期字段聚合。

生成 SQL 时会把这些信息一起传给模型，尽量减少模型编造字段名或者用错表的情况。

### 3. SQL 安全校验

Text-to-SQL 不能直接相信模型输出，所以我在 [app/tools/sql_tool.py](app/tools/sql_tool.py) 里加了校验：

- 只允许 `SELECT`
- 不允许多条 SQL
- 不允许 SQL 注释
- 拒绝 `DELETE`、`UPDATE`、`INSERT`、`DROP`、`ALTER`、`TRUNCATE` 等危险关键字
- 没有 `LIMIT` 时自动补一个默认限制

这个版本还是规则校验。真要放到企业里，还需要配合只读账号、字段权限、查询超时和 SQL AST 校验。

### 4. 前端会话

前端用 Streamlit 做了一个简单的分析页面，左侧可以新建、切换和删除会话。每个会话会保留自己的最近一次结果和历史查询记录，方便对比不同问题的分析结果。

---

## 数据说明

为了方便本地运行，项目在 [sql/init.sql](sql/init.sql) 里准备了一组电商订单样例数据。

主要表：

| 表名 | 说明 |
| --- | --- |
| customers | 客户信息，包括城市、年龄、会员等级等 |
| products | 商品信息，包括商品名称、品类、价格、成本等 |
| orders | 订单事实表，用于销售额、订单量、趋势和排行分析 |
| analysis_logs | 分析日志表，记录问题、SQL、结论和图表类型 |

可以覆盖的典型问题：

```text
哪个城市的订单量最高？
按商品类别统计销售额占比。
最近 30 天销售额趋势怎么样？
不同渠道的销售额排名如何？
```

---

## 环境变量

复制配置模板：

```bash
cp .env.example .env
```

Windows PowerShell：

```powershell
copy .env.example .env
```

配置大模型接口：

```env
LLM_PROVIDER=openai-compatible
LLM_API_KEY=
LLM_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

真实的 `.env` 不要提交到仓库，也不要在演示截图里展示 API Key。

---

## 本地启动

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

MySQL 映射到本机端口：

```text
localhost:3307 -> container:3306
```

### 3. 启动 FastAPI

```powershell
.venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

访问：

```text
http://localhost:8000/health
http://localhost:8000/docs
```

### 4. 启动 Streamlit

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

也可以直接启动完整服务：

```bash
docker compose up --build
```

服务包括：

```text
mysql
api
streamlit
```

本地调试时，我一般只用 Docker 启动 MySQL，FastAPI 和 Streamlit 放在本地虚拟环境里跑，这样排查问题更方便。

---

## API

### 健康检查

```http
GET /health
```

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

响应字段包括：

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

这里返回的是后端写入 MySQL 的分析日志；前端左侧的会话历史保存在当前浏览器会话中。

---

## 测试

```powershell
cd E:\TSDK\smart-data-agent
.venv\Scripts\python -m pytest tests
```

测试覆盖：

- SELECT SQL 校验
- 危险 SQL 拒绝
- 多语句 SQL 拒绝
- 自动追加 `LIMIT`
- FastAPI 健康检查接口
- 基础 API 响应结构

---

## 说明

- 样例数据只用于本地开发和功能验证，不包含真实业务数据。
- Schema 目前写在代码里，适合表数量较少的场景；如果接企业数据，可以改成读取数据字典或做 Schema RAG。
- Streamlit 会话记录保存在浏览器会话状态里，刷新或重启后不会持久化。
- SQL 校验是规则实现，正式环境建议增加只读账号、SQL AST 校验、字段级权限和审计日志。
