import json

class MarksUploader:    

    def __init__ (self) : 
        pass

    def upload(self, json_path, race_id, conn, cursor) : 
        with open(json_path) as json_file_object : 
            json_object = json.load(json_file_object)
    
        list_to_upload = []
        marks_list = json_object['marks']
        for record in marks_list : 

            list_positions_to_upload = []
            mark_id = record['id']
            mark_name = record['name']
            list_to_upload.append((mark_id, mark_name, race_id))

            for pos_record in record['track'] : 
                list_positions_to_upload.append((mark_id, pos_record['timepoint-ms'],\
                    race_id, pos_record['lat-deg'], pos_record['lng-deg']))
            
            query = "INSERT INTO powertracks.marks_positions VALUES (?,?,?,?,?)"
            cursor.executemany(query, list_positions_to_upload)
            cursor.commit()          

        query = "INSERT INTO powertracks.marks VALUES (?,?,?)"
        cursor.executemany(query, list_to_upload)
        cursor.commit()