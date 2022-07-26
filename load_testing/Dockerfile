FROM python:3.10-slim

RUN apt-get update && apt-get install -y wamerican apache2-utils gnupg2

# See https://github.com/grafana/k6#linux
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
RUN echo "deb https://dl.k6.io/deb stable main" | tee /etc/apt/sources.list.d/k6.list
RUN apt-get update && apt-get install k6

WORKDIR /app
