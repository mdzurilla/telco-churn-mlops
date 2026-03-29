# Simple Streamlit UI

This is a minimal Streamlit frontend for the FastAPI backend.

## Pages

- `Single Scoring`
- `Batch Scoring`

## Run

From the project root:

```powershell
pip install streamlit
.\.venv\Scripts\streamlit.exe run streamlit_ui/simple/app.py
```

Make sure the FastAPI backend is already running, for example:

```powershell
.\.venv\Scripts\uvicorn.exe app.main:app --reload
```
