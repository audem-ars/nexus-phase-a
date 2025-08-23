import os, psycopg2, minio, uuid, io, time
from PIL import Image, ImageDraw, ImageFont

DB_URL   = os.getenv("DATABASE_URL")
MINIO_EP = os.getenv("MINIO_ENDPOINT", "minio:9000")

minio_cli = minio.Minio(MINIO_EP, "minioadmin", "minioadmin", secure=False)
try: minio_cli.make_bucket("results")
except: pass

conn = psycopg2.connect(DB_URL)

def process_job(job_id, prompt):
    # basic CPU “generation”: draw colored gradient + text
    img = Image.new("RGB", (512,512), color="black")
    draw = ImageDraw.Draw(img)
    draw.rectangle([0,0,512,512], fill="cyan")
    draw.text((10,240), prompt[:40], fill="black")
    buf = io.BytesIO(); img.save(buf, "PNG"); buf.seek(0)
    minio_cli.put_object("results", f"{job_id}.png", buf, len(buf.getvalue()))

while True:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, prompt FROM jobs
            WHERE status='queued' LIMIT 1 FOR UPDATE SKIP LOCKED
        """)
        row = cur.fetchone()
        if not row:
            time.sleep(2)
            continue
        job_id, prompt = row
        cur.execute("UPDATE jobs SET status='processing' WHERE id=%s", (job_id,))
        conn.commit()

    process_job(job_id, prompt)

    with conn.cursor() as cur:
        cur.execute("UPDATE jobs SET status='done' WHERE id=%s", (job_id,))
        conn.commit()
