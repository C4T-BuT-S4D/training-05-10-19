FROM mono:latest

MAINTAINER @kekov

ADD . /app
ADD ./start.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

CMD ["/entrypoint.sh"]