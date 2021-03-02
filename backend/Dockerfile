FROM python:3.8

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt /app/
RUN pip install -r requirements.txt

EXPOSE 8080

ENTRYPOINT ["sh", "/app/entrypoint.sh"]
