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

        self.selected_regatta_names = [
            'Tokyo 2019',
            'WCS 2019 Enoshima',
            'HWCS 2020 Round 1',
            'WCS 2018 Marseille',
            'WCS 2018 Hyeres',
            'WCS 2019 Marseille',
            'SWC 2017 Hyeres',
            'Medemblik Regatta 2018',
            'Medemblik 2019',
            'Medemblik 2021',
            'SWC 2017 Miami',
            'WCS 2018 Miami',
            'WCS 2019 Miami',
            'HWCS 2020 Round 2',
            'SWC 2016 Melbourne',
            'Olympic Games 2012',
            'Olympic Games 2016'
        ]

    def regatta_in_selection(self, regatta_name):

        for n in self.selected_regatta_names :
            if n in regatta_name :
                return True

        return False

    def start(self):

        regatta_names = self.download_regattas()
        selected_regatta_names = [ n for n in regatta_names if self.regatta_in_selection(n) ]

        for n in sorted(selected_regatta_names) :
            print(n)

        for regatta_name in selected_regatta_names :
            regatta_folder = normalise_path_name(os.path.join(self.target_path, regatta_name))
            safe_mkdir(regatta_folder)

            for suffix in ('regattas', 'entries', 'windsummary'):
                regatta_url = f"{self.base_url}/regattas/{regatta_name}"
                regatta_path = normalise_path_name(f"{self.target_path}/{regatta_name}/{suffix}.json")
                json = self.json_downloader.download(regatta_url, regatta_path, f"{regatta_name}/{suffix}.json")

            tracked_race_names = []
            for s in json['series']:
                fleets = s['trackedRaces']['fleets']
                for fleet in fleets:
                    races = fleet['races']
                    for race in races:
                        if race['isTracked']:
                            tracked_race_names.append(race['trackedRaceName'])

            for race_name in tracked_race_names:
                fs_race_name = race_name.strip()   # Some races have trailing spaces...
                race_folder = normalise_path_name(f"{self.target_path}/{regatta_name}/{fs_race_name}")
                safe_mkdir(race_folder)

                # Strip race_name somehow. Trailing spaces are ignored! 

                for suffix in ('course', 'entries', 'firstlegbearing', 'markpassings', 'targettime', 'times', 'maneuvers'):
                    url = f"{self.base_url}/regattas/{regatta_name}/races/{race_name}/{suffix}"
                    path = normalise_path_name(f"{self.target_path}/{regatta_name}/{fs_race_name}/{suffix}.json")
                    self.json_downloader.download(url, path, f"{regatta_name}/{fs_race_name}/{suffix}.json")

                url = f"{self.base_url}/regattas/{regatta_name}/races/{race_name}/competitors/legs"
                path = normalise_path_name(f"{self.target_path}/{regatta_name}/{fs_race_name}/legs.json")
                self.json_downloader.download(url, path, f"{regatta_name}/{fs_race_name}/legs.json")

    def download_regattas(self):
        regattas_url = f"{self.base_url}/regattas"
        regattas_path = f"{self.target_path}/regattas.json"
        json = self.json_downloader.download(regattas_url, regattas_path, 'regattas.json')

        regatta_names = [regatta['name'] for regatta in json]
        return regatta_names
