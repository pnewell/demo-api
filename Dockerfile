FROM python:3.12-slim

ARG APP_VERSION=v1
ENV APP_VERSION=${APP_VERSION}

WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
