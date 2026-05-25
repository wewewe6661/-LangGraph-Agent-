"""根据查询结果推荐图表类型。"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any


DATE_KEYWORDS = ("date", "day", "month", "日期", "月份", "时间")
NUMERIC_KEYWORDS = ("amount", "count", "quantity", "sales", "total", "rate", "销售额", "订单量", "数量", "占比")
CATEGORY_KEYWORDS = ("city", "category", "product", "channel", "level", "城市", "类别", "商品", "渠道")


def is_number(value: Any) -> bool:
    """判断字段值是否为数值类型。"""
    return isinstance(value, (int, float, Decimal)) and not isinstance(value, bool)


def looks_like_date(column: str, value: Any) -> bool:
    """根据字段名和值判断是否适合作为时间轴。"""
    lower_column = column.lower()
    return isinstance(value, (date, datetime)) or any(keyword in lower_column for keyword in DATE_KEYWORDS)


def recommend_chart(rows: list[dict[str, Any]], question: str = "") -> dict[str, Any]:
    """根据结果字段类型和用户问题推荐折线图、柱状图、饼图或表格。"""
    if not rows:
        return {"chart_type": "table", "x": None, "y": None, "title": "暂无可视化数据"}

    columns = list(rows[0].keys())
    sample = rows[0]
    numeric_columns = [column for column in columns if is_number(sample.get(column))]
    date_columns = [column for column in columns if looks_like_date(column, sample.get(column))]
    category_columns = [column for column in columns if column not in numeric_columns]
    question_text = question.lower()

    if date_columns and numeric_columns:
        x = date_columns[0]
        y = numeric_columns[0]
        return {"chart_type": "line", "x": x, "y": y, "title": f"{x} 与 {y} 趋势"}

    if "占比" in question or "比例" in question or "pie" in question_text:
        if category_columns and numeric_columns and len(rows) <= 10:
            return {
                "chart_type": "pie",
                "x": category_columns[0],
                "y": numeric_columns[0],
                "title": f"按 {category_columns[0]} 的占比",
            }

    if category_columns and numeric_columns:
        category = _pick_category_column(category_columns)
        number = _pick_numeric_column(numeric_columns)
        if len(rows) <= 8 and ("占比" in question or "比例" in question):
            chart_type = "pie"
        else:
            chart_type = "bar"
        return {"chart_type": chart_type, "x": category, "y": number, "title": f"{category} 与 {number} 对比"}

    return {"chart_type": "table", "x": None, "y": None, "title": "查询结果表格"}


def _pick_category_column(columns: list[str]) -> str:
    """优先选择城市、品类、渠道等业务维度字段。"""
    for column in columns:
        if any(keyword in column.lower() for keyword in CATEGORY_KEYWORDS):
            return column
    return columns[0]


def _pick_numeric_column(columns: list[str]) -> str:
    """优先选择销售额、订单量等核心指标字段。"""
    for column in columns:
        if any(keyword in column.lower() for keyword in NUMERIC_KEYWORDS):
            return column
    return columns[0]
