# Ops Streamlit UI

This is the richer operational Streamlit frontend for the FastAPI backend.

## Pages

- `Overview`
- `Scoring Lab`
- `Batch Ops`
- `Model Registry`
- `Retraining`

## Run

From the project root:

```powershell
pip install streamlit
.\.venv\Scripts\streamlit.exe run streamlit_ui/ops/app.py
```

Make sure the FastAPI backend is already running:

```powershell
.\.venv\Scripts\uvicorn.exe app.main:app --reload
```
