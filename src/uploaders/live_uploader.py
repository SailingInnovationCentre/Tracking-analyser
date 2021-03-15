import json

class LiveUploader:    

    def __init__ (self) : 
        pass

    def upload(self, json_path, race_id, conn, cursor) : 
        with open(json_path) as json_file_object : 
            json_object = json.load(json_file_object)
    
        list_to_upload = []
        comp_list = json_object['competitors']
        for record in comp_list : 
            list_to_upload.append((race_id, record['id'], record['rank']))

        query = "INSERT INTO powertracks.race_comp(race_id, comp_id, rank) VALUES (?,?,?)"
        cursor.executemany(query, list_to_upload)
        cursor.commit()