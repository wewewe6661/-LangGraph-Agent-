"""FastAPI 路由定义模块。"""

from fastapi import APIRouter, HTTPException

from app.api.schemas import AnalyzeRequest, AnalyzeResponse, HealthResponse, QueryHistoryItem
from app.core.config import settings
from app.services.analysis_service import AnalysisService

router = APIRouter()
analysis_service = AnalysisService()


@router.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    """返回服务健康状态，供 Docker 和前端检查。"""
    return HealthResponse(status="ok", app_name=settings.app_name)


@router.post("/api/analyze", response_model=AnalyzeResponse, tags=["analysis"])
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """接收自然语言问题并触发智能数据分析流程。"""
    try:
        return analysis_service.analyze(request.question)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/api/history", response_model=list[QueryHistoryItem], tags=["analysis"])
def history(limit: int = 20) -> list[QueryHistoryItem]:
    """返回最近的自然语言分析历史记录。"""
    try:
        return analysis_service.get_history(limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
