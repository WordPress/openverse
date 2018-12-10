FROM python:3.7

ENV PYTHONBUFFERED 1

RUN mkdir /es_syncer
WORKDIR /es_syncer
ADD requirements.txt /es_syncer/
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

COPY config/ /es_syncer/config
COPY . /es_syncer/
ENV PYTHONPATH=$PYTHONPATH:/es_syncer/
EXPOSE 8001
CMD ["supervisord", "-c", "/es_syncer/config/supervisord.conf"]
