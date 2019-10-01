import os, sys, inspect, json
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import numpy as np
import pandas as pd
import requests
import itertools
from pandas.io.json import json_normalize
import matplotlib.pyplot as plt

import Download.download as download
from Utilities.converter import *
from Utilities.globalVar import *

class combineDataOud():

    def __init__(self, eventSelection = Tokyo2019Test):
        self.eventSelection = eventSelection

    def run(self):
        # # Combine data for one race all together
        # First get all the data from one racefolder
        gen_all = []
        comp_all = []
        for serv in self.eventSelection:
            d = download.download(server = serv['name'], regattasContaining = serv['regattaNameContaining'],\
             racesContaining = serv['raceNameContaining'])
            for regatta in d.getRegattas():
                loc = "regattas/" + regatta['name'] + "/races/"
                for race in d.getRaces(regatta['name'] ):
                    directory_race = r'X:\TU_Delft\2_Master\3_Stage\2_Code\SAPDataAnalysis\\'+ outdirbase +serv['name'] + raceLoc(regatta['name'], race['name'])
                    # directory_race = r'X:\TU_Delft\2_Master\3_Stage\2_Code\SAPDataAnalysis\data\raw\tokyo2019\regattas\Tokyo 2019 - 49er\races\R1 (49er)'
                    racedata = {}
                    # print(directory_race)
                    for subdir, dirs, files in os.walk(directory_race):
                        for file in files:
                            filepath = subdir + os.sep + file
                            if filepath.endswith(".json"):
                                with open(filepath) as json_file:
                                    print('file extracted: ', filepath)
                                    data = json.load(json_file)
                                racedata = {**racedata, **data}
                                continue
                            else:
                                continue
                    # racedata now contains all the information of one race
                    # Then we put everything together in a data frame, and set the index based on regatta and racename
                    df = pd.DataFrame([racedata])
                    df = df.set_index(['regatta', 'name'])
                    ind1 = df.index[0] ## contains regatta and race name index
                    # df

                    ## first we make the dataframe containing all general information about the race
                    gen_features = ['currentServerTime-ms',
                                     'delayToLive-ms',
                                     'durationMillis',
                                     'endOfRace-ms',
                                     'endOfTracking-ms',
                                     'liveTime',
                                     'newestTrackingEvent-ms',
                                     'startOfRace-ms',
                                     'startOfTracking-ms',
                                     'startTime',
                                     'timeSinceStart-s',
                                     'truebearingdegrees',
                                     'marks',
                                     'waypoints']
                    gen_race_df =df[list(set(gen_features) & set(df.columns))]

                    ## Next we make the different dataframes containing information per competitor, which we later concatinate
                    rel_df = []
                    sdf = json_normalize(df.loc[ind1 , "bycompetitor"])
                    sdf = sdf.assign(regatta = ind1[0]).assign(name = ind1[1])
                    sdf.columns = [col.replace('.', '_') for col in sdf.columns]
                    competitors = sdf.set_index(['regatta', 'name', 'competitor_id'])

                    mp_lst = list(competitors.loc[:, 'markpassings'].apply(self.markpassingsToDataFrame))
                    mp_df = pd.concat(mp_lst, axis = 0)
                    mp_df = mp_df.set_index(competitors.index)
                    mp_df.columns = ['_'.join(col).strip() for col in mp_df.columns.values]
                    rel_df.append(mp_df)

                    competitors = competitors.drop(['markpassings'], axis = 1)
                    rel_df.append(competitors)

                    # Next is the 'legs' feature. This one containes a lot of interesting data, regarding manouvres/ranks etc. per competitor
                    legs = json_normalize(df.loc[ind1 , "legs"])
                    legs = legs.loc[legs.astype(str).drop_duplicates().index].reset_index(drop = True)
                    legs['leg'] = legs.index
                    legs.loc[:,"leg"] = legs.loc[:,"leg"].apply(lambda x: "Leg_" + str(x) )
                    # We need to extract the data per leg and combine all the information into one pandas data frame
                    legs_data = []
                    for legnr in legs.index:
                        leg_df = json_normalize(legs.loc[legnr, 'competitors'])
                        leg_df = leg_df.assign(regatta = ind1[0]).assign(name = ind1[1])
                        leg_df = leg_df.assign(leg = legs.leg[legnr]).assign(legnr = legnr)\
                                .set_index(['regatta', 'name', 'id'])
                        legs_data.append(leg_df)
                    var = list(leg_df)
                    legs_df = pd.concat(legs_data, axis = 1)
                    legs_df.columns = pd.MultiIndex.from_tuples(itertools.product(legs.loc[:,"leg"],var) )
                    legs_df.columns = ['_'.join(col).strip() for col in legs_df.columns.values]
                    rel_df.append(legs_df)


                    # sdf = json_normalize(df.loc[ind1 , "competitors"])
                    # sdf = sdf.assign(regatta = ind1[0]).assign(name = ind1[1]).rename(columns={"id": "competitor_id"})
                    # tracks = sdf.set_index(['regatta', 'name', 'competitor_id'])
                    # rel_df.append(tracks)

                    comp_df = pd.concat(rel_df,axis=1)


                    ## combine all races in one list for the dataframes
                    gen_all.append(gen_race_df)
                    comp_all.append(comp_df)

        comp_all_df = pd.concat(comp_all, axis= 0, sort = True )
        gen_all_df = pd.concat(gen_all, axis= 0, sort = True )

        ## drop all columns which contain the same value for every row
        nunique = comp_all_df[comp_all_df.select_dtypes(exclude=['object']).columns].apply(pd.Series.nunique)
        cols_to_drop = nunique[nunique <= 1].index
        comp_all_df = comp_all_df.drop(cols_to_drop, axis=1)



        loc = r'data/output/' + self.eventSelection[0]['name'] + '/'
        filename = '/competitors.pkl'
        self.locSaved = loc + filename
        os.makedirs(os.path.dirname(self.locSaved), exist_ok=True)
        with open(self.locSaved, 'w', newline='\n') as f:
            df = gen_all_df.reset_index()
            df.to_json(f, index = True)
            print("dumped new file at: ", self.locSaved)
        return gen_all_df.reset_index()

    def markpassingsToDataFrame(self, markpassings):
        if markpassings != []:
            # print(competitors.loc[indcom1, 'markpassings'][0])
            list_of_dfs = [pd.DataFrame(x,index=[0]) for x in markpassings]
            list_of_dfs[0].drop('zeroBasedWaypointIndex', axis = 1)
            index = ['Mark_' + str(x.loc[0, 'zeroBasedWaypointIndex']) for x in list_of_dfs]

            mp = pd.concat(list_of_dfs, axis =1)
            var = list_of_dfs[0].columns
            mp.columns = pd.MultiIndex.from_tuples(itertools.product(index,var) )
            self.mp_columns = mp.columns
            return mp
        else:
            return pd.DataFrame(np.nan, index = [0], columns = self.mp_columns )


    # def expandTrack(self, track):
    #     dd = {}
    #     for d in track:
    #         for k, v in d.items():
    #             try:
    #                 dd[k].append(v)
    #             except KeyError:
    #                 dd[k] = []
    #     return dd
    #


