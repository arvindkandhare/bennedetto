FROM ubuntu:latest

MAINTAINER ARvind Kandhare

# apt is up to date
RUN apt-get update

# Basic tools
RUN apt-get install -y tar git curl nano wget dialog net-tools build-essential

# Install Python and Basic Python Tools
RUN apt-get install -y python python-dev python-distribute python-pip nodejs npm

RUN apt-get install -y tesseract-ocr

RUN npm install -g node-tesseract

RUN npm install -g grunt-cli

ADD . /benedetto

WORKDIR /benedetto

RUN make dev-bootstrap


EXPOSE 8000

CMD make run

