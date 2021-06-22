import os.path

from downloaders.json_downloader import JsonDownloader


def safe_mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def normalise_path_name(path):
    return path[:3] + path[3:].replace(":", "")


class SapDownloader:

    def __init__(self, base_url, target_path):
        self.json_downloader = JsonDownloader()
        self.base_url = base_url
        self.target_path = target_path

    def start(self):

        regatta_names = self.download_regattas()

        for regatta_name in [n for n in regatta_names if 'Medemblik Reg' in n]:
            regatta_folder = normalise_path_name(os.path.join(self.target_path, regatta_name))
            safe_mkdir(regatta_folder)

            regatta_url = f"{self.base_url}/regattas/{regatta_name}"
            regatta_path = normalise_path_name(f"{self.target_path}/{regatta_name}/regattas.json")
            json = self.json_downloader.download(regatta_url, regatta_path, f"{regatta_name}/regattas.json")

            tracked_race_names = []
            for s in json['series']:
                fleets = s['trackedRaces']['fleets']
                for fleet in fleets:
                    races = fleet['races']
                    for race in races:
                        if race['isTracked']:
                            tracked_race_names.append(race['trackedRaceName'])

            for race_name in tracked_race_names:
                race_folder = normalise_path_name(f"{self.target_path}/{regatta_name}/{race_name}")
                safe_mkdir(race_folder)

                for suffix in ('entries', 'markpassings', 'targettime', 'times', 'maneuvers'):
                    url = f"{self.base_url}/regattas/{regatta_name}/races/{race_name}/{suffix}"
                    path = normalise_path_name(f"{self.target_path}/{regatta_name}/{race_name}/{suffix}.json")
                    self.json_downloader.download(url, path, f"{regatta_name}/{race_name}/{suffix}.json")

                url = f"{self.base_url}/regattas/{regatta_name}/races/{race_name}/competitors/legs"
                path = normalise_path_name(f"{self.target_path}/{regatta_name}/{race_name}/legs.json")
                self.json_downloader.download(url, path, f"{regatta_name}/{race_name}/legs.json")

    def download_regattas(self):
        regattas_url = f"{self.base_url}/regattas"
        regattas_path = f"{self.target_path}/regattas.json"
        json = self.json_downloader.download(regattas_url, regattas_path, 'regattas.json')

        regatta_names = [regatta['name'] for regatta in json]
        return regatta_names
