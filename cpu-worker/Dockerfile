FROM python:3.11-slim
RUN pip install psycopg2-binary pillow minio
COPY worker.py /worker.py
CMD ["python", "/worker.py"]
