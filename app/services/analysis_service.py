"""数据分析业务服务模块。"""

from app.agent.graph import analysis_graph
from app.api.schemas import AnalyzeResponse, ChartConfig, QueryHistoryItem
from app.core.database import fetch_history, insert_analysis_log


class AnalysisService:
    """封装 API 层与 LangGraph Agent 之间的业务调用。"""

    def analyze(self, question: str) -> AnalyzeResponse:
        """执行一次自然语言数据分析请求，并保存分析日志。"""
        final_state = analysis_graph.invoke({"question": question})
        chart_config = final_state.get("chart_config") or {"chart_type": "table", "title": "查询结果"}

        response = AnalyzeResponse(
            question=question,
            intent=final_state.get("intent", ""),
            generated_sql=final_state.get("generated_sql", ""),
            validated_sql=final_state.get("validated_sql", ""),
            columns=final_state.get("columns", []),
            rows=final_state.get("query_result", []),
            analysis=final_state.get("analysis", ""),
            chart=ChartConfig(**chart_config),
            error=final_state.get("error"),
        )

        if not response.error and response.validated_sql:
            insert_analysis_log(
                question=question,
                generated_sql=response.validated_sql,
                analysis=response.analysis,
                chart_type=response.chart.chart_type,
            )

        return response

    def get_history(self, limit: int = 20) -> list[QueryHistoryItem]:
        """读取历史查询记录。"""
        rows = fetch_history(limit=limit)
        return [QueryHistoryItem(**row) for row in rows]
