FROM python:3.7-alpine

MAINTAINER @kekov

RUN apk add gcc musl-dev

ADD ./requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt

ADD . /app
ADD ./src/start.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]