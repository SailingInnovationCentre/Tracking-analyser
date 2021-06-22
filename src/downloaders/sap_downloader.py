import os.path 
from shutil import rmtree

from downloaders.json_downloader import JsonDownloader

def safe_mkdir(path) : 
    if not os.path.exists(path) : 
        os.mkdir(path)

def normalise_path_name(path) : 
    return path[:3] + path[3:].replace(":", "")

class SapDownloader : 

    def __init__(self, base_url, target_path): 
        self.json_downloader = JsonDownloader()
        self.base_url = base_url
        self.target_path = target_path       

    def start(self) : 

        regatta_names = self.download_regattas()

        for regatta_name in [ n for n in regatta_names if 'Medemblik Reg' in n ] : 
            regatta_path = normalise_path_name(os.path.join(self.target_path, regatta_name))
            safe_mkdir(regatta_path)

            regatta_url = f"{self.base_url}/regattas/{regatta_name}"
            regatta_path = normalise_path_name(f"{self.target_path}/{regatta_name}/regattas.json")
            json = self.json_downloader.download(regatta_url, regatta_path, f"Regatta: {regatta_name}")

            tracked_race_names = []
            for s in json['series'] : 
                for tracked_race in s['trackedRaces'] :
                    print (tracked_race) 
                    for f in tracked_race['fleets'][0] : 
                        for r in f['races'] : 
                            tracked_race_names.append(r['name'])

            print(tracked_race_names)



    def download_regattas(self) : 
        regattas_url = f"{self.base_url}/regattas"
        regattas_path = f"{self.target_path}/regattas.json"
        json = self.json_downloader.download(regattas_url, regattas_path, 'Regattas')

        regatta_names = [ regatta['name'] for regatta in json ]
        return regatta_names

