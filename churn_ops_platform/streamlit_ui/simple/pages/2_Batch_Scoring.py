import streamlit as st

from common import display_batch_preview, display_response, get_json, post_file


st.title("Batch Scoring")
st.caption("Upload a CSV to create a batch scoring job, then inspect job status and download links.")

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    display_batch_preview(file_bytes)

    if st.button("Create Batch Job", type="primary"):
        status_code, response = post_file(
            "/v1/batch-score",
            file_name=uploaded_file.name,
            file_bytes=file_bytes,
        )
        display_response(status_code, response)
        if status_code == 202 and "job_id" in response:
            st.session_state["simple_batch_job_id"] = response["job_id"]

st.divider()
st.subheader("Track Existing Job")

job_id = st.text_input("Job ID", value=st.session_state.get("simple_batch_job_id", ""))

if st.button("Refresh Job Status"):
    if not job_id.strip():
        st.error("Enter a job ID first.")
    else:
        status_code, response = get_json(f"/v1/jobs/{job_id.strip()}")
        display_response(status_code, response)
        if status_code == 200 and response.get("download_url"):
            st.info(f"Download endpoint: {response['download_url']}")
