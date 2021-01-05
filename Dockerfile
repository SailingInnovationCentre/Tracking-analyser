FROM ubuntu:latest

RUN apt-get update && apt-get install -y python3-pip

COPY src /powertracks
RUN pip3 install -r powertracks/requirements.txt
RUN mkdir data


CMD python3 /powertracks/regatta_downloader.py
