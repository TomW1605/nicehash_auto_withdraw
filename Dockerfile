#Download base image ubuntu 16.04
FROM debian:stretch-slim

RUN apt-get update
RUN apt-get install -y python3 python3-pip python3-requests at
RUN pip3 install python-pushover

COPY ./nicehash_auto_withdraw /nicehash_auto_withdraw

VOLUME /config

CMD ["sh", "/nicehash_auto_withdraw/run.sh"]
