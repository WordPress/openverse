FROM debian:11-slim as words

RUN apt-get update && apt-get install -y wamerican

FROM locustio/locust:2.9.0

COPY --from=words /usr/share/dict/american-english /usr/share/dict/american-english

RUN pip install --upgrade pipenv

COPY Pipfile .
COPY Pipfile.lock .

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --deploy --dev

ENTRYPOINT ["locust", "--headless"]
