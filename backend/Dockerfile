FROM python:3.8-alpine

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE 1

# install psycopg2
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip
COPY requirements.txt /app/
RUN pip install -r requirements.txt

EXPOSE 8080

ENTRYPOINT ["sh", "/app/entrypoint.sh"]
