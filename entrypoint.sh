#!/usr/bin/env bash
set -e

# certs 폴더가 있고 키·인증서 파일이 둘 다 있으면 SSL 모드
if [[ -d "/app/certs" && -f "/app/certs/localhost.pem" && -f "/app/certs/localhost-key.pem" ]]; then
  echo "[entrypoint] SSL mode is enabled; Starting in SSL mode."
  exec uvicorn application:app \
    --host 0.0.0.0 --port 443 \
    --ssl-certfile /app/certs/localhost.pem \
    --ssl-keyfile  /app/certs/localhost-key.pem
else
  echo "[entrypoint] SSL mode is disabled; Starting in non-SSL mode."
  exec uvicorn application:app \
    --host 0.0.0.0 --port ${WEB_PORT:-8000}
fi