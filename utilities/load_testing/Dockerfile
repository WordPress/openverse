# syntax=docker/dockerfile:1

FROM docker.io/python:3.11-slim

# See https://github.com/grafana/k6#linux
RUN apt-get update && \
    apt-get install -y wamerican apache2-utils gnupg2 && \
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69 && \
    echo "deb https://dl.k6.io/deb stable main" | tee /etc/apt/sources.list.d/k6.list && \
    apt-get update && \
    apt-get install k6 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
