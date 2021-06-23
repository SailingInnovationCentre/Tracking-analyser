import json


class RegattaUploader:

    def __init__(self):
        pass

    def upload(self, json_path, cursor):
        print(json_path)
        with open(json_path) as json_file_object:
            json_object = json.load(json_file_object)

        list_to_upload = []
        for record in json_object:
            if record['boatclass'] in ('470', '49er', '49erFX', 'Finn', 'Laser Int.',
                                       'Laser Radial', 'Nacra 17 Foiling', 'RS:X'):
                list_to_upload.append((record['name'], record['boatclass']))

        query = "INSERT INTO powertracks3.regattas(regatta_id, boatclass) VALUES (?,?)"
        cursor.executemany(query, list_to_upload)
        cursor.commit()
