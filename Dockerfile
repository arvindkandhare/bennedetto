FROM ubuntu:latest

MAINTAINER ARvind Kandhare

# apt is up to date
RUN apt-get update

# Basic tools
RUN apt-get install -y tar git curl nano wget dialog net-tools build-essential

# Install Python and Basic Python Tools
RUN apt-get install -y python python-dev python-distribute python-pip nodejs npm

RUN apt-get install tesseract-ocr

RUN npm install node-tesseract

ADD . /benedetto

RUN make dev-bootstrap


EXPOSE 8000

WORKDIR /benedetto

CMD make run

