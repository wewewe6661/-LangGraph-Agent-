# 基于 LangGraph 的智能数据分析 Agent 系统

这是一个面向业务数据分析场景的 AI Agent 项目。用户可以输入中文自然语言问题，系统会自动完成 Schema 检索、Text-to-SQL 生成、SQL 安全校验、MySQL 查询、结果解释、图表推荐，并通过 Streamlit 页面展示分析结果。

## 1. 项目整体说明

系统目标是让业务人员用自然语言直接查询数据库，例如：

- 最近 30 天销售额趋势怎么样？
- 哪个城市的订单量最高？
- 上个月销售额下降的原因可能是什么？
- 按商品类别统计销售额占比。

项目使用 FastAPI 提供后端接口，使用 LangGraph 编排 Agent 工作流，使用 MySQL 存储模拟业务数据，使用 Streamlit 展示交互页面，使用 Docker Compose 一键启动完整环境。

## 2. 技术栈

- Python
- FastAPI
- Streamlit
- MySQL
- Docker / Docker Compose
- LangChain
- LangGraph
- SQLAlchemy / PyMySQL
- Pydantic
- Plotly

## 3. 项目目录结构

```text
smart-data-agent/
├── app/
│   ├── main.py
│   ├── api/
│   │   ├── routes.py
│   │   └── schemas.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   ├── agent/
│   │   ├── graph.py
│   │   ├── state.py
│   │   ├── nodes.py
│   │   └── prompts.py
│   ├── tools/
│   │   ├── sql_tool.py
│   │   ├── schema_tool.py
│   │   └── chart_tool.py
│   └── services/
│       └── analysis_service.py
├── streamlit_app/
│   └── app.py
├── sql/
│   └── init.sql
├── tests/
│   ├── test_sql_validate.py
│   └── test_api.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## 4. 数据流转流程

```text
用户中文问题
  ↓
Streamlit 前端
  ↓
FastAPI /api/analyze
  ↓
LangGraph Agent
  ↓
understand_question：识别分析意图
  ↓
retrieve_schema：获取数据库 Schema 描述
  ↓
generate_sql：调用大模型生成 SQL
  ↓
validate_sql：只允许 SELECT，禁止危险 SQL，自动添加 LIMIT
  ↓
execute_sql：查询 MySQL
  ↓
analyze_result：生成中文业务分析结论
  ↓
recommend_chart：推荐折线图、柱状图、饼图或表格
  ↓
Streamlit 展示 SQL、表格、结论和图表
```

## 5. 核心功能

### 自然语言数据查询

用户输入中文问题，系统通过 LangGraph 工作流生成 SQL 并查询 MySQL。

### Schema 理解

`app/tools/schema_tool.py` 中维护了业务 Schema 描述，包括表说明、字段说明和表关联关系。Text-to-SQL 生成时必须参考这些 Schema 信息。

### SQL 安全校验

`app/tools/sql_tool.py` 实现了 SQL 安全控制：

- 只允许 SELECT 查询。
- 禁止 DELETE、UPDATE、INSERT、DROP、ALTER、TRUNCATE 等危险语句。
- 禁止多语句执行。
- 禁止 SQL 注释绕过。
- 自动添加 LIMIT，避免返回过多数据。

### 图表推荐

`app/tools/chart_tool.py` 会根据查询结果字段自动推荐：

- 日期字段 + 数值字段：折线图。
- 类别字段 + 数值字段：柱状图。
- 占比类问题：饼图。
- 其他情况：表格。

## 6. 环境变量配置

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

然后编辑 `.env`，配置你的大模型 API：

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

如果你使用的是其他 OpenAI 兼容模型服务，只需要修改 `LLM_BASE_URL` 和 `LLM_MODEL`。

## 7. Docker 启动方式

在项目根目录执行：

```bash
docker compose up --build
```

启动后访问：

- FastAPI：http://localhost:8000
- FastAPI 文档：http://localhost:8000/docs
- Streamlit：http://localhost:8501
- MySQL：localhost:3306

如果是旧版本 Docker Compose，也可以使用：

```bash
docker-compose up --build
```

## 8. 接口说明

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

响应字段：

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

### 历史查询

```http
GET /api/history?limit=20
```

## 9. 测试方式

本地安装依赖后执行：

```bash
pip install -r requirements.txt
pytest
```

如果使用 Docker，可以进入 API 容器执行：

```bash
docker compose exec api pytest
```

## 10. 演示问题示例

- 最近 30 天销售额趋势怎么样？
- 哪个城市的订单量最高？
- 按商品类别统计销售额占比。
- 不同渠道的销售额排名如何？
- 上个月销售额下降的原因可能是什么？
- 各商品类别的订单量分别是多少？
- 最近每月的销售额变化趋势如何？

## 11. 简历项目描述

可以写成：

> 设计并实现基于 LangGraph 的智能数据分析 Agent 系统，支持业务人员通过中文自然语言查询 MySQL 业务数据。系统使用 LangGraph 编排“问题理解、Schema 检索、Text-to-SQL、SQL 安全校验、SQL 执行、结果解释、图表推荐”等节点，结合 FastAPI 提供后端服务、Streamlit 提供可视化页面，并通过 Docker Compose 实现 FastAPI、Streamlit、MySQL 一键部署。

项目亮点：

- 使用 LangGraph 构建多节点 Agent 工作流，节点职责清晰，可观测性强。
- 使用 LangChain 调用 OpenAI 兼容大模型完成 Text-to-SQL 和业务结果解释。
- 设计 SQL 安全校验机制，只允许 SELECT，禁止危险语句和多语句执行。
- 设计 MySQL 模拟业务库，支持销售额趋势、城市排行、商品类别占比等典型分析场景。
- 使用 Streamlit + Plotly 自动展示表格、折线图、柱状图和饼图。
- 使用 FastAPI 提供分析接口、历史记录接口和健康检查接口。
- 使用 Docker Compose 编排 API、前端、MySQL，方便演示和部署。

## 12. 后续可优化方向

- 增加基于向量数据库的 Schema RAG 检索。
- 增加 SQL 自动修复节点，当数据库执行失败时让大模型修正 SQL。
- 增加多轮对话能力，支持基于上一次分析继续追问。
- 增加权限控制，不同用户只能查询授权表和字段。
- 增加查询缓存，降低重复问题的数据库和大模型调用成本。
- 增加图表配置微调能力，让用户手动选择 X 轴、Y 轴和图表类型。
- 增加更完善的单元测试和集成测试。
