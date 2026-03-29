import streamlit as st


st.set_page_config(
    page_title="Churn Ops Platform Ops Console",
    page_icon="O",
    layout="wide",
)


if "backend_url" not in st.session_state:
    st.session_state.backend_url = "http://127.0.0.1:8000"


st.title("Churn Ops Platform Ops Console")
st.caption("Operational UI for monitoring, scoring, retraining, promotion, and historical replay.")

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

- `Overview` for health and monitoring
- `Scoring Lab` for live and historical scoring
- `Batch Ops` for batch upload and job tracking
- `Model Registry` for viewing artifacts and promoting challengers
- `Retraining` for challenger creation from uploaded labeled data

This UI is intentionally richer than the simple demo app, but it still stays lightweight and local-first.
"""
)
