from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import uuid, datetime, sqlite3, os

DB_FILE = os.getenv("DB_FILE", "/app/data/nexus.db")
os.makedirs("/app/data", exist_ok=True)

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
conn.execute(
    "CREATE TABLE IF NOT EXISTS jobs "
    "(id TEXT PRIMARY KEY, prompt TEXT, status TEXT, created_at TEXT)"
)

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!doctype html><title>Nexus Phase-A</title>
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
    conn.execute(
        "INSERT INTO jobs VALUES (?, ?, ?, ?)",
        (job_id, prompt, "queued", datetime.datetime.utcnow().isoformat())
    )
    conn.commit()
    return {"job_id": job_id, "prompt": prompt, "status": "queued"}

@app.get("/gallery")
def gallery():
    rows = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC").fetchall()
    return {"jobs": [{"id": r[0], "prompt": r[1], "status": r[2]} for r in rows]}

@app.get("/health")
def health():
    return {"status": "ok"}
