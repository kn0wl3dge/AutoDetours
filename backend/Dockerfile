FROM python:3.8-alpine

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE 1

# install psycopg2
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    && pip install psycopg2 \
    && apk del build-deps \
    && apk add netcat-openbsd

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt /app/
RUN pip install -r requirements.txt

EXPOSE 8080

ENTRYPOINT ["sh", "/app/entrypoint.sh"]
