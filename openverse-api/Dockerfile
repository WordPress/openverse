FROM python:3.7-stretch

ENV PYTHONBUFFERED 1

RUN apt-get update \
    && apt-get install -y libexempi3 \
    && mkdir /openverse-api \
    && mkdir -p /var/log/openverse-api/openverse-api.log

ADD catalog/api/utils/fonts/SourceSansPro-Bold.ttf /usr/share/fonts/truetype/SourceSansPro-Bold.ttf

WORKDIR /openverse-api

# Install Python dependency management tools
RUN pip install --upgrade pip \
    && pip install --upgrade setuptools \
    && pip install --upgrade pipenv

# Copy the Pipenv files into the container
COPY Pipfile /openverse-api/
COPY Pipfile.lock /openverse-api/

# Install the dependencies system-wide
# TODO: Use build args to avoid installing dev dependencies in production
RUN pipenv install --deploy --system --dev

ENTRYPOINT ["./run.sh"]
