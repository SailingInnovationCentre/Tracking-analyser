import pyodbc
import json

from uploaders.regatta_uploader import RegattaUploader
from uploaders.race_uploader import RaceUploader

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

    uploader = RaceUploader()

    #path = "C:/data/powertracks/hwcs2020-round1/regattas/HWCS 2020 Round 1 - 49er/races.json"
    #dict_short_name_to_id = uploader.upload_races(path, conn, cursor)

    #path = "C:/data/powertracks/hwcs2020-round1/regattas/HWCS 2020 Round 1 - 49er/windsummary.json"
    #uploader.upload_windsummary(path, dict_short_name_to_id, conn, cursor)

    path = "C:/data/powertracks/hwcs2020-round1/regattas/HWCS 2020 Round 1 - 49er/races/M Medal (49ER)/firstlegbearing.json"
    race_id = "9c45be60-ad9f-0137-131d-06773f917276"
    uploader.upload_first_leg_bearing(path, race_id, conn, cursor)

    cursor.close()
    conn.close()

    print("reached the end.")


if __name__ == "__main__":
    main()