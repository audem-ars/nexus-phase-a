from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os, psycopg2, minio

app = FastAPI()

# mount static files (JS/CSS/images)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!doctype html>
    <title>Nexus Phase-A</title>
    <h1>Prompt Uploader</h1>
    <form action="/generate" method="post">
      Prompt: <input name="prompt"><br>
      <input type="submit">
    </form>
    <a href="/gallery">Gallery</a>
    """

# TODO: /generate and /gallery endpoints
