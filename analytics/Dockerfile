FROM python:3.9

ENV PYTHONBUFFERED 1

# Install librdkafka, a dependency for confluent-kafka
RUN wget https://github.com/edenhill/librdkafka/archive/v1.6.1.tar.gz \
    && tar xvzf v1.6.1.tar.gz  \
    && cd librdkafka-1.6.1/  \
    && ./configure  \
    && make && make install && ldconfig

ENV PYTHONPATH=$PYTHONPATH:/analytics

WORKDIR /analytics

# Install Python dependency management tools
RUN pip install --upgrade pip \
    && pip install --upgrade setuptools \
    && pip install --upgrade pipenv

# Copy the Pipenv files into the container
COPY Pipfile Pipfile.lock /analytics/

# Install the dependencies system-wide
# TODO: Use build args to avoid installing dev dependencies in production
RUN pipenv install --deploy --system --dev

EXPOSE 8090

CMD ["gunicorn"]
