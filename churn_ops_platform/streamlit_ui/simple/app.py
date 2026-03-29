import streamlit as st


st.set_page_config(
    page_title="Churn Ops Platform",
    page_icon="C",
    layout="wide",
)


if "backend_url" not in st.session_state:
    st.session_state.backend_url = "http://127.0.0.1:8000"


st.title("Churn Ops Platform")
st.caption("Simple Streamlit frontend for single and batch scoring against the FastAPI backend.")

with st.sidebar:
    st.header("Backend")
    st.session_state.backend_url = st.text_input(
        "API Base URL",
        value=st.session_state.backend_url,
        help="Example: http://127.0.0.1:8000",
    ).rstrip("/")

st.markdown(
    """
Use the pages in the sidebar:

- `Single Scoring` for one customer payload
- `Batch Scoring` for CSV upload and job tracking

This UI is intentionally simple and portfolio-friendly. It focuses on guided input instead of heavy dashboards.
"""
)
