FROM python:3.6-alpine

ENV FLASK_APP=ejudge_listener.wsgi.py:application
# ENV PIP_INDEX_URL=https://registry.tcsbank.ru/repository/pypi-all/simple/

COPY . /code
WORKDIR /code

RUN apk add --no-cache gcc musl-dev python3-dev
RUN pip3 install -r requirements.txt -r dev-requirements.txt

CMD ["flask", "run", "--host", "0.0.0.0", "--port", "23456", "--no-reload"]
