"""SQL 安全校验和执行工具。"""

import re
from typing import Any

from app.core.config import settings
from app.core.database import fetch_all, rows_to_columns


DANGEROUS_KEYWORDS = (
    "DELETE",
    "UPDATE",
    "INSERT",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "REPLACE",
    "GRANT",
    "REVOKE",
    "EXEC",
    "MERGE",
    "CALL",
)

COMMENT_TOKENS = ("--", "#", "/*", "*/")


class SQLValidationError(ValueError):
    """SQL 安全校验失败时抛出的业务异常。"""


def normalize_sql(sql: str) -> str:
    """清理大模型输出中的 Markdown 标记和多余空白。"""
    cleaned = sql.strip()
    cleaned = re.sub(r"^```(?:sql)?", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    return cleaned.strip().rstrip(";").strip()


def validate_select_sql(sql: str, default_limit: int | None = None) -> str:
    """校验 SQL 是否安全，并在缺少 LIMIT 时自动补充限制。"""
    limit = default_limit or settings.sql_default_limit
    cleaned = normalize_sql(sql)

    if not cleaned:
        raise SQLValidationError("SQL 安全校验失败：SQL 不能为空")

    # 禁止多语句执行，避免 SELECT 后拼接 DROP 等危险操作。
    if ";" in cleaned:
        raise SQLValidationError("SQL 安全校验失败：禁止执行多条 SQL 语句")

    upper_sql = cleaned.upper()

    if any(token in cleaned for token in COMMENT_TOKENS):
        raise SQLValidationError("SQL 安全校验失败：禁止使用 SQL 注释")

    if not re.match(r"^\s*SELECT\b", upper_sql):
        raise SQLValidationError("SQL 安全校验失败：只允许 SELECT 查询")

    for keyword in DANGEROUS_KEYWORDS:
        if re.search(rf"\b{keyword}\b", upper_sql):
            raise SQLValidationError(f"SQL 安全校验失败：禁止使用危险关键字 {keyword}")

    if not re.search(r"\bLIMIT\b", upper_sql):
        cleaned = f"{cleaned} LIMIT {limit}"

    return cleaned


def execute_safe_select(sql: str) -> tuple[list[dict[str, Any]], list[str], str | None]:
    """执行已经通过安全校验的 SELECT 查询。"""
    try:
        rows = fetch_all(sql)
        return rows, rows_to_columns(rows), None
    except RuntimeError as exc:
        return [], [], str(exc)
