from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import numpy as np

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        #"http://localhost:5173",   # For local testing
        "https://www.vizgiri.com", # Frontend production domain
        "https://vizgiri.com"      # Optional, if users access without www
    ],
    allow_methods=["*"],  # Allow GET, POST, etc.
    allow_headers=["*"],  # Allow headers like Content-Type
)

# Allow local dev + eventual frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://vizgiri.com", "https://www.vizgiri.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    df = df.replace({np.nan: None})
    dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
    head = df.head(10).to_dict(orient="records")
    numeric_summary = {}
    for col in df.select_dtypes(include=["number"]).columns:
        s = df[col].describe().to_dict()
        numeric_summary[col] = {k: (float(v) if pd.notna(v) else None) for k, v in s.items()}
    return {"columns": numeric_summary, "head": head, "dtypes": dtypes}
