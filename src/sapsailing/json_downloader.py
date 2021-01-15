import json
import requests

class JsonDownloader: 

    def __init__(self, config):
        self.__config = config

    def download(self, source_url, destination_json_path, description) : 
        
        print (f"Downloading '{description}'...")
        r = requests.get(source_url)
        if r.status_code != 200 : 
            print("Download not successful.")
            raise 
        try : 
            j = json.loads(r.text)
        except JSONDecodeError :
            print("Downloaded text is not a valid JSON.")
            print(r.text)
            raise

        with open(destination_json_path, 'w') as f :
            f.write(r.text)

        print (f"Download of '{description}'' done. ")