FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y ffmpeg openssl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ARG GENERATE_SELF_SIGNED=false

RUN if [ "$GENERATE_SELF_SIGNED" = "true" ]; then \
        echo "[build] self-signed cert creating..." \
        mkdir -p /app/certs; \
        openssl req -x509 -nodes -days 365 \
            -newkey rsa:2048 \
            -keyout /app/certs/localhost-key.pem \
            -out /app/certs/localhost.pem \
            -subj "/CN=localhost"; \
        echo "[build] cert created."; \
    fi

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT [ "/app/entrypoint.sh" ]

CMD []