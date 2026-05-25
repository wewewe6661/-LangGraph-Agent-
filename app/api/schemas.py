"""FastAPI 请求和响应数据模型。"""

from typing import Any

from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    """自然语言分析请求。"""

    question: str = Field(..., min_length=2, max_length=500, description="用户的中文自然语言问题")


class ChartConfig(BaseModel):
    """前端渲染图表所需配置。"""

    chart_type: str = Field(default="table", description="图表类型：line、bar、pie、table")
    x: str | None = Field(default=None, description="X 轴字段")
    y: str | None = Field(default=None, description="Y 轴字段")
    title: str = Field(default="查询结果", description="图表标题")


class AnalyzeResponse(BaseModel):
    """自然语言分析接口响应。"""

    question: str
    intent: str = ""
    generated_sql: str = ""
    validated_sql: str = ""
    columns: list[str] = Field(default_factory=list)
    rows: list[dict[str, Any]] = Field(default_factory=list)
    analysis: str = ""
    chart: ChartConfig = Field(default_factory=ChartConfig)
    error: str | None = None


class QueryHistoryItem(BaseModel):
    """历史查询记录展示模型。"""

    id: int
    question: str
    generated_sql: str
    analysis: str
    chart_type: str
    created_at: Any


class HealthResponse(BaseModel):
    """健康检查接口响应。"""

    status: str
    app_name: str
