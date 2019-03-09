FROM python:3.7

ENV PYTHONBUFFERED 1

RUN mkdir /cccatalog-api \
    && mkdir -p /var/log/cccatalog-api/cccatalog-api.log

WORKDIR /cccatalog-api

# Install Python dependency management tools
RUN pip install --upgrade pip \
    && pip install --upgrade setuptools \
    && pip install --upgrade pipenv

# Copy the Pipenv files into the container
COPY Pipfile /cccatalog-api/
COPY Pipfile.lock /cccatalog-api/

# Install the dependencies system-wide
# TODO: Use build args to avoid installing dev dependencies in production
RUN pipenv install --deploy --system --dev
