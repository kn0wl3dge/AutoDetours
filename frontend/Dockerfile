FROM node:15.12-alpine

ENV HOST 0.0.0.0
ENV NODE_ENV development

RUN apk add --update \
    build-base \
    python \
    python-dev \
    py-pip \
  && rm -rf /var/cache/apk/*

RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/

COPY package*.json ./
RUN npm install && npm rebuild node-sass
