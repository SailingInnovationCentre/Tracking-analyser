import json

class CompetitorUploader:    

    def __init__ (self) : 
        pass

    def upload_entries(self, json_path, conn, cursor) : 
        with open(json_path) as json_file_object : 
            json_object = json.load(json_file_object)
    
        regatta_id = json_object['name']
        competitors_lst = json_object['competitors']
        list_to_upload = []

        for record in competitors_lst : 
            list_to_upload.append((record['id'], record['name'], \
                record['nationality'], regatta_id, record['boat']['sailId']))

        query = "INSERT INTO powertracks.competitors(comp_id, comp_name, nationality, regatta_id, sail_id) \
            VALUES (?,?,?,?,?)"
        cursor.executemany(query, list_to_upload)
        cursor.commit()

    def upload_datamining(self, json_dir, conn, cursor) : 
        avg_json_path = json_dir + "AvgSpeed_Per_Competitor.json"
        self.upload_avg_json(avg_json_path, conn, cursor)

        avg_legtype_json_path = json_dir + "AvgSpeed_Per_Competitor-LegType.json"
        self.upload_avg_legtype_json(avg_legtype_json_path, conn, cursor)

        dist_json_path = json_dir + "DistanceTraveled_Per_Competitor.json"
        self.upload_dist_json(dist_json_path, conn, cursor)

        dist_legtype_json_path = json_dir + "DistanceTraveled_Per_Competitor-LegType.json"
        self.upload_dist_legtype_json(dist_legtype_json_path, conn, cursor)

        maneuver_json_path = json_dir + "Maneuvers_Per_Competitor.json"
        self.upload_maneuvers_json(maneuver_json_path, conn, cursor)

    def upload_avg_json(self, json_path, conn, cursor) : 
        with open(json_path) as json_file_object : 
            json_object = json.load(json_file_object)
        
        list_to_upload = []

        regatta_id = json_object['regatta']
        for record in json_object['results'] :
            list_to_upload.append((record['value'], record['groupKey'][0], regatta_id))

        query = "UPDATE powertracks.competitors SET speed_kts_avg = ? \
            WHERE comp_name = ? AND regatta_id = ?"
        cursor.executemany(query, list_to_upload)
        cursor.commit()
    
    def upload_avg_legtype_json(self, json_path, conn, cursor) :
        with open(json_path) as json_file_object : 
            json_object = json.load(json_file_object)
            
        list_upwind_to_upload = []
        list_downwind_to_upload = []
        list_reaching_to_upload = []

        regatta_id = json_object['regatta']
        for record in json_object['results'] :
            tup = (record['value'], record['groupKey'][0][0], regatta_id)
            if record['groupKey'][1][0] == "UPWIND" :
                list_upwind_to_upload.append(tup)
            elif record['groupKey'][1][0] == "DOWNWIND" :
                list_downwind_to_upload.append(tup)
            elif record['groupKey'][1][0] == "REACHING" :
                list_reaching_to_upload.append(tup)

        if len(list_downwind_to_upload) > 0 : 
            query = "UPDATE powertracks.competitors SET speed_kts_downwind_avg = ? \
                WHERE comp_name = ? AND regatta_id = ?"
            cursor.executemany(query, list_downwind_to_upload)
            cursor.commit()

        if len(list_upwind_to_upload) > 0 : 
            query = "UPDATE powertracks.competitors SET speed_kts_upwind_avg = ? \
                WHERE comp_name = ? AND regatta_id = ?"
            cursor.executemany(query, list_upwind_to_upload)
            cursor.commit()

        if len(list_reaching_to_upload) > 0 : 
            query = "UPDATE powertracks.competitors SET speed_kts_reaching_avg = ? \
                WHERE comp_name = ? AND regatta_id = ?"
            cursor.executemany(query, list_reaching_to_upload)
            cursor.commit()

    def upload_dist_json(self, json_path, conn, cursor) : 
        with open(json_path) as json_file_object : 
            json_object = json.load(json_file_object)
            
        list_to_upload = []

        regatta_id = json_object['regatta']
        for record in json_object['results'] :
            list_to_upload.append((record['value'], record['groupKey'][0], regatta_id))

        query = "UPDATE powertracks.competitors SET distance_sum = ? \
            WHERE comp_name = ? AND regatta_id = ?"
        cursor.executemany(query, list_to_upload)
        cursor.commit()
    
    def upload_dist_legtype_json(self, json_path, conn, cursor) :
        with open(json_path) as json_file_object : 
            json_object = json.load(json_file_object)
            
        list_upwind_to_upload = []
        list_downwind_to_upload = []
        list_reaching_to_upload = []

        regatta_id = json_object['regatta']
        for record in json_object['results'] :
            tup = (record['value'], record['groupKey'][0][0], regatta_id)
            if record['groupKey'][1][0] == "UPWIND" :
                list_upwind_to_upload.append(tup)
            elif record['groupKey'][1][0] == "DOWNWIND" :
                list_downwind_to_upload.append(tup)
            elif record['groupKey'][1][0] == "REACHING" :
                list_reaching_to_upload.append(tup)

        if len(list_downwind_to_upload) > 0 : 
            query = "UPDATE powertracks.competitors SET distance_sum_downwind = ? \
                WHERE comp_name = ? AND regatta_id = ?"
            cursor.executemany(query, list_downwind_to_upload)
            cursor.commit()

        if len(list_upwind_to_upload) > 0 : 
            query = "UPDATE powertracks.competitors SET distance_sum_upwind = ? \
                WHERE comp_name = ? AND regatta_id = ?"
            cursor.executemany(query, list_upwind_to_upload)
            cursor.commit()

        if len(list_reaching_to_upload) > 0 : 
            query = "UPDATE powertracks.competitors SET distance_sum_reaching = ? \
                WHERE comp_name = ? AND regatta_id = ?"
            cursor.executemany(query, list_reaching_to_upload)
            cursor.commit()

    def upload_maneuvers_json(self, json_path, conn, cursor) : 
        with open(json_path) as json_file_object : 
            json_object = json.load(json_file_object)

        list_to_upload = []

        regatta_id = json_object['regatta']
        for record in json_object['results'] :
            list_to_upload.append((record['value'], record['groupKey'][0], regatta_id))

        query = "UPDATE powertracks.competitors SET sum_nr_maneuvers = ? \
            WHERE comp_name = ? AND regatta_id = ?"
        cursor.executemany(query, list_to_upload)
        cursor.commit() 