FROM python:3.7
RUN pip install pipenv

WORKDIR /image_spider
COPY . /image_spider/
RUN pipenv install --system --deploy

CMD pipenv run scrapy crawl image
