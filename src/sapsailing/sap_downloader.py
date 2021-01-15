import os
import os.path
from datetime import datetime

from sapsailing.regatta_downloader import RegattaDownloader

class SapDownloader: 

    def __init__(self, config) :
        self.__config = config
        now = datetime.now()
        timestamp_str = now.strftime("%Y-%m-%d_%H:%M:%S")
        self.__download_folder = os.path.join(self.__config.data_dir, timestamp_str)
        os.mkdir(self.__download_folder)
        print(f"Created folder '{self.__download_folder}'.")
    
    def start(self) :
        d = RegattaDownloader(self.__config)
        d.download(self.__download_folder)
