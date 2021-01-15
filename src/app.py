from config import Config
from sapsailing.sap_downloader import SapDownloader

if __name__ == "__main__" : 
    config = Config()
    downloader = SapDownloader(config)
    downloader.start()
