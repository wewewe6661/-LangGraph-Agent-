"""Streamlit 前端页面。"""

import os
from datetime import datetime
from typing import Any

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
DEFAULT_QUESTION = "请输入你的问题"


st.set_page_config(page_title="智能数据分析 Agent", layout="wide")


def call_analyze_api(question: str) -> dict[str, Any]:
    """调用 FastAPI 的自然语言分析接口。"""
    response = requests.post(
        f"{API_BASE_URL}/api/analyze",
        json={"question": question},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()


def init_sessions() -> None:
    """初始化左侧会话记忆。"""
    if "sessions" not in st.session_state:
        session_id = create_session_id()
        st.session_state["sessions"] = {
            session_id: {
                "title": "新会话",
                "messages": [],
                "last_result": None,
                "question": DEFAULT_QUESTION,
                "history": [],
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
        }
        st.session_state["active_session_id"] = session_id


def create_session_id() -> str:
    """生成当前浏览器会话内唯一的会话 ID。"""
    return datetime.now().strftime("%Y%m%d%H%M%S%f")


def get_active_session() -> dict[str, Any]:
    """获取当前选中的会话数据。"""
    init_sessions()
    active_session_id = st.session_state["active_session_id"]
    session = st.session_state["sessions"][active_session_id]
    session.setdefault("history", [])
    return session


def create_new_session() -> None:
    """新建一个空白分析会话。"""
    session_id = create_session_id()
    st.session_state["sessions"][session_id] = {
        "title": "新会话",
        "messages": [],
        "last_result": None,
        "question": DEFAULT_QUESTION,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    st.session_state["active_session_id"] = session_id


def delete_session(session_id: str) -> None:
    """删除一个会话，并保证删除后仍有可用会话。"""
    sessions = st.session_state["sessions"]
    if session_id in sessions:
        sessions.pop(session_id)

    if not sessions:
        create_new_session()
        return

    if st.session_state["active_session_id"] == session_id:
        st.session_state["active_session_id"] = next(reversed(sessions))


def update_session_after_analysis(question: str, result: dict[str, Any]) -> None:
    """分析完成后保存当前会话的问题、回答和结果。"""
    session = get_active_session()
    answer = result.get("analysis") or result.get("error") or "分析完成。"
    session["question"] = question
    session["last_result"] = result
    session["messages"].append({"role": "user", "content": question})
    session["messages"].append({"role": "assistant", "content": answer})
    session.setdefault("history", []).insert(
        0,
        {
            "question": question,
            "generated_sql": result.get("validated_sql") or result.get("generated_sql") or "",
            "analysis": answer,
            "chart_type": result.get("chart", {}).get("chart_type", "table"),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
    )

    if session["title"] == "新会话":
        session["title"] = question[:18] + ("..." if len(question) > 18 else "")


def render_sidebar_sessions() -> None:
    """在左侧边栏展示会话列表，并支持切换会话。"""
    with st.sidebar:
        st.header("会话记忆")

        if st.button("新建会话", use_container_width=True):
            create_new_session()
            st.rerun()

        st.divider()

        for session_id, session in reversed(list(st.session_state["sessions"].items())):
            is_active = session_id == st.session_state["active_session_id"]
            label = session["title"]
            if is_active:
                label = f"当前：{label}"

            session_col, delete_col = st.columns([0.78, 0.22])
            with session_col:
                if st.button(label, key=f"session_{session_id}", use_container_width=True):
                    st.session_state["active_session_id"] = session_id
                    st.rerun()
            with delete_col:
                if st.button("❌️", key=f"delete_{session_id}", use_container_width=True):
                    delete_session(session_id)
                    st.rerun()

            st.caption(session["created_at"])


def render_chart(rows: list[dict[str, Any]], chart: dict[str, Any]) -> None:
    """根据后端推荐的 chart_config 渲染 Plotly 图表。"""
    if not rows:
        st.info("暂无数据可展示图表。")
        return

    df = pd.DataFrame(rows)
    chart_type = chart.get("chart_type", "table")
    x = chart.get("x")
    y = chart.get("y")
    title = chart.get("title", "查询结果")

    if chart_type == "line" and x in df.columns and y in df.columns:
        fig = px.line(df, x=x, y=y, markers=True, title=title)
        st.plotly_chart(fig, use_container_width=True)
    elif chart_type == "bar" and x in df.columns and y in df.columns:
        fig = px.bar(df, x=x, y=y, title=title)
        st.plotly_chart(fig, use_container_width=True)
    elif chart_type == "pie" and x in df.columns and y in df.columns:
        fig = px.pie(df, names=x, values=y, title=title)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)


def render_analysis_panel(result: dict[str, Any]) -> None:
    """保持原有方式展示最近一次分析的完整结果。"""
    if result.get("error"):
        st.error(result["error"])

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("识别意图")
        st.code(result.get("intent") or "未识别")
    with col2:
        st.subheader("推荐图表")
        st.code(result.get("chart", {}).get("chart_type", "table"))

    st.subheader("生成 SQL")
    st.code(result.get("validated_sql") or result.get("generated_sql") or "暂无 SQL", language="sql")

    rows = result.get("rows", [])
    st.subheader("查询结果")
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info("暂无查询结果。")

    st.subheader("业务分析结论")
    st.write(result.get("analysis") or "暂无分析结论。")

    st.subheader("可视化图表")
    render_chart(rows, result.get("chart", {}))


def render_history(session: dict[str, Any]) -> None:
    """展示当前会话中独立保存的历史查询记录。"""
    st.divider()
    st.subheader("历史查询记录")
    history = session.get("history", [])
    if history:
        st.dataframe(pd.DataFrame(history), use_container_width=True)
    else:
        st.info("当前会话暂无历史查询记录。")


def main() -> None:
    """渲染智能数据分析 Agent 页面。"""
    init_sessions()
    render_sidebar_sessions()
    active_session = get_active_session()

    st.title("基于 LangGraph 的智能数据分析 Agent")
    

    question = st.text_area(
        "请输入你的业务数据问题",
        value=active_session.get("question", DEFAULT_QUESTION),
        height=100,
        placeholder="例如：最近 30 天销售额趋势怎么样？",
        key=f"question_{st.session_state['active_session_id']}",
    )

    if st.button("开始分析", type="primary", use_container_width=True):
        if not question.strip():
            st.warning("请输入问题后再开始分析。")
            return

        with st.spinner("Agent 正在分析，请稍候..."):
            try:
                result = call_analyze_api(question.strip())
                update_session_after_analysis(question.strip(), result)
            except requests.RequestException as exc:
                st.error(f"调用后端服务失败：{exc}")
                return

    active_session = get_active_session()
    result = active_session.get("last_result")
    if result:
        render_analysis_panel(result)

    render_history(active_session)


if __name__ == "__main__":
    main()
