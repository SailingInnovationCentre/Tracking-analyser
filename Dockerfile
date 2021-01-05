FROM ubuntu:latest

RUN apt-get update && apt-get install -y python3-pip
RUN pip3 install -r powertracks/requirements.txt
RUN mkdir data

COPY src /powertracks

CMD python3 /powertracks/regatta_downloader.py
