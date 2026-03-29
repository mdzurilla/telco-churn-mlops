import pandas as pd
import streamlit as st

from common import csv_preview, display_response, post_file


st.title("Retraining")
st.caption("Upload labeled data to create a challenger artifact for the current `v1` HGB model.")

uploaded_file = st.file_uploader("Upload Labeled Training CSV", type=["csv"])

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    preview_df = csv_preview(file_bytes)
    st.subheader("Preview")
    st.dataframe(preview_df.head(10), use_container_width=True)

    if "Churn" not in preview_df.columns:
        st.error("The uploaded dataset must include the `Churn` target column.")
    else:
        st.info("The retraining flow expects a labeled dataset with the `Churn` column present.")

        if st.button("Create Challenger", type="primary"):
            status_code, response = post_file(
                "/v1/training/retrain",
                file_name=uploaded_file.name,
                file_bytes=file_bytes,
            )
            if status_code == 200:
                st.success("Challenger artifact created.")
                top1, top2, top3 = st.columns(3)
                top1.metric("Artifact ID", response["artifact_id"])
                top2.metric("Threshold", response["threshold"])
                top3.metric("Rows Received", response["rows_received"])

                metrics_df = pd.DataFrame(
                    [
                        {"metric": key, "value": value}
                        for key, value in response["challenger_metrics"].items()
                    ]
                )
                st.subheader("Challenger Metrics")
                st.dataframe(metrics_df, use_container_width=True)

                comparison_df = pd.DataFrame(
                    {
                        "metric": list(response["comparison_to_serving"]["serving"].keys()),
                        "serving": list(response["comparison_to_serving"]["serving"].values()),
                        "challenger": list(response["comparison_to_serving"]["challenger"].values()),
                    }
                )
                st.subheader("Serving vs Challenger")
                st.dataframe(comparison_df, use_container_width=True)
                st.json(response)
            else:
                display_response(status_code, response)
