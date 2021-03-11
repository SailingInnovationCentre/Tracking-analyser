import json
import uuid

class LegUploader:    

    def __init__ (self) : 
        pass

    def upload(self, json_path, race_id, conn, cursor) : 

        with open(json_path) as json_file_object : 
            json_object = json.load(json_file_object)
        
        list_to_upload = []
        i_to_leg_id_dict = {}

        leg_lst = json_object['legs']
        for i, leg_record in enumerate(leg_lst):
            up_down = 1 if leg_record['upOrDownwindLeg'] else 0
            leg_id = str(uuid.uuid4())
            i_to_leg_id_dict[i] = leg_id
            list_to_upload.append((leg_id, race_id, \
                leg_record['fromWaypointId'], leg_record['from'],\
                leg_record['toWaypointId'], leg_record['to'], up_down))

        query = "INSERT INTO powertracks.legs(leg_id, race_id, from_waypoint_id, \
            from_waypoint_name, to_waypoint_id, to_waypoint_name, up_or_downwind_leg) \
            VALUES (?,?,?,?,?,?,?)"
        cursor.executemany(query, list_to_upload)
        cursor.commit()
    
        list_to_upload = []

        for i, leg_record in enumerate(leg_lst):
            leg_id = i_to_leg_id_dict[i]
            competitors_lst = leg_record['competitors']
            for comp_record in competitors_lst :
                comp_id = comp_record['id']
                list_to_upload.append((leg_id, comp_id, \
                    comp_record['distanceTraveled-m'], comp_record['averageSOG-kts'], \
                    comp_record['tacks'], comp_record['jibes'], comp_record['penaltyCircles'], comp_record['rank'], \
                    comp_record['gapToLeader-s'], comp_record['gapToLeader-m'], \
                    comp_record['started'], comp_record['finished']))
        
        query = "INSERT INTO powertracks.comp_leg(leg_id, comp_id, \
            distance_traveled_m, average_sog_kts, tacks, jibes, penalty_circles, rank, \
            gap_to_leader_s, gap_to_leader_m, started, finished) \
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
        cursor.executemany(query, list_to_upload)
        cursor.commit()


