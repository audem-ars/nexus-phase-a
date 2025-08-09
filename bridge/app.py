from fastapi import FastAPI, UploadFile
from pydantic import BaseModel
import numpy as np, requests, os, uuid, io
import sqlalchemy as sa
from minio import Minio

app = FastAPI()
db = sa.create_engine("postgresql://nexus:nexuspass@postgres/nexusdb")
minio = Minio("minio:9000", "minioadmin", "minioadmin", secure=False)
bucket = "nexus-hot"

class Prompt(BaseModel):
    prompt: str

@app.post("/prompt")
def generate(p: Prompt):
    vec = np.random.randn(512).astype(np.float32)  # stub encoder
    # fake FAISS hit
    if np.random.rand() > 0.2:
        img_id = "demo"
        minio.put_object(bucket, img_id + ".webp", io.BytesIO(b"stub"), 4)
        url = minio.presigned_get_object(bucket, img_id + ".webp")
        return {"status": "hot", "url": url}
    else:
        return {"status": "fallback", "url": "http://example.com/fallback.webp"}

@app.post("/ingest")
def ingest(file: UploadFile):
    img_id = str(uuid.uuid4())
    minio.put_object(bucket, img_id + ".webp", file.file, file.size)
    return {"id": img_id}