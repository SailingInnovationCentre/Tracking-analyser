from sqlalchemy import create_engine
from sqlalchemy.sql.expression import *
from sqlalchemy.types import VARCHAR
import urllib
import pyodbc
import pandas as pd

class sql(object):
    def saveDataframes(self, dfs):
        quoted = urllib.parse.quote_plus('Driver={SQL Server};Server=LAPTOP-NERINE\MSSMLBIZ;Database=SAPTrackingData;Trusted_Connection=yes;')
        engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted))
        for feat, df in dfs.items():
            print('Saving', feat, 'at SQL server')

            # id_cols = [col for col in list(df.columns) if ('id' in col)]
            # dtypes = dict([(key, VARCHAR(100)) for key in id_cols])


            df.to_sql(feat, schema='dbo', con = engine, index = False, if_exists = 'replace')

if __name__ == "__main__":
    from sqlalchemy import *
    quoted = urllib.parse.quote_plus('Driver={SQL Server};Server=LAPTOP-NERINE\MSSMLBIZ;Database=SAPTrackingData;Trusted_Connection=yes;')
    engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted))
    metadata = MetaData()

    metadata.drop_all(engine)
    print('everything done')
