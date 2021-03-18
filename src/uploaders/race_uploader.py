import json
import re

class RaceUploader:    

    def __init__ (self) : 
        pass

    def upload_races(self, json_path, conn, cursor) : 
        print (json_path)
        with open(json_path) as json_file_object : 
            json_object = json.load(json_file_object)

        dict_name_to_id = {}  # Both regular and short names! 
        list_to_upload = []
        regatta_id = json_object['regatta']
        races_list = json_object['races']
        for record in races_list : 
            name = record['name']
            short_name = self.make_short(name)
            race_id = record['id']
            list_to_upload.append((race_id, regatta_id, name, short_name))
            dict_name_to_id[short_name] = race_id
            dict_name_to_id[name] = race_id
            if re.match('[a-zA-Z]0[0-9]', short_name) is not None :
                # R08 -> R8
                shorter_name = short_name[0] + short_name[2] 
                dict_name_to_id[shorter_name] = race_id

        query = "INSERT INTO powertracks.races(race_id, regatta_id, race_name, race_short_name) VALUES (?,?,?,?)"
        cursor.executemany(query, list_to_upload)
        cursor.commit()
        
        return dict_name_to_id

    def make_short(self, long_name) : 
        i_space = long_name.find(' ')
        i_bracket = long_name.find('(')
        if i_space == -1 : 
            i_space = 100
        if i_bracket == -1 : 
            i_bracket = 100
        
        min_index = min(i_space, i_bracket)
        if min_index == 100 : 
            return long_name

        return long_name[:min_index]

    def upload_windsummary(self, json_path, dict_short_name_to_id, conn, cursor) : 
        print (json_path)
        with open(json_path) as json_file_object : 
            json_object = json.load(json_file_object)
            
        list_to_upload = []
        for record in json_object : 
            short_name = record['racecolumn']
            
            # Super hack. 
            if short_name == 'M' and short_name not in dict_short_name_to_id : 
                if "R13" in dict_short_name_to_id :
                    short_name = "R13"
                elif "R11" in dict_short_name_to_id : 
                    # For RS:X races. 
                    short_name = "R11"

            race_id = dict_short_name_to_id[short_name]
            fleet = record['fleet']
            lo = record['trueLowerboundWindInKnots']
            hi = record['trueUppwerboundWindInKnots']
            avg = record['trueWindDirectionInDegrees']

            list_to_upload.append((fleet, lo, hi, avg, race_id))

        query = "UPDATE powertracks.races set fleet = ?, \
            min_wind_speed_kts = ?, max_wind_speed_kts = ?, avg_wind_dir_deg = ? \
            WHERE race_id = ?"
        cursor.executemany(query, list_to_upload)
        cursor.commit()

    def upload_first_leg_bearing(self, json_path, race_id, conn, cursor) : 
        print (json_path)
        with open(json_path) as json_file_object : 
            json_object = json.load(json_file_object)
        
        deg = json_object['truebearingdegrees']

        query = "UPDATE powertracks.races set first_leg_bearing_deg = ? WHERE race_id = ?"
        cursor.execute(query, (deg, race_id))
        cursor.commit()

    def upload_times(self, json_path, race_id, conn, cursor) :
        print (json_path)
        with open(json_path) as json_file_object : 
            json_object = json.load(json_file_object)

        start_ms = json_object['startOfRace-ms']
        end_ms = json_object['endOfRace-ms']

        query = "UPDATE powertracks.races set start_of_race_ms = ?, end_of_race_ms = ? WHERE race_id = ?"
        cursor.execute(query, (start_ms, end_ms, race_id))
        cursor.commit()
