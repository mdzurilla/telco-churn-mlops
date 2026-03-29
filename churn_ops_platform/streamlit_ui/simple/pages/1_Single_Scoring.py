import streamlit as st

from common import display_response, post_json, render_payload_form


st.title("Single Scoring")
st.caption("Score one customer payload against the current serving model or one archived artifact.")

mode = st.radio(
    "Scoring Mode",
    options=["Current Serving Model", "Archived Model"],
    horizontal=True,
)

payload = render_payload_form("single")

artifact_id = ""
if mode == "Archived Model":
    artifact_id = st.text_input(
        "Archived Artifact ID",
        help="Example: artifact_2026-03-29T18-03-34Z_9103c0dd",
    ).strip()

if st.button("Run Score", type="primary"):
    if mode == "Archived Model":
        if not artifact_id:
            st.error("Artifact ID is required for archived scoring.")
        else:
            status_code, response = post_json(f"/v1/score/historical/{artifact_id}", payload)
            display_response(status_code, response)
    else:
        status_code, response = post_json("/v1/score", payload)
        display_response(status_code, response)
