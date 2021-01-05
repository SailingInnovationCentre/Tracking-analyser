import os.path
import requests
import json

from global_config import GlobalConfig
from azure_blob_uploader import AzureBlobUploader

class RegattaDownloader : 

    def __init__(self, config) :
        self.config = config

    def download_to(self, destination) :
        print ("Downloading Regattas...")
        r = requests.get(config.regattas_url)
        if r.status_code != 200 : 
            print("Download not successful.")
        try : 
            j = json.loads(r.text)
        except JSONDecodeError :
            print("Downloaded text is not a valid JSON.")
            raise

        with open(destination, 'w') as f :
            f.write(r.text)
        print ("Downloading Regattas done. ")
        return r.text

if __name__ == "__main__" : 
    config = GlobalConfig()
    downloader = RegattaDownloader(config)
    data = downloader.download_to(os.path.join(config.data_dir, "regattas.json"))

    uploader = AzureBlobUploader()
    uploader.upload('testcontainer', 'regattas.json', data)
