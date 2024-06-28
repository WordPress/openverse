# syntax=docker/dockerfile:1

######
# K6 #
######

FROM docker.io/grafana/k6:v0.51.0 as k6

###############
# Observation #
###############

FROM docker.io/python:3.11-slim AS lt

LABEL org.opencontainers.image.source="https://github.com/WordPress/openverse"

# Copy `k6` binary
COPY --from=k6 /usr/bin/k6 /usr/bin/k6

# Install system packages needed by the project
# - wamerican: American words dictionary
# - apache2-utils: Apache HTTP server benchmarking tool `ab`
# - gnupg2: TODO why?
RUN apt-get update \
  && apt-get install -yqq --no-install-recommends \
    wamerican \
    apache2-utils gnupg2 \
  && apt-get autoremove -y \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENTRYPOINT ["k6"]
