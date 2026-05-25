"""LangGraph Agent 状态定义。"""

from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    """在 LangGraph 各节点之间传递的数据结构。"""

    question: str
    intent: str
    schema_info: str

    generated_sql: str
    validated_sql: str
    sql_error: str | None

    query_result: list[dict[str, Any]]
    columns: list[str]

    analysis: str

    chart_type: str
    chart_config: dict[str, Any]

    error: str | None
