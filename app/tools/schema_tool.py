"""业务数据库 Schema 描述工具。"""

from typing import Any


BUSINESS_SCHEMA: dict[str, dict[str, Any]] = {
    "customers": {
        "description": "客户表，保存客户基础信息，可用于城市、年龄、会员等级等维度分析。",
        "columns": {
            "id": "客户ID，主键",
            "customer_name": "客户姓名",
            "city": "客户所在城市",
            "gender": "性别",
            "age": "年龄",
            "member_level": "会员等级，例如普通会员、白银会员、黄金会员、铂金会员",
            "registered_at": "注册日期",
            "created_at": "记录创建时间",
        },
    },
    "products": {
        "description": "商品表，保存商品名称、类别、价格和成本。",
        "columns": {
            "id": "商品ID，主键",
            "product_name": "商品名称",
            "category": "商品类别，例如数码电子、家用电器、服饰鞋包、美妆个护、食品饮料",
            "price": "商品单价",
            "cost": "商品成本",
            "created_at": "记录创建时间",
        },
    },
    "orders": {
        "description": "订单事实表，保存销售订单明细，是销售额、订单量、趋势、排行分析的核心表。",
        "columns": {
            "id": "订单ID，主键",
            "order_no": "订单编号",
            "customer_id": "客户ID，关联 customers.id",
            "product_id": "商品ID，关联 products.id",
            "city": "下单城市",
            "quantity": "购买数量",
            "total_amount": "订单总金额，销售额分析优先使用该字段",
            "order_status": "订单状态：paid 已支付，cancelled 已取消，refunded 已退款。统计销售额时默认只统计 paid",
            "channel": "下单渠道，例如 APP、小程序、官网、直播间",
            "order_date": "下单日期，趋势分析优先使用该字段",
            "created_at": "记录创建时间",
        },
    },
    "analysis_logs": {
        "description": "分析日志表，仅用于展示历史查询，不参与业务分析 SQL 生成。",
        "columns": {
            "id": "日志ID",
            "question": "用户自然语言问题",
            "generated_sql": "生成并校验后的 SQL",
            "analysis": "业务分析结论",
            "chart_type": "推荐图表类型",
            "created_at": "日志创建时间",
        },
    },
}

RELATIONSHIPS = [
    "orders.customer_id = customers.id",
    "orders.product_id = products.id",
]


def format_schema_for_prompt() -> str:
    """把结构化 Schema 转换为适合放进 Prompt 的文本。"""
    lines: list[str] = ["数据库 Schema 信息如下："]

    for table_name, table_info in BUSINESS_SCHEMA.items():
        lines.append(f"\n表名：{table_name}")
        lines.append(f"表说明：{table_info['description']}")
        lines.append("字段：")
        for column_name, column_desc in table_info["columns"].items():
            lines.append(f"- {column_name}: {column_desc}")

    lines.append("\n表关联关系：")
    for relationship in RELATIONSHIPS:
        lines.append(f"- {relationship}")

    lines.append("\n业务口径：")
    lines.append("- 销售额默认使用 orders.total_amount")
    lines.append("- 订单量默认使用 COUNT(*)")
    lines.append("- 有效成交订单默认过滤 orders.order_status = 'paid'")
    lines.append("- 趋势分析默认按 orders.order_date 聚合")
    lines.append("- 商品类别分析需要关联 products 表")
    return "\n".join(lines)


def get_schema_summary() -> dict[str, Any]:
    """返回结构化 Schema，便于调试或未来扩展接口。"""
    return {
        "tables": BUSINESS_SCHEMA,
        "relationships": RELATIONSHIPS,
    }
