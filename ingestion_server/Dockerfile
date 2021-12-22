FROM python:3.9

ENV PYTHONBUFFERED 1

RUN groupadd --system supervisord \
    && useradd --system --gid supervisord supervisord

RUN apt-get update \
    && apt-get install -y supervisor \
    && mkdir -p /var/log/supervisord/ \
    && chown -R supervisord:supervisord /var/log/supervisord \
    && mkdir /worker_state \
    && chown -R supervisord:supervisord /worker_state

ENV PYTHONPATH=$PYTHONPATH:/ingestion_server/
# TLDEXTRACT fails to cache in /home/supervisord, set its cache to /tmp instead
ENV TLDEXTRACT_CACHE=/tmp/python-tldextract

WORKDIR /ingestion_server

# Install Python dependency management tools
RUN pip install --upgrade pip \
    && pip install --upgrade setuptools \
    && pip install --upgrade pipenv

# Copy the Pipenv files into the container
COPY Pipfile Pipfile.lock /ingestion_server/

# Install the dependencies system-wide
# TODO: Use build args to avoid installing dev dependencies in production
RUN pipenv install --deploy --system --dev

USER supervisord

EXPOSE 8001

CMD ["supervisord", "-c", "/ingestion_server/config/supervisord.conf"]