if __name__ == "__main__":
    pd.set_option('display.max_columns', 500)
    # c = combineData(eventSelection = Tokyo2019Test)
    # df = c.run()

    filepath = 'data/output/tokyo2019/competitors.json'
    df = pd.read_json(filepath)   #.set_index(['regatta', 'name', 'competitor_id'])
    df = df.drop(['competitor_team_sailors', 'competitor_boat_boatClass_aliasNames'], axis = 1)


    ### to save df to sql data base:
    # from pandas.io import sql
    # import pymysql
    # pymysql.install_as_MySQLdb()
    # import sqlalchemy
    # engine = sqlalchemy.create_engine('mysql://root:Dataisleuk!2019@localhost:3306/demo')
    # df.to_sql(name='competitors', con=engine, if_exists = 'replace')
    ###

    # from pandas.io import sql
    # # import pymysql
    # # pymysql.install_as_MySQLdb()
    # import sqlalchemy
    # # import pymssql
    # import pyodbc
    # # conn = pymssql.connect(server='LAPTOP-NERINE/MSSMLBIZ', database='[MSSmallBusiness]')
    #
    # conn = pyodbc.connect('Driver={SQL Server};Server=LAPTOP-NERINE\MSSMLBIZ;Database=SAPTrackingData;Trusted_Connection=yes;')
    # # engine = sqlalchemy.create_engine('mssql://LAPTOP-NERINE/MSSMLBIZ/SAPTrackingData')
    # cursor = conn.cursor()
    # cursor.execute('SELECT * FROM SAPTrackingData.dbo.Table_1')
    # for row in cursor:
    #     print(row)
    # df.to_sql(name='competitors', con=conn, if_exists = 'replace')

    from sqlalchemy import create_engine
    import urllib
    import pyodbc
    import pandas as pd

    # df = pd.read_csv("./data.csv")

    quoted = urllib.parse.quote_plus('Driver={SQL Server};Server=LAPTOP-NERINE\MSSMLBIZ;Database=SAPTrackingData;Trusted_Connection=yes;')
    engine = create_engine('mssql+pyodbc:///?odbc_connect={}'.format(quoted))

    df.to_sql('VeryNewTable', schema='dbo', con = engine, if_exists = 'replace')




    # indcom1 = rdf.index[0]
    # print(rdf.index)
    # plt.plot(rdf.loc[indcom1, 'track_lat-deg'], rdf.loc[indcom1, 'track_lng-deg'])
    #
    # filepath = 'data/output/tokyo2019//new_csv.csv'
    # rdf = pd.read_csv(filepath, sep='\t').set_index(['regatta', 'name', 'competitor_id'])
    # indcom1 = rdf.index[0]
    # print(rdf.columns)
    # plt.plot(rdf.loc[indcom1, 'track_lat-deg'], rdf.loc[indcom1, 'track_lng-deg'])
    #
    plt.show()
    # print(rdf.head())
    print('everything done')
