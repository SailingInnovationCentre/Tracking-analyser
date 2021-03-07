import json

class RegattaUploader:    

    def __init__ (self) : 
        pass

    def upload(self, json_path, conn, cursor) : 
        with open(json_path) as json_file_object : 
            regattas_json = json.load(json_file_object)
    
            list_to_upload = []
            for record in regattas_json : 
                for att in record : 
                    print(record[att])
                print()

                list_to_upload.append((record['name'], record['boatclass'], record['courseAreaId']))

            query = "INSERT INTO powertracks.regattas VALUES (?,?,?)"

            cursor.executemany(query, list_to_upload)
            cursor.commit()

