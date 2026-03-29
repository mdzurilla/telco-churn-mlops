import streamlit as st

from common import display_response, post_json, render_payload_form


st.title("Scoring Lab")
st.caption("Run live scoring or historical scoring using an archived artifact.")

mode = st.radio(
    "Mode",
    options=["Serving Model", "Historical Archive"],
    horizontal=True,
)

payload = render_payload_form("ops_score")
artifact_id = ""

if mode == "Historical Archive":
    artifact_id = st.text_input(
        "Archived Artifact ID",
        help="Use an artifact listed in the Model Registry page.",
    ).strip()

if st.button("Score Payload", type="primary"):
    if mode == "Historical Archive":
        if not artifact_id:
            st.error("Archived scoring requires an artifact ID.")
        else:
            status_code, response = post_json(f"/v1/score/historical/{artifact_id}", payload)
            display_response(status_code, response)
    else:
        status_code, response = post_json("/v1/score", payload)
        display_response(status_code, response)
