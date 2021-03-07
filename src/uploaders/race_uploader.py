import json

class RaceUploader:    

    def __init__ (self) : 
        pass

    def upload_races(self, json_path, conn, cursor) : 
        with open(json_path) as json_file_object : 
            json_object = json.load(json_file_object)
    
            list_to_upload = []
            regatta_id = json_object['regatta']
            races_list = json_object['races']
            for record in races_list : 
                list_to_upload.append((record['id'], regatta_id, record['name']))

            query = "INSERT INTO powertracks.races(race_id, regatta_id, race_name) VALUES (?,?,?)"

            cursor.executemany(query, list_to_upload)
            cursor.commit()


    def upload_windsummary(self, json_path, conn, cursor) : 
        pass

    def upload_first_leg_bearing(self, json_path, conn, cursor) : 
        pass