import sqlite3, uuid, datetime, os, time
from PIL import Image, ImageDraw

DB_FILE = "/app/data/nexus.db"
conn = sqlite3.connect(DB_FILE, check_same_thread=False)

conn.execute(
    "CREATE TABLE IF NOT EXISTS jobs "
    "(id TEXT PRIMARY KEY, prompt TEXT, status TEXT, created_at TEXT)"
)

def process_job(job_id, prompt):
    img = Image.new("RGB", (512, 512), color="cyan")
    draw = ImageDraw.Draw(img)
    draw.text((10, 240), prompt[:40], fill="black")
    img.save(f"/app/data/{job_id}.png")

while True:
    with conn:
        cur = conn.execute(
            "SELECT id, prompt FROM jobs WHERE status='queued' LIMIT 1"
        )
        row = cur.fetchone()
        if not row:
            time.sleep(2)
            continue
        job_id, prompt = row
        conn.execute("UPDATE jobs SET status='processing' WHERE id=?", (job_id,))
        process_job(job_id, prompt)
        conn.execute("UPDATE jobs SET status='done' WHERE id=?", (job_id,))
