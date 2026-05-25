import pytest

from app.tools.sql_tool import SQLValidationError, validate_select_sql


def test_select_sql_is_allowed():
    sql = validate_select_sql("SELECT * FROM orders", default_limit=50)
    assert sql == "SELECT * FROM orders LIMIT 50"


def test_existing_limit_is_kept():
    sql = validate_select_sql("SELECT * FROM orders LIMIT 10", default_limit=50)
    assert sql == "SELECT * FROM orders LIMIT 10"


@pytest.mark.parametrize(
    "sql",
    [
        "DELETE FROM orders",
        "UPDATE orders SET total_amount = 0",
        "INSERT INTO orders(order_no) VALUES('x')",
        "DROP TABLE orders",
        "ALTER TABLE orders ADD COLUMN test INT",
        "TRUNCATE TABLE orders",
    ],
)
def test_dangerous_sql_is_rejected(sql):
    with pytest.raises(SQLValidationError):
        validate_select_sql(sql)


def test_multi_statement_is_rejected():
    with pytest.raises(SQLValidationError):
        validate_select_sql("SELECT * FROM orders; DROP TABLE orders")


def test_comment_is_rejected():
    with pytest.raises(SQLValidationError):
        validate_select_sql("SELECT * FROM orders -- comment")
