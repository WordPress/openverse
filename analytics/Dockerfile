FROM python:3.7

ENV PYTHONBUFFERED 1
ENV PYTHONPATH .
WORKDIR /analytics

# Install Python dependency management tools
RUN pip install --upgrade pip \
    && pip install --upgrade setuptools \
    && pip install --upgrade pipenv

# Copy the Pipenv files into the container
COPY . /analytics/

RUN pipenv install
EXPOSE 8090
ENTRYPOINT pipenv run gunicorn -b '0.0.0.0:8090' server:api
