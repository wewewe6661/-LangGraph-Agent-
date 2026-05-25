"""LangGraph Agent 编排入口。"""

from langgraph.graph import END, StateGraph

from app.agent.nodes import (
    analyze_result,
    execute_sql,
    generate_sql,
    recommend_chart_node,
    retrieve_schema,
    understand_question,
    validate_sql,
)
from app.agent.state import AgentState


def build_graph():
    """构建自然语言数据分析 Agent 工作流。"""
    graph = StateGraph(AgentState)

    graph.add_node("understand_question", understand_question)
    graph.add_node("retrieve_schema", retrieve_schema)
    graph.add_node("generate_sql", generate_sql)
    graph.add_node("validate_sql", validate_sql)
    graph.add_node("execute_sql", execute_sql)
    graph.add_node("analyze_result", analyze_result)
    graph.add_node("recommend_chart", recommend_chart_node)

    graph.set_entry_point("understand_question")
    graph.add_edge("understand_question", "retrieve_schema")
    graph.add_edge("retrieve_schema", "generate_sql")
    graph.add_edge("generate_sql", "validate_sql")
    graph.add_edge("validate_sql", "execute_sql")
    graph.add_edge("execute_sql", "analyze_result")
    graph.add_edge("analyze_result", "recommend_chart")
    graph.add_edge("recommend_chart", END)

    return graph.compile()


analysis_graph = build_graph()
