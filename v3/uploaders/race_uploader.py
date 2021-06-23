import json


class RaceUploader:

    def __init__(self):
        pass

    def upload_races(self, json_path, cursor):
        print(json_path)
        with open(json_path) as json_file_object:
            json_object = json.load(json_file_object)

        dict_name_to_id = {}
        list_to_upload = []
        regatta_id = json_object['name']
        series_list = json_object['series']
        for series in series_list:
            for fleet in series['trackedRaces']['fleets']:
                for race in fleet['races']:
                    race_id = race['raceId']
                    race_name = race['name']
                    tracked_race_name = race['trackedRaceName']
                    is_tracked = race['isTracked']

                    if is_tracked :
                        list_to_upload.append((race_id, regatta_id, race_name, tracked_race_name))
                        dict_name_to_id[tracked_race_name] = race_id

        query = "INSERT INTO powertracks3.races(race_id, regatta_id, race_name, tracked_race_name) VALUES (?,?,?,?)"
        cursor.executemany(query, list_to_upload)
        cursor.commit()

        return dict_name_to_id
