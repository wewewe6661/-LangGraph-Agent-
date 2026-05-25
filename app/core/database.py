"""数据库连接和通用查询模块。"""

from collections.abc import Iterable
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings


# 全局 Engine 由 SQLAlchemy 维护连接池，供 API 和 Agent 节点复用。
engine: Engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    future=True,
)


def fetch_all(sql: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """执行查询 SQL 并返回字典列表。"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text(sql), params or {})
            return [dict(row._mapping) for row in result.fetchall()]
    except SQLAlchemyError as exc:
        raise RuntimeError(f"数据库查询失败：{exc}") from exc


def execute_write(sql: str, params: dict[str, Any] | None = None) -> None:
    """执行写入 SQL，用于保存分析日志。"""
    try:
        with engine.begin() as connection:
            connection.execute(text(sql), params or {})
    except SQLAlchemyError as exc:
        raise RuntimeError(f"数据库写入失败：{exc}") from exc


def fetch_history(limit: int = 20) -> list[dict[str, Any]]:
    """读取最近的自然语言分析历史。"""
    sql = """
    SELECT id, question, generated_sql, analysis, chart_type, created_at
    FROM analysis_logs
    ORDER BY created_at DESC
    LIMIT :limit
    """
    return fetch_all(sql, {"limit": limit})


def insert_analysis_log(
    question: str,
    generated_sql: str,
    analysis: str,
    chart_type: str,
) -> None:
    """保存一次完整的分析请求记录。"""
    sql = """
    INSERT INTO analysis_logs (question, generated_sql, analysis, chart_type)
    VALUES (:question, :generated_sql, :analysis, :chart_type)
    """
    execute_write(
        sql,
        {
            "question": question,
            "generated_sql": generated_sql,
            "analysis": analysis,
            "chart_type": chart_type,
        },
    )


def rows_to_columns(rows: Iterable[dict[str, Any]]) -> list[str]:
    """从查询结果中提取列名。"""
    for row in rows:
        return list(row.keys())
    return []
