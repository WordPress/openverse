# The sha256 sum is an immutable version of the image tag that's on the
# production server.
FROM puckel/docker-airflow@sha256:62f9f5392c31d03a1770ec3705a9de7cc3373930b78b8a4007ed3f31e955cc8f
ENV PATH=/usr/local/airflow/.local/bin:$PATH
ENV EXECUTOR=Local
WORKDIR  /usr/local/airflow
ADD ./requirements.txt /usr/local/airflow
RUN pip install --user -r requirements.txt
RUN rm requirements.txt
CMD ["webserver"]
