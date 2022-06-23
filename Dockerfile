FROM python:3.8.10

COPY / /ticketbook

WORKDIR /ticketbook

RUN pip3 install -r requirements.txt