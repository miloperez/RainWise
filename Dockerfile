FROM python:3.11.6-alpine3.17

COPY . /usr/src/app
WORKDIR /usr/src/app

RUN pip install -r requirements.txt

ENTRYPOINT python main.py