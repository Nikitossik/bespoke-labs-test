FROM python:3.12.3-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir \
    fastapi==0.115.0 \
    pydantic==2.9.2 \
    sqlalchemy==2.0.35 \
    uvicorn==0.30.6 \
    httpx==0.27.2

CMD ["bash"]