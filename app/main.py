"""FastAPI 应用入口。"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用实例。"""
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="基于 LangGraph 的智能数据分析 Agent 系统",
    )

    # 允许 Streamlit 前端和本地调试环境跨域访问 API。
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册系统健康检查、自然语言分析和历史记录接口。
    app.include_router(router)
    return app


app = create_app()
