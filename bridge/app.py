from fastapi import FastAPI, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
import psycopg2, minio, os, uuid, datetime, json

DB_URL = os.getenv("DATABASE_URL")
MINIO_CLIENT = minio.Minio(
    os.getenv("MINIO_ENDPOINT", "minio:9000"),
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

app = FastAPI()

# ensure bucket
try: MINIO_CLIENT.make_bucket("jobs")
except: pass

def db():
    return psycopg2.connect(DB_URL)

with db() as conn, conn.cursor() as cur:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id UUID PRIMARY KEY,
            prompt TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMPTZ DEFAULT now()
        );
    """)
    conn.commit()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!doctype html>
    <title>Nexus Phase-A</title>
    <h1>Generate Image (CPU placeholder)</h1>
    <form action="/generate" method="post">
      Prompt: <input name="prompt" required><br>
      <input type="submit">
    </form>
    <p><a href="/gallery">Gallery</a></p>
    """

@app.post("/generate")
def generate(prompt: str = Form(...)):
    job_id = str(uuid.uuid4())
    with db() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO jobs(id, prompt, status) VALUES(%s,%s,%s)",
            (job_id, prompt, "queued")
        )
        conn.commit()
    return RedirectResponse("/gallery", status_code=303)

@app.get("/gallery", response_class=HTMLResponse)
def gallery():
    with db() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, prompt, status, created_at FROM jobs ORDER BY created_at DESC")
        rows = cur.fetchall()
    items = "".join(
        f"<li><b>{r[1]}</b> → {r[2]} @ {r[3].strftime('%H:%M:%S')}</li>"
        for r in rows
    )
    return f"<h1>Jobs</h1><ul>{items}</ul><a href='/'>Back</a>"

@app.get("/health")
def health(): return {"status":"ok"}
