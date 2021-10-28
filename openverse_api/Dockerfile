FROM realies/audiowaveform:latest AS awf

RUN ldd /usr/local/bin/audiowaveform | tr -s '[:blank:]' '\n' | grep '^/' | \
    xargs -I % sh -c 'mkdir -p $(dirname deps%); cp % deps%;'

FROM python:3.10 AS api

ENV PYTHONBUFFERED 1

RUN apt-get update \
    && apt-get install -y libexempi8 \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /var/log/openverse_api/openverse_api.log

ADD catalog/api/utils/fonts/SourceSansPro-Bold.ttf /usr/share/fonts/truetype/SourceSansPro-Bold.ttf

WORKDIR /openverse_api

# Install Python dependency management tools
RUN pip install --upgrade pip \
    && pip install --upgrade setuptools \
    && pip install --upgrade pipenv

# Copy the Pipenv files into the container
COPY Pipfile Pipfile.lock /openverse_api/

# Install the dependencies system-wide
# TODO: Use build args to avoid installing dev dependencies in production
RUN pipenv install --deploy --system --dev

COPY --from=awf /deps /
COPY --from=awf /usr/local/bin/audiowaveform /usr/local/bin

EXPOSE 8000

ENTRYPOINT ["./run.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
