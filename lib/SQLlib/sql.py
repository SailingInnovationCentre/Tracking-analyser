from sqlalchemy import *
from sqlalchemy.sql.expression import *
import pymysql
pymysql.install_as_MySQLdb()
import urllib
import pyodbc
import pandas as pd

class sql(object):
    # def __init__(self, Database = 'SAPTrackingData'):
        # quoted = urllib.parse.quote_plus('Driver={SQL Server};Server=LAPTOP-NERINE\MSSMLBIZ;Database=SAPTrackingData;Trusted_Connection=yes;')
        # self.engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted))

    def saveDataframes(self, dfs):
        # quoted = urllib.parse.quote_plus('Driver={SQL Server};Server=LAPTOP-NERINE\MSSMLBIZ;Database=SAPTrackingData;Trusted_Connection=yes;')
        # engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted))
        for feat, df in dfs.items():

            # id_cols = [col for col in list(df.columns) if ('id' in col)]
            # dtypes = dict([(key, VARCHAR(100)) for key in id_cols])

            print('also still doing this')
            df.to_sql(feat, schema='dbo', con = engine, index = False, if_exists = 'replace')

    def saveDataFrame(self, df, filename, keepExisting = True):
        # quoted = urllib.parse.quote_plus('Driver={SQL Server};Server=LAPTOP-NERINE\MSSMLBIZ;Database=SAPTrackingData;Trusted_Connection=yes;')
        # engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted))
        engine = create_engine('mysql://root:Dataisleuk!2019@localhost:3306/sap_track')
        print('Saving', filename, 'at SQL server')
        print(len(df))
        # id_cols = [col for col in list(df.columns) if ('id' in col)]
        # dtypes = dict([(key, VARCHAR(100)) for key in id_cols])
        if keepExisting:
            if_exists = 'append'
        else:
            if_exists = 'replace'
        print(if_exists)
        # df.to_sql(filename, schema='dbo', con = engine, index = False, if_exists = if_exists)
        df.to_sql(filename.lower(), schema='sap_track', con = engine, index = False, if_exists = 'replace')

        # with engine.connect() as con:
        #     con.execute('ALTER TABLE `'+ filename + '` ADD PRIMARY KEY (`ID_column`);')





if __name__ == "__main__":
    import pymysql
    pymysql.install_as_MySQLdb()
    import sqlalchemy
    engine = sqlalchemy.create_engine('mysql://root:Dataisleuk!2019@localhost:3306/demo')
    s = sql()
    # quoted = urllib.parse.quote_plus('Driver={SQL Server};Server=LAPTOP-NERINE\MSSMLBIZ;Database=SAPTrackingData;Trusted_Connection=yes;')
    # engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted))
    metadata = MetaData()

    dfregattas = pd.read_sql_table('regattas', engine, schema='demo')
    dfcomp = pd.read_sql_table('competitors', engine, schema='demo')

    dfregattas.to_sql('regatta1', schema='demo', con = engine, index = False, if_exists = 'append')
    dfcomp.to_sql('competitors1', schema='demo', con = engine, index = False, if_exists = 'append')

    list_md = {'name': 'regatta', 'columns': [{'name' : 'regatta', 'type' : String(60), 'primary_key' : False, 'nullable' : False, 'Foreignkey' : False },
                                            {'name' : 'regatta_id', 'type' : Integer, 'primary_key' : True, 'nullable' : False, 'Foreignkey' : False },] }
    regatta = Table('user', metadata,
        Column('user_id', Integer, primary_key=True),
        Column('user_name', String(16), nullable=False),
        Column('email_address', String(60), key='email'),
        Column('nickname', String(50), nullable=False),
    )

    user_prefs = Table('user_prefs', metadata,
        Column('pref_id', Integer, primary_key=True),
        Column('user_id', Integer, ForeignKey("user.user_id"), nullable=False),
        Column('pref_name', String(40), nullable=False),
        Column('pref_value', String(100))
    )

    metadata.create_all(engine)
    print('run sql finished')

#     from sqlalchemy import *
#     quoted = urllib.parse.quote_plus('Driver={SQL Server};Server=LAPTOP-NERINE\MSSMLBIZ;Database=SAPTrackingData;Trusted_Connection=yes;')
#     engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted))
#     metadata = MetaData()
#
#     metadata.drop_all(engine)
#     print('everything done')

    ### Connection to mysql

    # from pandas.io import sql
    # import pymysql
    # pymysql.install_as_MySQLdb()
    # import sqlalchemy
    # engine = sqlalchemy.create_engine('mysql://root:Dataisleuk!2019@localhost:3306/demo')
    # df.to_sql(name='competitors', con=engine, if_exists = 'replace')
