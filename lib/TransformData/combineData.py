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

class combineData():
    def __init__(self, eventSelection = Tokyo2019Test):
        self.eventSelection = eventSelection
        self.dataframes = {}

    def combineFiles(self, filenames = AllFilenames):
        self.dataframes = dict([(key,[]) for key in filenames])
        if 'positions' in filenames:
            self.dataframes['competitor_positions'] = []
        if 'entries' in filenames:
            self.dataframes['entries_race'] = []
        self.dataframes['regattas'] = []
        self.dataframes['races'] = []

        for serv in self.eventSelection:
            d = download.download(server = serv['name'], regattasContaining = serv['regattaNameContaining'],\
             racesContaining = serv['raceNameContaining'])

            regattas = d.getRegattas()
            self.dataframes['regattas'] += regattas

            for regatta in regattas:
                races = d.getRaces(regatta['name'])
                directory_regatta =  r'X:\TU_Delft\2_Master\3_Stage\2_Code\SAPDataAnalysis\\'+ outdirbase +serv['name'] + regattaLoc(regatta['name'])
                exclude = set(['races'])
                for root, dirs, files in os.walk(directory_regatta, topdown=True):
                    dirs[:] = [d for d in dirs if d not in exclude]
                    for fname in files:
                        filepath = root + os.sep + fname
                        filename = os.path.splitext(fname)[0]
                        if filepath.endswith(".json") and (filename in filenames):
                            with open(filepath) as json_file:
                                print('file extracted: ', filepath, 'in category:')
                                data = json.load(json_file)
                            dic_data = {'regatta': regatta['name'], 'data': data}
                            self.dataframes[filename].append(dic_data)
            #
            #
                for race in races:
                    race['regatta'] = regatta['name']
                    directory_race = r'X:\TU_Delft\2_Master\3_Stage\2_Code\SAPDataAnalysis\\'+ outdirbase +serv['name'] + raceLoc(regatta['name'], race['name'])
                    racedata = {}
                    for subdir, dirs, files in os.walk(directory_race):
                        for file in files:
                            filepath = subdir + os.sep + file
                            filename = os.path.splitext(file)[0]
                            if filepath.endswith(".json") and (filename in filenames):
                                with open(filepath) as json_file:
                                    print('file extracted: ', filepath, 'in category:')
                                    data = json.load(json_file)
                                dic_data = {'regatta': regatta['name'], 'race' : race['name'], 'data': data}
                                if filename == 'entries':
                                    self.dataframes['entries_race'].append(dic_data)
                                elif filename == 'positions':
                                    if 'competitor' in filepath:
                                        self.dataframes['competitor_positions'].append(dic_data)
                                else:
                                    self.dataframes[filename].append(dic_data)
                self.dataframes['races'] += races


        # print(dataframes['entries'])
        for feature, data in self.dataframes.items():
            self.dataframes[feature] = self.transformJsonToPD(data, feature = feature)

        ## don't print dataframes when it containts everything!!
        # print(dataframes)
        return self.dataframes           ## dictionairy with keys are filenames and pandaframe as value containing everything nicely structured
        ### letop entries bevat de algemen en per race specifieke dataframes

    def transformJsonToPD(self, data, feature):
        pd.set_option('display.max_columns', 500)
        if feature == 'regattas':
            regattas = pd.DataFrame(data)[['name', 'boatclass', 'courseAreaId']]
            return regattas

        elif feature == 'races':
            races = pd.DataFrame(data)
            races['regatta_race_id'] = races.regatta + ', ' + races.name
            races['regatta_raceShort_id'] = races.regatta + ', ' + races.name.apply(lambda x: x.split(' ')[0])
            races = races.drop(['name', 'id'], axis = 1)
            return races

        elif feature == 'entries':
            df = pd.DataFrame(data)
            df = self.expandRecord(df, 'data', columnsToKeep ='competitors')
            df = self.expandListToRows(df, 'competitors')
            df = self.expandRecord(df, 'competitors',  columnsToKeep ='name')
            df['regatta_competitor_id'] = df.regatta + ', ' + df.name
            df = df.drop('regatta', axis = 1)
            return df

        elif feature == 'windsummary':
            df = pd.DataFrame(data)
            df = self.expandListToRows(pd.DataFrame(data), 'data')
            df = self.expandRecord(df, 'data')
            df['regatta_raceShort_id'] = df.regatta + ', ' + df.racecolumn

            df = df.drop(['regatta', 'racecolumn'], axis = 1)
            return df

        elif feature == 'entries_race':
            df = self.expandRecord(pd.DataFrame(data), 'data').drop('name', axis = 1)
            df = self.expandListToRows(df, 'competitors')
            df = self.expandRecord(df, 'competitors', prefix = 'competitor_',
                                    columnsToKeep = ['id', 'name', 'nationality',
                                                    'boat.sailId',
                                                    'boat.boatClass.displayName'])

            df['regatta_race_id'] = df.regatta + ', ' + df.race
            df['regatta_race_competitor_id'] = df.regatta_race_id + ', ' + df.competitor_name
            df['regatta_race_competitorid_id'] =  df[['regatta', 'race', 'competitor_id']].apply(self.mergeColumns, axis=1)
            df = df.drop(['regatta', 'race'], axis = 1)
            return df

        elif feature == 'legs':
            df = pd.DataFrame(data).drop('regatta', axis = 1)
            df = self.expandRecord(df, 'data').drop('name', axis = 1)
            df = self.expandListToRows(df, 'legs')
            df = self.expandRecord(df, 'legs')
            df = df.drop_duplicates(subset = ['regatta', 'race', 'from', 'to']).reset_index()
            df['leg_nr'] = df.groupby(['regatta','race']).cumcount() + 1
            df = df.iloc[::-1]
            df['leg_nr_from_finish'] = df.groupby(['regatta','race']).cumcount() + 1
            df = df.iloc[::-1]
            df = self.expandListToRows(df, 'competitors')
            df = self.expandRecord(df, 'competitors', prefix = 'competitor_',
                                    ).drop('competitor_color', axis = 1)

            df['regatta_race_competitor_id'] = df.regatta + ', ' + df.race + ', ' + df.competitor_name
            df['regatta_race_competitor_to_id'] = df.regatta_race_competitor_id + ', ' + df.to
            df['regatta_race_competitor_legnr_id'] = df.regatta_race_competitor_id + ', ' + df.leg_nr.apply(str)
            df = df.drop(['regatta', 'race'], axis = 1)
            return df

        elif feature == "markpassings":
            df = pd.DataFrame(data)
            df = self.expandRecord(df, 'data').drop('bywaypoint', axis = 1)
            df = self.expandListToRows(df, 'bycompetitor')
            df = self.expandRecord(df, 'bycompetitor', columnsToKeep = ['markpassings', 'competitor.name'])
            df = self.expandListToRows(df, 'markpassings')
            df = self.expandRecord(df, 'markpassings').reset_index()
            df['timeasmillis'] = df['timeasmillis'].apply(lambda x: round(x, -4))
            df['begin_leg_ms'] = df.groupby(['regatta', 'race', 'competitor.name'])['timeasmillis'].transform(lambda x: x.shift())
            df = df.rename(columns={"timeasmillis": "end_leg_ms"})
            df = df.dropna(axis = 0) ## delete rows where begin time was not defined
            df['during_leg_ms'] = df.apply(lambda row: range(int(row['begin_leg_ms']),int(row['end_leg_ms']), 10000), axis = 1)
            df = self.expandListToRows(df, 'during_leg_ms')

            df['regatta_race_competitor_legnr_id'] = df.regatta + ', ' + df.race + ', ' + df['competitor.name']+ \
                                                ', ' + df.zeroBasedWaypointIndex.apply(str)
            df['regatta_race_competitor_time_id'] = df.regatta + ', ' + df.race + ', ' + df['competitor.name']+ \
                                                ', ' + df.during_leg_ms.apply(str)
            df = df.drop(['regatta', 'race'], axis = 1)
            return df

        elif feature == "course":
            df = pd.DataFrame(data)
            df = self.expandRecord(df, 'data').drop('name', axis = 1)
            df = self.expandListToRows(df, 'waypoints')
            df = self.expandRecord(df, 'waypoints', columnsToKeep =['name'])
            df['mark_nr'] = df.groupby(['regatta','race']).cumcount()
            df = df.iloc[::-1]
            df['mark_nr_from_finish'] = df.groupby(['regatta','race']).cumcount()
            df = df.iloc[::-1]

            df['regatta_race_to_id'] = df.regatta + ', ' + df.race + ', ' + df.name
            return df

        elif feature == 'firstlegbearing':
            df = pd.DataFrame(data)
            df = self.expandRecord(df, 'data')
            df['regatta_race_id'] = df.regatta + ', ' + df.race
            df = df.drop(['regatta','race'], axis = 1)
            return df

        elif feature == 'competitor_positions':
            df = pd.DataFrame(data).drop('regatta', axis = 1)
            df = self.expandRecord(df, 'data').drop('name', axis = 1)
            df = self.expandListToRows(df, 'competitors')
            df = self.expandRecord(df, 'competitors', columnsToKeep = ['name', 'track'])
            df = self.expandListToRows(df, 'track')
            df = self.expandRecord(df, 'track')
            df = df.rename(columns={"timepoint-ms": "timepoint_ms"})

            df['regatta_race_competitor_time_id'] =  df[['regatta', 'race', 'name']].apply(self.mergeColumns, axis=1) + \
                                          ', ' + df['timepoint_ms'].apply(str)
            df = df.drop(['regatta','race', 'name'], axis = 1)
            return df

        elif feature == 'maneuvers':
            df = pd.DataFrame(data)
            df = self.expandRecord(df, 'data')
            df = self.expandListToRows(df, 'bycompetitor')
            df = self.expandRecord(df, 'bycompetitor')
            df = self.expandListToRows(df, 'maneuvers' )
            df = self.expandRecord(df, 'maneuvers', columnsToDiscard = ['maneuverLoss.nauticalMiles',
                                        'maneuverLoss.seaMiles',
                                        'maneuverLoss.kilometers',
                                        'maneuverLoss.geographicalMiles',
                                        'maneuverLoss.centralAngleRad',
                                        'positionAndTime.type',
                                        'maneuverLoss'])
            df['regatta_race_competitorid_id'] = df[['regatta', 'race', 'competitor']].apply(self.mergeColumns, axis=1)
            return df

        elif feature == 'AvgSpeed_Per_Competitor-LegType':
            df = pd.DataFrame(data).drop('regatta', axis = 1)
            df = self.expandRecord(df, 'data', columnsToDiscard =['state',
                                    'calculationDuration-s'])
            df = self.expandListToRows(df, 'results')
            df = self.expandRecord(df, 'results')
            df = self.expandListToColumns(df, 'groupKey', ['competitor', 'leg_type'])
            df = self.expandListToRows(df, 'competitor')
            df = self.expandListToRows(df, 'leg_type')
            df = df.rename(columns = {'value': 'Speed (kts) (Average)'})

            df['regatta_competitor_id'] = df[['regatta', 'competitor']].apply(self.mergeColumns, axis=1)
            df = df.drop(columns = ['regatta', 'competitor', 'description', 'resultUnit'])
            return df
        else:
            return pd.DataFrame([])

    def mergeColumns(self, x):
        return ', '.join(x)

    def expandRecord(self, df, columnToExpand, prefix = '', columnsToKeep = None,
                        columnsToDiscard = None):
        exp = json_normalize(df[columnToExpand])
        if columnsToDiscard != None:
            exp = exp.drop(columns = columnsToDiscard)
        if columnsToKeep == None:
            columnsToKeep = exp.columns
        exp = exp[columnsToKeep]
        if prefix != '':
            exp.columns = [prefix + str(col) for col in exp.columns]
        return pd.concat([df, exp],
                axis=1).drop(columns = columnToExpand)

    def expandListToRows(self, df, lst_col):
        r = pd.DataFrame({
          col:np.repeat(df[col].values, df[lst_col].str.len())
          for col in df.columns.drop(lst_col)}
        ).assign(**{lst_col:np.concatenate(df[lst_col].values)})[df.columns]
        return r

    def expandListToColumns(self, df, lst_col, colNames):
        df[colNames] = pd.DataFrame(df[lst_col].values.tolist(), index= df.index)
        df = df.drop(lst_col, axis = 1)
        return df



if __name__ == "__main__":
    pd.set_option('display.max_columns', 500)
    # c = combineData(eventSelection = Tokyo2019Test)
    # df = c.run()

    filepath = 'data/output/tokyo2019/competitors.json'
    df = pd.read_json(filepath)   #.set_index(['regatta', 'name', 'competitor_id'])
    df = df.drop(['competitor_team_sailors', 'competitor_boat_boatClass_aliasNames'], axis = 1)
    plt.show()
    # print(rdf.head())
    print('everything done')
