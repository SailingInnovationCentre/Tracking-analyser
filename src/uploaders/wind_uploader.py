import json

class WindUploader:    

    def __init__ (self) : 
        pass

    def upload(self, json_path, race_id, conn, cursor) : 
        print(json_path)
        with open(json_path) as json_file_object : 
            json_object = json.load(json_file_object)
            
        list_to_upload = []

        data_lst = json_object['windSources'][0]['COMBINED']
        for r in data_lst:
            list_to_upload.append((race_id, \
                r['timepoint-ms'], r['trueBearing-deg'], r['speed-kts'],\
                r['speed-m/s'], r['dampenedTrueBearing-deg'], r['dampenedSpeed-kts'],
                r['dampenedSpeed-m/s'], r['lat-deg'], r['lng-deg']))

        query = "INSERT INTO powertracks.wind VALUES (?,?,?,?,?,?,?,?,?,?)"
        cursor.executemany(query, list_to_upload)
        cursor.commit()