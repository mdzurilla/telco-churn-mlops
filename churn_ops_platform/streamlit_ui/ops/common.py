import json
from io import BytesIO
from urllib import error, request

import pandas as pd
import streamlit as st


YES_NO = ["Yes", "No"]
GENDERS = ["Male", "Female"]
SENIOR_CITIZEN = [0, 1]
MULTIPLE_LINES = ["Yes", "No", "No phone service"]
INTERNET_SERVICE = ["DSL", "Fiber optic", "No"]
INTERNET_ADDON = ["Yes", "No", "No internet service"]
CONTRACT = ["Month-to-month", "One year", "Two year"]
PAYMENT_METHOD = [
    "Electronic check",
    "Mailed check",
    "Bank transfer (automatic)",
    "Credit card (automatic)",
]


def get_backend_url() -> str:
    return st.session_state.get("backend_url", "http://127.0.0.1:8000").rstrip("/")


def post_json(path: str, payload: dict) -> tuple[int, dict]:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url=f"{get_backend_url()}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    return _send_request(req)


def get_json(path: str) -> tuple[int, dict]:
    req = request.Request(url=f"{get_backend_url()}{path}", method="GET")
    return _send_request(req)


def post_file(path: str, *, file_name: str, file_bytes: bytes) -> tuple[int, dict]:
    boundary = "----StreamlitBoundary7MA4YWxkTrZu0gW"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{file_name}"\r\n'
        "Content-Type: text/csv\r\n\r\n"
    ).encode("utf-8") + file_bytes + f"\r\n--{boundary}--\r\n".encode("utf-8")

    req = request.Request(
        url=f"{get_backend_url()}{path}",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    return _send_request(req)


def _send_request(req: request.Request) -> tuple[int, dict]:
    try:
        with request.urlopen(req) as response:
            payload = response.read().decode("utf-8")
            return response.status, json.loads(payload) if payload else {}
    except error.HTTPError as exc:
        payload = exc.read().decode("utf-8")
        try:
            return exc.code, json.loads(payload) if payload else {"detail": str(exc)}
        except json.JSONDecodeError:
            return exc.code, {"detail": payload or str(exc)}
    except error.URLError as exc:
        return 0, {"detail": f"Could not reach backend: {exc.reason}"}


def display_response(status_code: int, payload: dict) -> None:
    if 200 <= status_code < 300:
        st.success(f"Request succeeded with status {status_code}.")
        st.json(payload)
    else:
        st.error(f"Request failed with status {status_code}.")
        st.json(payload)


def render_payload_form(prefix: str) -> dict:
    st.subheader("Customer Attributes")
    customer_id = st.text_input("Customer ID", value="CUST-001", key=f"{prefix}_customer_id")

    col1, col2, col3 = st.columns(3)
    with col1:
        gender = st.selectbox("Gender", GENDERS, key=f"{prefix}_gender")
        senior_citizen = st.selectbox("Senior Citizen", SENIOR_CITIZEN, key=f"{prefix}_senior")
        partner = st.selectbox("Partner", YES_NO, key=f"{prefix}_partner")
        dependents = st.selectbox("Dependents", YES_NO, key=f"{prefix}_dependents")
    with col2:
        tenure = st.number_input("Tenure", min_value=0, max_value=72, value=24, key=f"{prefix}_tenure")
        phone_service = st.selectbox("Phone Service", YES_NO, key=f"{prefix}_phone_service")
        multiple_lines = st.selectbox("Multiple Lines", MULTIPLE_LINES, key=f"{prefix}_multiple_lines")
        internet_service = st.selectbox("Internet Service", INTERNET_SERVICE, key=f"{prefix}_internet_service")
    with col3:
        contract = st.selectbox("Contract", CONTRACT, key=f"{prefix}_contract")
        paperless_billing = st.selectbox("Paperless Billing", YES_NO, key=f"{prefix}_paperless_billing")
        payment_method = st.selectbox("Payment Method", PAYMENT_METHOD, key=f"{prefix}_payment_method")

    st.subheader("Add-On Services")
    col4, col5, col6 = st.columns(3)
    with col4:
        online_security = st.selectbox("Online Security", INTERNET_ADDON, key=f"{prefix}_online_security")
        online_backup = st.selectbox("Online Backup", INTERNET_ADDON, key=f"{prefix}_online_backup")
    with col5:
        device_protection = st.selectbox("Device Protection", INTERNET_ADDON, key=f"{prefix}_device_protection")
        tech_support = st.selectbox("Tech Support", INTERNET_ADDON, key=f"{prefix}_tech_support")
    with col6:
        streaming_tv = st.selectbox("Streaming TV", INTERNET_ADDON, key=f"{prefix}_streaming_tv")
        streaming_movies = st.selectbox("Streaming Movies", INTERNET_ADDON, key=f"{prefix}_streaming_movies")

    st.subheader("Charges")
    col7, col8 = st.columns(2)
    with col7:
        monthly_charges = st.number_input(
            "Monthly Charges",
            min_value=0.0,
            value=70.0,
            step=0.1,
            key=f"{prefix}_monthly_charges",
        )
    with col8:
        total_charges = st.number_input(
            "Total Charges",
            min_value=0.0,
            value=1680.0,
            step=0.1,
            key=f"{prefix}_total_charges",
        )

    return {
        "customerID": customer_id,
        "gender": gender,
        "SeniorCitizen": senior_citizen,
        "Partner": partner,
        "Dependents": dependents,
        "tenure": int(tenure),
        "PhoneService": phone_service,
        "MultipleLines": multiple_lines,
        "InternetService": internet_service,
        "OnlineSecurity": online_security,
        "OnlineBackup": online_backup,
        "DeviceProtection": device_protection,
        "TechSupport": tech_support,
        "StreamingTV": streaming_tv,
        "StreamingMovies": streaming_movies,
        "Contract": contract,
        "PaperlessBilling": paperless_billing,
        "PaymentMethod": payment_method,
        "MonthlyCharges": float(monthly_charges),
        "TotalCharges": float(total_charges),
    }


def csv_preview(file_bytes: bytes) -> pd.DataFrame:
    return pd.read_csv(BytesIO(file_bytes))
