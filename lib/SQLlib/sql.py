from sqlalchemy import create_engine
import urllib
import pyodbc
import pandas as pd

class sql(object):
    def saveDataframes(self, dfs):
        quoted = urllib.parse.quote_plus('Driver={SQL Server};Server=LAPTOP-NERINE\MSSMLBIZ;Database=SAPTrackingData;Trusted_Connection=yes;')
        engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted))
        for feat, df in dfs.items():
            if feat !='positions': ## TODO put markpositions in positions
                print('Saving', feat, 'at SQL server')
                # print(df.head())
                df.to_sql(feat, schema='dbo', con = engine, if_exists = 'replace')
