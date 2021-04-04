#Download base image ubuntu 16.04
FROM debian:stretch-slim

RUN apt-get update
RUN apt-get install -y python3 python3-pip python3-requests
RUN pip3 install python-pushover

COPY nicehash_auto_withdraw /nicehash_auto_withdraw

RUN mkdir /tmp

COPY config.ini /config/config.ini

VOLUME /config
