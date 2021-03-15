import pyodbc
import json

from uploaders.regatta_uploader import RegattaUploader
from uploaders.race_uploader import RaceUploader
from uploaders.competitor_uploader import CompetitorUploader
from uploaders.wind_uploader import WindUploader
from uploaders.leg_uploader import LegUploader
from uploaders.live_uploader import LiveUploader
from uploaders.marks_uploader import MarksUploader

def main():

    server = 'sic-match-analysis.database.windows.net'
    database = 'match-analysis'
    username = 'sic-admin'
    password = 'ZeilenIsLeuk!'
    driver= '{ODBC Driver 17 for SQL Server}'

    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = conn.cursor()    
    cursor.fast_executemany = True

    #path = "c:/data/powertracks/hwcs2020-round1/regattas.json"
    #uploader = RegattaUploader()
    #uploader.upload(path, conn, cursor)

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