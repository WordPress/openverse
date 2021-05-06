FROM python:3.9

ENV PYTHONBUFFERED 1

RUN groupadd --system supervisord && useradd --system --gid supervisord supervisord

RUN apt-get update \
    && apt-get install -y supervisor \
    && mkdir -p /var/log/supervisord/ \
    && chown -R supervisord:supervisord /var/log/supervisord

# Install Python dependency management tools
RUN pip install --upgrade pip \
    && pip install --upgrade setuptools \
    && pip install --upgrade pipenv

# Copy all files into the container
COPY . /ingestion_server/
WORKDIR /ingestion_server
RUN chown -R supervisord:supervisord /ingestion_server
ENV PYTHONPATH=$PYTHONPATH:/ingestion_server/

# Install the dependencies system-wide
# TODO: Use build args to avoid installing dev dependencies in production
RUN pipenv install --deploy --system --dev
USER supervisord
EXPOSE 8001
CMD ["supervisord", "-c", "/ingestion_server/config/supervisord.conf"]
