import os.path
import requests
import json

from sapsailing.json_downloader import JsonDownloader

class RegattaDownloader : 

    def __init__(self, config) :
        self.__downloader = JsonDownloader(config)
        self.__source_url = config.base_url + 'regattas'

    def download(self, destination_folder) :
        destination_json = os.path.join(destination_folder, "regattas.json")
        self.__downloader.download(self.__source_url, destination_json, "Regattas")
        