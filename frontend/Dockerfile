FROM node:latest

RUN npm install -g nodemon

RUN mkdir -p /usr/src/app/
WORKDIR /usr/src/app/

ONBUILD RUN npm install

ENV HOST 0.0.0.0
