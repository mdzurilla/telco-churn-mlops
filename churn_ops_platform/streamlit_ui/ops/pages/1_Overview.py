import pandas as pd
import streamlit as st

from common import display_response, get_json


st.title("Overview")
st.caption("Health and monitoring summary for the current backend instance.")

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("Check Health", type="primary"):
        status_code, payload = get_json("/v1/health")
        display_response(status_code, payload)

with col2:
    if st.button("Refresh Monitoring Summary"):
        status_code, payload = get_json("/v1/monitoring/summary")
        if status_code == 200:
            st.success("Monitoring summary loaded.")
            top1, top2, top3 = st.columns(3)
            top1.metric("Total Requests", payload["total_requests"])
            top2.metric("Successful Predictions", payload["successful_predictions"])
            top3.metric(
                "Average Probability",
                payload["average_probability"] if payload["average_probability"] is not None else "n/a",
            )

            dist1, dist2, dist3 = st.columns(3)
            dist1.metric("Prediction 0", payload["prediction_distribution"]["prediction_0"])
            dist2.metric("Prediction 1", payload["prediction_distribution"]["prediction_1"])
            dist3.metric("Realtime Requests", payload["source_breakdown"]["realtime"])

            st.subheader("Daily Volume Last 7 Days")
            trend_df = pd.DataFrame(payload["daily_volume_last_7_days"])
            if not trend_df.empty:
                st.line_chart(trend_df.set_index("date"))

            st.subheader("Raw Summary")
            st.json(payload)
        else:
            display_response(status_code, payload)
