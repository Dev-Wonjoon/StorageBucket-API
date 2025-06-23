FROM python:3.12-slim

WORKDIR /app

# ffmpeg 설치
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

VOLUME ["/app"]

CMD ["uvicorn", "application:app", "--host", "0.0.0.0", "--port", "8000"]