import os
import os.path
import json
from json import JSONDecodeError

import requests


class JsonDownloader:

    def download(self, source_url: str, destination_json_path: str, description: str) -> object:

        # Cache!
        if os.path.exists(destination_json_path):
            if os.path.getsize(destination_json_path) == 0:
                print(f"Cached (empty): {description}")
                return None
            else:
                with open(destination_json_path) as f:
                    j = json.load(f)
                    print(f"Cached: {description}")
                    return j

        r = requests.get(source_url)
        if r.status_code != 200:
            print(f"Download not successful: {description}")
            f = open(destination_json_path, 'w')
            f.close()
            return None

        try:
            j = json.loads(r.text)
        except JSONDecodeError:
            print("Downloaded text is not a valid JSON.")
            print(r.text)
            raise

        with open(destination_json_path, 'w') as f:
            json.dump(j, f, indent=4)

        print(
            f"Download successful: {description} . Size: {int(len(r.text) / 1000)} kB. Time: " +
            f"{r.elapsed.total_seconds():.2f} s.")

        return j
