FROM python:3.7

ENV PYTHONBUFFERED 1

RUN mkdir /ingestion_server
WORKDIR /ingestion_server
ADD requirements.txt /ingestion_server/
RUN pip install -r requirements.txt
RUN pip install gunicorn

# Install supervisord (still requires Python 2.7 in 2018 :( )
RUN apt-get update
RUN apt-get install -y python-pip
RUN pip2 install supervisor
RUN useradd -m supervisord
RUN mkdir -p /var/log/supervisord
RUN chown -R supervisord /var/log/supervisord
USER supervisord

COPY config/ /ingestion_server/config
COPY . /ingestion_server/
ENV PYTHONPATH=$PYTHONPATH:/ingestion_server/
EXPOSE 8001
CMD ["supervisord", "-c", "/ingestion_server/config/supervisord.conf"]
