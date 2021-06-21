import pyodbc
import json
import sys
import os
import math

from uploaders.regatta_uploader import RegattaUploader
from uploaders.race_uploader import RaceUploader
from uploaders.competitor_uploader import CompetitorUploader
from uploaders.wind_uploader import WindUploader
from uploaders.leg_uploader import LegUploader
from uploaders.live_uploader import LiveUploader
from uploaders.marks_uploader import MarksUploader
from uploaders.aux_uploader import AuxUploader
from downloaders.sap_downloader import SapDownloader

def main(): 
    main_download()
    #main_upload()

def main_download():
    base_url = 'https://www.sapsailing.com/sailingserver/api/v1'
    target_path = 'c:/data/powertracks/auto_download'
    downloader = SapDownloader(base_url, target_path)
    downloader.start()

def main_upload():

    root_path = extract_parameters()

    conn, cursor = create_connection()

    # Safety first! 
    sys.exit(0) 


    
    #truncate_tables(conn, cursor)

    """
    uploader = AuxUploader(conn, cursor)
    uploader.start() 

    upload_regattas_overview(root_path, conn, cursor)

    regatta_dirs = find_regatta_dirs(root_path)
    for regatta_dir in regatta_dirs : 

        #if "RS" not in regatta_dir : 
        #    continue

        upload_competitors(regatta_dir, conn, cursor)
        upload_regatta(regatta_dir, conn, cursor)
    """

    cursor.close()
    conn.close()


def upload_regattas_overview(root_path, conn, cursor) : 
    path = os.path.join(root_path, 'regattas.json')
    uploader = RegattaUploader()
    uploader.upload(path, conn, cursor)

def upload_regatta(regatta_dir, conn, cursor) : 
    uploader = RaceUploader()
    
    races_json_path = os.path.join(regatta_dir, 'races.json') 
    dict_name_to_id = uploader.upload_races(races_json_path, conn, cursor)
    
    windsummary_json_path = os.path.join(regatta_dir, 'windsummary.json')
    uploader.upload_windsummary(windsummary_json_path, dict_name_to_id, conn, cursor)

    race_dirs = find_races_dirs(regatta_dir)
    for race_dir in race_dirs : 

        #if "R5" not in race_dir : 
        #    continue
        
        race_dir_basename = os.path.basename(race_dir)
        short_name = uploader.make_short(race_dir_basename)
        race_id = dict_name_to_id[short_name]

        flb_json_path = os.path.join(race_dir, 'firstlegbearing.json')
        uploader.upload_first_leg_bearing(flb_json_path, race_id, conn, cursor)
        times_json_path = os.path.join(race_dir, 'times.json')
        uploader.upload_times(times_json_path, race_id, conn, cursor)
        course_json_path = os.path.join(race_dir, 'course.json')
        uploader.upload_course(course_json_path, race_id, conn, cursor)

        wind_uploader = WindUploader()
        wind_file_path = find_wind_file(race_dir)
        wind_uploader.upload(wind_file_path, race_id, conn, cursor)

        leg_uploader = LegUploader()
        path = os.path.join(race_dir, 'competitors', 'legs.json')
        leg_uploader.upload_legs(path, race_id, conn, cursor)
        path = os.path.join(race_dir, 'markpassings.json')
        leg_uploader.upload_markpassings(path, race_id, conn, cursor)
        path = os.path.join(race_dir, 'competitors', 'positions.json')
        leg_uploader.upload_positions(path, race_id, conn, cursor)

        path = os.path.join(race_dir, 'competitors', 'live.json')
        live_uploader = LiveUploader()
        live_uploader.upload(path, race_id, conn, cursor)

        marks_uploader = MarksUploader()
        marks_path = os.path.join(race_dir, 'marks', 'positions.json')
        marks_uploader.upload(marks_path, race_id, conn, cursor)

def upload_competitors(regatta_dir, conn, cursor) :
    uploader = CompetitorUploader()
    
    path = os.path.join(regatta_dir, 'entries.json')
    uploader.upload_entries(path, conn, cursor)

    datamining_dir = os.path.join(regatta_dir, 'datamining')
    uploader.upload_datamining(datamining_dir, conn, cursor)

def extract_parameters() : 

    if len(sys.argv) != 2 : 
        print ("Usage: python main.py <dir>")
        sys.exit(1)

    root_path = sys.argv[1]

    if not os.path.isdir(root_path) : 
        raise FileNotFoundError("Directory not found: " + root_path)

    return root_path

