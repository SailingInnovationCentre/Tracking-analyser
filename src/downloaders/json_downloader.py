import os.path
import json
import requests
from requests.models import InvalidURL

class JsonDownloader: 

    def download(self, source_url, destination_json_path, description) : 
        
        # Cache! 
        print(destination_json_path)
        if os.path.exists(destination_json_path) : 
            with open(destination_json_path) as f : 
                j = json.load(f)
                print (f"Cached: '{description}'")
                return j

        print (f"Downloading '{description}'...")
        r = requests.get(source_url)
        if r.status_code != 200 : 
            print("Download not successful.")
            raise InvalidURL()

        try : 
            j = json.loads(r.text)
        except JSONDecodeError :
            print("Downloaded text is not a valid JSON.")
            print(r.text)
            raise

        with open(destination_json_path, 'w') as f :
            json.dump(j, f, indent=4)

        print (f"Download of '{description}'' done. Size: {int(len(r.text) / 1000)} kB. Time: {r.elapsed.total_seconds():.2f} s.")

        return j

