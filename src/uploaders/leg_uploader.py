import sys
import json
import uuid

class LegUploader:    

    def __init__ (self) : 
        self.dict_leg_id = {}        # (race_id, leg_nr) -> leg_id
        self.dict_leg_comp_id = {}   # (race_id, leg_nr, comp_id) -> leg_comp_id

    def upload_legs(self, json_path, race_id, conn, cursor) : 

        with open(json_path) as json_file_object : 
            json_object = json.load(json_file_object)
        
        leg_list_to_upload = []
        comp_leg_list_to_upload = []

        """
        There is an error in this file. If there are 5 legs, with 10 competitors. In some way, 
        this is represented in this file as 50 legs, all containing 10 competitors. Therefore, 
        we need to filter out the duplicates. We do that by making sure that for each 'fromWaypointId', 
        we only add one leg. 
        """

        fromWaypointIdSet = set()
        leg_nr = 0

        leg_lst = json_object['legs']
        for leg_record in leg_lst:

            # If we already had this waypoint, skip the record in order to avoid duplicates. 
            fromWaypointId = leg_record['fromWaypointId']
            if fromWaypointId in fromWaypointIdSet : 
                continue

            # This is a newly generated ID, unique for each leg. 
            leg_id = str(uuid.uuid4())
            self.dict_leg_id[(race_id, leg_nr)] = leg_id

            up_down = 1 if leg_record['upOrDownwindLeg'] else 0          
            leg_list_to_upload.append((leg_id, race_id, leg_nr, \
                leg_record['fromWaypointId'], leg_record['from'],\
                leg_record['toWaypointId'], leg_record['to'], up_down))

            # Add leg_comps
            competitor_lst = leg_record['competitors']
            for comp_record in competitor_lst : 
                comp_id = comp_record['id']
                comp_leg_id = str(uuid.uuid4())
                self.dict_leg_comp_id[(race_id, leg_nr, comp_id)] = comp_leg_id

                comp_leg_list_to_upload.append((comp_leg_id, leg_id, comp_id, \
                    comp_record['distanceTraveled-m'], comp_record['averageSOG-kts'], \
                    comp_record['tacks'], comp_record['jibes'], comp_record['penaltyCircles'], comp_record['rank'], \
                    comp_record['gapToLeader-s'], comp_record['gapToLeader-m'], \
                    comp_record['started'], comp_record['finished']))

            fromWaypointIdSet.add(fromWaypointId)
            leg_nr += 1

        query = "INSERT INTO powertracks.legs(leg_id, race_id, leg_nr, from_waypoint_id, \
            from_waypoint_name, to_waypoint_id, to_waypoint_name, up_or_downwind_leg) \
            VALUES (?,?,?,?,?,?,?,?)"
        cursor.executemany(query, leg_list_to_upload)
        cursor.commit()

        query = "INSERT INTO powertracks.comp_leg(comp_leg_id, leg_id, comp_id, \
            distance_traveled_m, average_sog_kts, tacks, jibes, penalty_circles, rank, \
            gap_to_leader_s, gap_to_leader_m, started, finished) \
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"
        cursor.executemany(query, comp_leg_list_to_upload)
        cursor.commit()
    
    def upload_markpassings(self, json_path, race_id, conn, cursor) :

        with open(json_path) as json_file_object : 
            json_object = json.load(json_file_object)

        list_to_upload = []
        for comp_record in json_object['bycompetitor'] :
            comp_id = comp_record['competitor']['id']
            mp_list = comp_record['markpassings']

            for mp_record in mp_list :
                ms = mp_record['timeasmillis']
                leg_nr = mp_record['zeroBasedWaypointIndex']

                if leg_nr > 0 : 
                    list_to_upload[-1][1] = ms
                if leg_nr < len(mp_list) - 1 : 
                    comp_leg_id = self.dict_leg_comp_id[(race_id, leg_nr, comp_id)]
                    list_to_upload.append([ms, 0, comp_leg_id])
        
        query = "UPDATE powertracks.comp_leg \
            SET start_ms = ?, end_ms = ? \
            WHERE comp_leg_id = ?"
        cursor.executemany(query, list_to_upload)
        cursor.commit()

    def __create_comp_leg_lookup_list(self, race_id, comp_id, conn, cursor) : 
        
        query = "select start_ms, end_ms, comp_leg_id \
            from powertracks.comp_leg cl join powertracks.legs l on cl.leg_id = l.leg_id \
            where comp_id = ? and race_id = ?"
    
        rows = cursor.execute(query, (comp_id, race_id)).fetchall()
        rows.sort()  # Sort based on start_ms. 

        return rows

    def upload_positions(self, json_path, race_id, conn, cursor) :
        
        with open(json_path) as json_file_object : 
            json_object = json.load(json_file_object)

        for comp_record in json_object['competitors'] :
            comp_id = comp_record['id']
            comp_leg_lookup = self.__create_comp_leg_lookup_list(race_id, comp_id, conn, cursor)
            
            list_to_upload = []
            track_list = comp_record['track']
            for track_record in track_list : 
                ms = track_record['timepoint-ms']
                try : 
                    comp_leg_id = next(x[2] for x in comp_leg_lookup if ms > x[0])
                except StopIteration : 
                    # Outside scope of any leg. 
                    continue

                list_to_upload.append((comp_leg_id, ms, track_record['lat-deg'], track_record['lng-deg'], \
                    track_record['truebearing-deg'], track_record['speed-kts']))

            query = "INSERT INTO powertracks.positions(comp_leg_id, timepoint_ms, lat_deg, lng_deg, \
                true_bearing_deg, speed_kts) VALUES (?,?,?,?,?,?)"
            cursor.executemany(query, list_to_upload)
            cursor.commit()   


  