def create_connection() :
    server = 'sic-match-analysis.database.windows.net'
    database = 'match-analysis'
    username = 'sic-admin'
    password = 'ZeilenIsLeuk!'
    driver= '{ODBC Driver 17 for SQL Server}'

    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = conn.cursor()    
    cursor.fast_executemany = True

    return conn, cursor

def truncate_tables(conn, cursor) :
    for name in ('regattas', 'races', 'competitors', 'race_comp', 'legs', \
        'comp_leg', 'positions', 'wind', 'marks', 'marks_positions') :
        cursor.execute(f'TRUNCATE TABLE powertracks.{name}')
        cursor.commit()

def find_regatta_dirs(root_path) : 
    return get_immediate_subdirectories(os.path.join(root_path, 'regattas'))

def find_races_dirs(root_path) : 
    return get_immediate_subdirectories(os.path.join(root_path, 'races'))

def get_immediate_subdirectories(a_dir):
    return [os.path.join(a_dir, name) for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]

def find_wind_file(race_dir) : 
    l = [ filename for filename in os.listdir(race_dir) if filename.startswith('wind--') and filename.endswith('json')]
    if len(l) != 1 : 
        raise Exception("Too many possible wind files.")
    return os.path.join(race_dir, l[0])



def compute_rel_distance_startline(l1x, l1y, l2x, l2y, px, py) : 
    #print("\n")
    
    r = math.sqrt( math.pow(l2x-l1x,2) + math.pow(l2y-l1y,2) )
    theta = - math.atan( (l2x - l1x) / (l2y - l1y) )
    #print(f"Theta: {theta}")
    
    
    translated_px = px - l1x
    translated_py = py - l1y
    #print(f"Translated: ({translated_px},{translated_py})")
    
    rotated_px =  translated_px * math.cos(theta) + translated_py * math.sin(theta)
    rotated_py = -translated_px * math.sin(theta) + translated_py * math.cos(theta)
    #print(f"Rotated: ({rotated_px}, {rotated_py})")
    
    scaled_px = rotated_px / r
    scaled_py = rotated_py / r
    #print(f"Scaled: ({scaled_px}, {scaled_py})")
    
    if l2y < l1y : 
        ret = -scaled_py
    else :
        ret = scaled_py

    return ret

def test_rel_pos_startline() : 
    l1x = 0
    l1y = 0
    l2x = 200
    l2y = 100

    print (compute_rel_distance_startline(l1x, l1y, l2x, l2y, -100, -50))
    print (compute_rel_distance_startline(l1x, l1y, l2x, l2y, 0, 0))
    print (compute_rel_distance_startline(l1x, l1y, l2x, l2y, 50, 25))
    print (compute_rel_distance_startline(l1x, l1y, l2x, l2y, 300, 150))
    print()

    l1x = 0
    l1y = 0
    l2x = -200
    l2y = 100

    print (compute_rel_distance_startline(l1x, l1y, l2x, l2y, 100, -50))
    print (compute_rel_distance_startline(l1x, l1y, l2x, l2y, 0, 0))
    print (compute_rel_distance_startline(l1x, l1y, l2x, l2y, -50, 25))
    print (compute_rel_distance_startline(l1x, l1y, l2x, l2y, -300, 150))
    print()

    l1x = 0
    l1y = 0
    l2x = -200
    l2y = -100

    print (compute_rel_distance_startline(l1x, l1y, l2x, l2y, 100, 50))
    print (compute_rel_distance_startline(l1x, l1y, l2x, l2y, 0, 0))
    print (compute_rel_distance_startline(l1x, l1y, l2x, l2y, -50, -25))
    print (compute_rel_distance_startline(l1x, l1y, l2x, l2y, -300, -150))
    print()

    l1x = 0
    l1y = 0
    l2x = 200
    l2y = -100

    print (compute_rel_distance_startline(l1x, l1y, l2x, l2y, -100, 50))
    print (compute_rel_distance_startline(l1x, l1y, l2x, l2y, 0, 0))
    print (compute_rel_distance_startline(l1x, l1y, l2x, l2y, 50, -25))
    print (compute_rel_distance_startline(l1x, l1y, l2x, l2y, 300, -150))

if __name__ == "__main__":
    main()
