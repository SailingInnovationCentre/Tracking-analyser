import json

class RaceUploader:    

    def __init__ (self) : 
        pass

    def upload_races(self, json_path, conn, cursor) : 
        dict_short_name_to_id = {}

        with open(json_path) as json_file_object : 
            json_object = json.load(json_file_object)
            print(json_object)

            list_to_upload = []
            regatta_id = json_object['regatta']
            races_list = json_object['races']
            for record in races_list : 
                name = record['name']
                short_name = name.split(" ")[0]
                list_to_upload.append((record['id'], regatta_id, name, short_name))
                dict_short_name_to_id[short_name] = record['id']

            query = "INSERT INTO powertracks.races(race_id, regatta_id, race_name, race_short_name) VALUES (?,?,?,?)"

            cursor.executemany(query, list_to_upload)
            cursor.commit()
        
        return dict_short_name_to_id


    def upload_windsummary(self, json_path, dict_short_name_to_id, conn, cursor) : 
        with open(json_path) as json_file_object : 
            json_object = json.load(json_file_object)
            
            list_to_upload = []
            for record in json_object : 
                short_name = record['racecolumn']
                race_id = dict_short_name_to_id[short_name]
                fleet = record['fleet']
                lo = record['trueLowerboundWindInKnots']
                hi = record['trueUppwerboundWindInKnots']
                avg = record['trueWindDirectionInDegrees']

                list_to_upload.append((fleet, lo, hi, avg, race_id))

            query = "UPDATE powertracks.races set fleet = ?, min_wind_speed_kts = ?, max_wind_speed_kts = ?, avg_wind_dir_deg = ? WHERE race_id = ?"
            
            cursor.executemany(query, list_to_upload)
            cursor.commit()

    def upload_first_leg_bearing(self, json_path, race_id, conn, cursor) : 
        with open(json_path) as json_file_object : 
            json_object = json.load(json_file_object)
            deg = json_object['truebearingdegrees']

            query = "UPDATE powertracks.races set first_leg_bearing_deg = ? WHERE race_id = ?"

            cursor.execute(query, (deg, race_id))
            cursor.commit()
