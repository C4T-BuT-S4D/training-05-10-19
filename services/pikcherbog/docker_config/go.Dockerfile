FROM golang

MAINTAINER @pomo_mondreganto

ADD ./ /app
WORKDIR /app/src/server
ENV GOPATH=/app/


RUN go build .
CMD ["go", "run", "."]
