import pyodbc
import json
import sys
import os

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
    truncate_tables(conn, cursor)

    upload_regattas_overview(root_path, conn, cursor)

    regatta_dirs = find_regatta_dirs(root_path)
    for regatta_dir in regatta_dirs : 
        upload_regatta(regatta_dir, conn, cursor)

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
        race_dir_basename = os.path.basename(race_dir)
        short_name = uploader.make_short(race_dir_basename)
        race_id = dict_name_to_id[short_name]

        flb_json_path = os.path.join(race_dir, 'firstlegbearing.json')
        uploader.upload_first_leg_bearing(flb_json_path, race_id, conn, cursor)

        times_json_path = os.path.join(race_dir, 'times.json')
        uploader.upload_times(times_json_path, race_id, conn, cursor)
        


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



def other():


    """
    uploader = RaceUploader()
    
    path = "C:/data/powertracks/hwcs2020-round1/regattas/HWCS 2020 Round 1 - 49er/races.json"
    dict_name_to_id = uploader.upload_races(path, conn, cursor)

    path = "C:/data/powertracks/hwcs2020-round1/regattas/HWCS 2020 Round 1 - 49er/windsummary.json"
    uploader.upload_windsummary(path, dict_name_to_id, conn, cursor)

    path = "C:/data/powertracks/hwcs2020-round1/regattas/HWCS 2020 Round 1 - 49er/races/M Medal (49ER)/firstlegbearing.json"
    race_id = "9c45be60-ad9f-0137-131d-06773f917276"
    uploader.upload_first_leg_bearing(path, race_id, conn, cursor)
        
    path = "C:/data/powertracks/hwcs2020-round1/regattas/HWCS 2020 Round 1 - 49er/races/M Medal (49ER)/times.json"
    race_id = "9c45be60-ad9f-0137-131d-06773f917276"
    uploader.upload_times(path, race_id, conn, cursor)
    """

    race_id = "9c45be60-ad9f-0137-131d-06773f917276"
    """
    uploader = CompetitorUploader()
    path = "C:/data/powertracks/hwcs2020-round1/regattas/HWCS 2020 Round 1 - 49er/entries.json"
    uploader.upload_entries(path, conn, cursor)

    datamining_dir = "C:/data/powertracks/hwcs2020-round1/regattas/HWCS 2020 Round 1 - 49er/datamining/"
    uploader.upload_datamining(datamining_dir, conn, cursor)
    """

    """
    uploader = WindUploader()
    path = "C:/data/powertracks/hwcs2020-round1/regattas/HWCS 2020 Round 1 - 49er/races/M Medal (49ER)/wind--fromtime=2012-01-01T10__12__03Z&totime=2019-12-31T10__12__03Z.json"
    uploader.upload(path, race_id, conn, cursor)
    """

    """
    uploader = LegUploader()
    path = "C:/data/powertracks/hwcs2020-round1/regattas/HWCS 2020 Round 1 - 49er/races/M Medal (49ER)/competitors/legs.json"
    uploader.upload_legs(path, race_id, conn, cursor)
    path = "C:/data/powertracks/hwcs2020-round1/regattas/HWCS 2020 Round 1 - 49er/races/M Medal (49ER)/markpassings.json"
    uploader.upload_markpassings(path, race_id, conn, cursor)
    path = "C:/data/powertracks/hwcs2020-round1/regattas/HWCS 2020 Round 1 - 49er/races/M Medal (49ER)/competitors/positions.json"
    uploader.upload_positions(path, race_id, conn, cursor)
    """

    """
    path = "C:/data/powertracks/hwcs2020-round1/regattas/HWCS 2020 Round 1 - 49er/races/M Medal (49ER)/competitors/live.json"
    uploader = LiveUploader()
    uploader.upload(path, race_id, conn, cursor)
    """

    path = "C:/data/powertracks/hwcs2020-round1/regattas/HWCS 2020 Round 1 - 49er/races/M Medal (49ER)/marks/positions.json"
    uploader = MarksUploader()
    uploader.upload(path, race_id, conn, cursor)
    
    cursor.close()
    conn.close()

    print("reached the end.")


if __name__ == "__main__":
    main()