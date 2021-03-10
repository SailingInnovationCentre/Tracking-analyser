import json

class LegUploader:    

    def __init__ (self) : 
        pass

    def upload_legs(self, json_path, race_id, conn, cursor) : 
        with open(json_path) as json_file_object : 
            json_object = json.load(json_file_object)
            list_to_upload = []

            data_lst = json_object['legs']
            for r in data_lst:
                upDown = 1 if r['upOrDownwindLeg'] else 0
                list_to_upload.append((race_id, \
                    r['fromWaypointId'], r['from'],\
                    r['toWaypointId'], r['to'], upDown))

            query = "INSERT INTO powertracks.legs(race_id, from_waypoint_id, from_waypoint_name, to_waypoint_id, to_waypoint_name, up_or_downwind_leg) VALUES (?,?,?,?,?,?)"
            cursor.executemany(query, list_to_upload)
            cursor.commit()
    