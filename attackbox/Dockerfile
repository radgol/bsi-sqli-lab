FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl mariadb-client iputils-ping netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /lab

CMD ["sh", "-c", "sleep infinity"]
