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

def main():

    root_path = extract_parameters()

    conn, cursor = create_connection()
    #truncate_tables(conn, cursor)

    upload_regattas_overview(root_path, conn, cursor)

    regatta_dirs = find_regatta_dirs(root_path)
    for regatta_dir in regatta_dirs : 

        #if "RS" not in regatta_dir : 
        #    continue

        upload_competitors(regatta_dir, conn, cursor)
        upload_regatta(regatta_dir, conn, cursor)
    
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

        #if "R1" not in race_dir : 
        #    continue
        
        race_dir_basename = os.path.basename(race_dir)
        short_name = uploader.make_short(race_dir_basename)
        race_id = dict_name_to_id[short_name]

        flb_json_path = os.path.join(race_dir, 'firstlegbearing.json')
        uploader.upload_first_leg_bearing(flb_json_path, race_id, conn, cursor)
        times_json_path = os.path.join(race_dir, 'times.json')
        uploader.upload_times(times_json_path, race_id, conn, cursor)

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
        path = os.path.join(race_dir, 'marks', 'positions.json')
        marks_uploader.upload(path, race_id, conn, cursor)

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

def distance_point_line(x0, y0, x1, y1, x2, y2) :
    # (x0, y0) is the point, the line is defined by (x1, y1) -> (x2, y2)
    
    numerator = (x2 - x1) * (y1 - y0) - (x1 - x0) * (y2 - y1)
    print(f"Numerator: {numerator}")
    denominator = ( math.pow((x2-x1), 2) + math.pow((y2-y1), 2)) / 2.0
    print(f"Denominator: {denominator}")
    distance = numerator / denominator
    return distance
    print(f"Distance: {distance}")
    relative_distance = distance / 25
    return relative_distance

if __name__ == "__main__":
    #main()

    x1 = 35.301074
    y1 = 139.503617

    x2 = 35.295528
    y2 = 139.491287

    x0 = 35.300643
    y0 = 139.499135

    print(distance_point_line(x0,y0,x1,y1,x2,y2))