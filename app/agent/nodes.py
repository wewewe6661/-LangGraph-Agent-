"""LangGraph 节点实现。"""

import json
from typing import Any

from langchain_openai import ChatOpenAI

from app.agent.prompts import ANALYZE_RESULT_PROMPT, GENERATE_SQL_PROMPT, UNDERSTAND_QUESTION_PROMPT
from app.agent.state import AgentState
from app.core.config import settings
from app.tools.chart_tool import recommend_chart
from app.tools.schema_tool import format_schema_for_prompt
from app.tools.sql_tool import SQLValidationError, execute_safe_select, validate_select_sql


def get_llm() -> ChatOpenAI:
    if not settings.llm_api_key:
        raise RuntimeError("大模型 API Key 未配置，请在 .env 中设置 LLM_API_KEY。")

    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        temperature=settings.llm_temperature,
    )


def understand_question(state: AgentState) -> AgentState:
    if state.get("error"):
        return state

    question = state["question"]
    try:
        prompt = UNDERSTAND_QUESTION_PROMPT.format(question=question)
        intent = get_llm().invoke(prompt).content.strip()
    except Exception:
        intent = _fallback_intent(question)

    return {**state, "intent": intent}


def retrieve_schema(state: AgentState) -> AgentState:
    if state.get("error"):
        return state

    return {**state, "schema_info": format_schema_for_prompt()}


def generate_sql(state: AgentState) -> AgentState:
    if state.get("error"):
        return state

    try:
        prompt = GENERATE_SQL_PROMPT.format(
            question=state["question"],
            intent=state.get("intent", "detail_query"),
            schema_info=state["schema_info"],
        )
        sql = get_llm().invoke(prompt).content.strip()
        return {**state, "generated_sql": sql}
    except Exception as exc:
        return {**state, "error": str(exc), "generated_sql": ""}


def validate_sql(state: AgentState) -> AgentState:
    """校验 SQL 安全性，并自动补充 LIMIT。"""
    if state.get("error"):
        return state

    try:
        validated_sql = validate_select_sql(state.get("generated_sql", ""))
        return {**state, "validated_sql": validated_sql, "sql_error": None}
    except SQLValidationError as exc:
        return {**state, "sql_error": str(exc), "error": str(exc)}


def execute_sql(state: AgentState) -> AgentState:
    """执行安全 SQL 并返回结构化查询结果。"""
    if state.get("error"):
        return state

    rows, columns, error = execute_safe_select(state["validated_sql"])
    if error:
        return {**state, "query_result": [], "columns": [], "error": error}
    return {**state, "query_result": rows, "columns": columns}


def analyze_result(state: AgentState) -> AgentState:
    """调用大模型将查询结果解释为中文业务结论。"""
    if state.get("error"):
        return state

    rows = state.get("query_result", [])
    if not rows:
        return {**state, "analysis": "没有查询到符合条件的数据，建议调整时间范围或筛选条件后重试。"}

    try:
        prompt = ANALYZE_RESULT_PROMPT.format(
            question=state["question"],
            sql=state["validated_sql"],
            result=json.dumps(_json_safe_rows(rows), ensure_ascii=False, default=str),
        )
        analysis = get_llm().invoke(prompt).content.strip()
    except Exception:
        analysis = _fallback_analysis(state["question"], rows)

    return {**state, "analysis": analysis}


def recommend_chart_node(state: AgentState) -> AgentState:
    """根据结果结构推荐适合的图表。"""
    chart_config = recommend_chart(state.get("query_result", []), state.get("question", ""))
    return {
        **state,
        "chart_type": chart_config.get("chart_type", "table"),
        "chart_config": chart_config,
    }


def _fallback_intent(question: str) -> str:
    """大模型不可用时使用关键词兜底识别意图。"""
    if any(word in question for word in ("趋势", "最近", "每日", "每月", "变化")):
        return "trend_analysis"
    if any(word in question for word in ("最高", "最多", "排行", "排名", "TOP")):
        return "ranking_analysis"
    if any(word in question for word in ("占比", "比例", "构成")):
        return "proportion_analysis"
    if any(word in question for word in ("原因", "为什么", "下降", "增长")):
        return "reason_analysis"
    return "detail_query"


def _fallback_analysis(question: str, rows: list[dict[str, Any]]) -> str:
    """大模型不可用时返回基础分析结论。"""
    first_row = rows[0] if rows else {}
    return (
        f"本次问题为：{question}。查询共返回 {len(rows)} 条结果，"
        f"首条结果为 {first_row}。建议结合图表进一步观察核心指标变化。"
    )


def _json_safe_rows(rows: list[dict[str, Any]], limit: int = 20) -> list[dict[str, Any]]:
    """限制传给大模型的数据量，避免 Prompt 过长。"""
    return rows[:limit]
