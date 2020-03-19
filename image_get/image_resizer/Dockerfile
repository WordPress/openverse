FROM python:3.7
RUN pip install pipenv

WORKDIR /image_resizer
COPY . /image_resizer/
RUN pipenv install

CMD pipenv run python consumer.py 
