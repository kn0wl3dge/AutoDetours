FROM node:latest

ENV HOST 0.0.0.0
ENV NODE_ENV development

RUN npm install -g nodemon

RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/

COPY package*.json ./
RUN npm install
