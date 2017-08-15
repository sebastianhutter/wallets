FROM python:alpine
MAINTAINER sebastian hutter <mail@sebastian-hutter.ch>

ADD requirements.txt /requirements.txt

ENV PYTHONPATH="${PYTHONPATH}:/app"

RUN apk --no-cache add --virtual build-dependencies build-base gcc binutils linux-headers libffi-dev openssl-dev && \
  apk add --no-cache tini libffi curl jq && \
  pip install --upgrade -r /requirements.txt && \
  apk del build-dependencies

ADD build/docker-entrypoint.sh /docker-entrypoint.sh

RUN adduser -D wallets \
  && chmod +x /docker-entrypoint.sh

ADD wallets /app

USER wallets
WORKDIR /app

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["python", "/app/wallets.py"]