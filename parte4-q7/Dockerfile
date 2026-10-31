FROM python:3.14-slim

WORKDIR /app
COPY parte3-q6/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY parte2-q4 /app/parte2-q4
COPY parte3-q6 /app/parte3-q6

ARG APP_DIR=parte3-q6
WORKDIR /app/${APP_DIR}
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
