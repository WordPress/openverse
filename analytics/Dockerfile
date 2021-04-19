FROM python:3.9

ENV PYTHONBUFFERED 1
ENV PYTHONPATH .
WORKDIR /analytics

# Install librdkafka, a dependency for confluent-kafka
RUN wget https://github.com/edenhill/librdkafka/archive/v1.6.1.tar.gz \
    && tar xvzf v1.6.1.tar.gz  \
    && cd librdkafka-1.6.1/  \
    && ./configure  \
    && make && make install && ldconfig

# Install Python dependency management tools
RUN pip install --upgrade pip \
    && pip install --upgrade setuptools \
    && pip install --upgrade pipenv

# Copy the Pipenv files into the container
COPY . /analytics/

RUN pipenv install
EXPOSE 8090
ENTRYPOINT pipenv run gunicorn -b '0.0.0.0:8090' server:api
