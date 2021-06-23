import os
import os.path
import pyodbc

from uploaders.regatta_uploader import RegattaUploader
from uploaders.race_uploader import RaceUploader

class SapUploader:

    def __init__(self, base_path):
        self.conn, self.cursor = create_connection()
        self.base_path = base_path

    def start(self):
        self.truncate_tables()

        path = os.path.join(self.base_path, 'regattas.json')
        uploader = RegattaUploader()
        uploader.upload(path, self.cursor)

        regatta_dirs = get_immediate_subdirectories(self.base_path)
        for regatta_dir in regatta_dirs :

            if 'WCS 2019 Enoshima - RSX' not in regatta_dir:
                continue

            path = os.path.join(regatta_dir, 'regattas.json')
            uploader = RaceUploader()
            uploader.upload_races(path, self.cursor)

        self.conn.close()

    def truncate_tables(self):
        # for name in ('regattas', 'races', 'competitors', 'legs', 'comp_legs', 'positions'):
        for name in ('regattas', 'races', 'competitors'):
            self.cursor.execute(f'TRUNCATE TABLE powertracks3.{name}')
            self.cursor.commit()


def create_connection():
    server = 'sic-match-analysis.database.windows.net'
    database = 'match-analysis'
    username = 'sic-admin'
    password = 'ZeilenIsLeuk!'
    driver = '{ODBC Driver 17 for SQL Server}'

    conn = pyodbc.connect(
        'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
    cursor = conn.cursor()
    cursor.fast_executemany = True

    return conn, cursor

def find_races_dirs(root_path):
    return get_immediate_subdirectories(os.path.join(root_path, 'races'))


def get_immediate_subdirectories(a_dir):
    return [os.path.join(a_dir, name) for name in os.listdir(a_dir)
            if os.path.isdir(os.path.join(a_dir, name))]
