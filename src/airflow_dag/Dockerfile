FROM puckel/docker-airflow@sha256:62f9f5392c31d03a1770ec3705a9de7cc3373930b78b8a4007ed3f31e955cc8f
ENV OUTPUT_DIR=/tmp/
ENV FLICKR_API_KEY=notset
ENV PATH=/usr/local/airflow/.local/bin:$PATH
WORKDIR  /usr/local/airflow
ADD ./requirements.txt /usr/local/airflow
RUN pip install --user -r requirements.txt
RUN rm requirements.txt
