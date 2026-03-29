import pandas as pd
import streamlit as st

from common import display_response, get_json, post_json


st.title("Model Registry")
st.caption("Inspect serving, challenger, and archive artifacts. Promote challengers into serving.")

if st.button("Load Models", type="primary"):
    status_code, payload = get_json("/v1/models")
    if status_code == 200:
        st.success("Model registry loaded.")
        for model in payload:
            st.subheader(model["model_name"])
            artifacts_df = pd.DataFrame(model["artifacts"])
            if not artifacts_df.empty:
                st.dataframe(artifacts_df, use_container_width=True)
    else:
        display_response(status_code, payload)

st.divider()
st.subheader("Promote Challenger")
model_name = st.text_input("Model Name", value="churn_hist_gradient_boosting")
artifact_id = st.text_input("Challenger Artifact ID")

if st.button("Promote Challenger"):
    if not model_name.strip() or not artifact_id.strip():
        st.error("Model name and artifact ID are both required.")
    else:
        status_code, response = post_json(
            f"/v1/models/{model_name.strip()}/promote",
            {"artifact_id": artifact_id.strip()},
        )
        display_response(status_code, response)
