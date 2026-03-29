import streamlit as st

from common import csv_preview, display_response, get_json, post_file


st.title("Batch Ops")
st.caption("Create and inspect batch scoring jobs.")

uploaded_file = st.file_uploader("Upload Batch CSV", type=["csv"])
if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    st.subheader("Preview")
    st.dataframe(csv_preview(file_bytes).head(10), use_container_width=True)

    if st.button("Create Batch Job", type="primary"):
        status_code, response = post_file(
            "/v1/batch-score",
            file_name=uploaded_file.name,
            file_bytes=file_bytes,
        )
        display_response(status_code, response)
        if status_code == 202 and "job_id" in response:
            st.session_state["ops_batch_job_id"] = response["job_id"]

st.divider()
job_id = st.text_input("Job ID", value=st.session_state.get("ops_batch_job_id", ""))

if st.button("Fetch Job Status"):
    if not job_id.strip():
        st.error("Enter a job ID.")
    else:
        status_code, response = get_json(f"/v1/jobs/{job_id.strip()}")
        display_response(status_code, response)
        if status_code == 200 and response.get("download_url"):
            st.info(f"Download output at: {response['download_url']}")
