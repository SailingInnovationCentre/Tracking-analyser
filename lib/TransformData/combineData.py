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
import lib.SQLlib.sql as sql


class combineData():
    def __init__(self, eventSelection = Tokyo2019Test):
        self.eventSelection = eventSelection
        self.featureSaved =[]
        self.s = sql.sql()


    def combineFiles(self, filenames = AllFilenames):
        for serv in self.eventSelection:
            d = download.download(server = serv['name'], regattasContaining = serv['regattaNameContaining'],\
             racesContaining = serv['raceNameContaining'])

            regattas = d.getRegattas()
            self.saveJsonAtSQLServer(regattas, 'regattas')

            for regatta in regattas:
                races = d.getRaces(regatta['name'])
                directory_regatta =  r'X:\TU_Delft\2_Master\3_Stage\2_Code\SAPDataAnalysis\\'+ outdirbase +serv['name'] + regattaLoc(regatta['name']) ##TODO niet zo beun
                exclude = set(['races'])
                for root, dirs, files in os.walk(directory_regatta, topdown=True):
                    dirs[:] = [d for d in dirs if d not in exclude]
                    for fname in files:
                        filepath = root + os.sep + fname
                        filename = os.path.splitext(fname)[0]
                        if filepath.endswith(".json") and (filename in filenames):
                            with open(filepath) as json_file:
                                print('file extracted: ', filepath)
                                data = json.load(json_file)
                            dic_data = {'regatta': regatta['name'], 'data': data}
                            self.saveJsonAtSQLServer(dic_data, filename)

                            # self.dataframes[filename].append(dic_data)
            #
            #
                for race in races:
                    race['regatta'] = regatta['name']
                    directory_race = r'X:\TU_Delft\2_Master\3_Stage\2_Code\SAPDataAnalysis\\'+ outdirbase +serv['name'] + raceLoc(regatta['name'], race['name']) ##TODO niet zo beun
                    for subdir, dirs, files in os.walk(directory_race):
                        for file in files:
                            filepath = subdir + os.sep + file
                            filename = os.path.splitext(file)[0]
                            if filepath.endswith(".json") and (filename in filenames):
                                with open(filepath) as json_file:
                                    print('file extracted: ', filepath)
                                    data = json.load(json_file)
                                dic_data = {'regatta': regatta['name'], 'race' : race['name'], 'data': data}
                                if filename == 'entries':
                                    self.saveJsonAtSQLServer(dic_data, 'entries_race')
                                elif filename == 'positions':
                                    if 'competitor' in filepath:
                                        self.saveJsonAtSQLServer(dic_data, 'competitor_positions')
                                    elif 'marks' in filepath:
                                        self.saveJsonAtSQLServer(dic_data, 'marks_positions')
                                elif filename == 'wind--fromtime=2012-01-01T10__12__03Z&totime=2019-12-31T10__12__03Z':
                                        self.saveJsonAtSQLServer(dic_data, 'wind')
                                else:
                                    self.saveJsonAtSQLServer(dic_data, filename)
                self.saveJsonAtSQLServer(races, 'races')

    def saveJsonAtSQLServer(self, data, feature, **race):
        df = self.transformJsonToPD(data, feature)
        keep = (feature in self.featureSaved)
        self.s.saveDataFrame(df, filename = feature, keepExisting = keep )
        self.featureSaved.append(feature)

    def transformJsonToPD(self, data, feature, **race):
        pd.set_option('display.max_columns', 500)
        if feature == 'regattas':
            regattas = pd.DataFrame(data)[['name', 'boatclass', 'courseAreaId']]
            regattas = regattas.rename(columns = {'name' : 'regatta'})
            return regattas

        elif feature == 'races':
            races = pd.DataFrame(data)
            races['regatta_race_id'] = races.regatta + '_' + races.name
            races['regatta_raceShort_id'] = races.regatta + '_' + races.name.apply(lambda x: x.split(' ')[0])
            # races = races.drop(['name', 'id'], axis = 1)
            return races

        elif feature == 'entries':
            df = pd.DataFrame({k: [v] for k, v in data.items()})
            df = self.expandRecord(df, 'data', columnsToKeep ='competitors')
            df = self.expandListToRows(df, 'competitors')
            df = self.expandRecord(df, 'competitors',  columnsToKeep ='name')
            df['regatta_competitor_id'] = df.regatta + '_' + df.name
            # df = df.drop('regatta', axis = 1)
            return df

        elif feature == 'windsummary':
            df = pd.DataFrame(data)
            df = self.expandRecord(df, 'data')
            df['regatta_raceShort_id'] = df.regatta + '_' + df.racecolumn

            # df = df.drop(['regatta', 'racecolumn'], axis = 1)
            return df

        elif feature == 'entries_race':
            df = pd.DataFrame({k: [v] for k, v in data.items()})
            df = self.expandRecord(df, 'data').drop('name', axis = 1)
            df = self.expandListToRows(df, 'competitors')
            df = self.expandRecord(df, 'competitors', prefix = 'competitor_',
                                    columnsToKeep = ['id', 'name', 'nationality',
                                                    'boat.sailId',
                                                    'boat.boatClass.displayName'])

            df['regatta_race_id'] = df.regatta + '_' + df.race
            df['regatta_race_competitor_id'] = df.regatta_race_id + '_' + df.competitor_name
            df['regatta_race_competitorid_id'] =  df[['regatta', 'race', 'competitor_id']].apply(self.mergeColumns, axis=1)
            # df = df.drop(['regatta', 'race'], axis = 1)
            return df

        elif feature == 'legs':
            df = pd.DataFrame({k: [v] for k, v in data.items()})
            df = df.drop('regatta', axis = 1)
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

            df['regatta_race_competitor_id'] = df.regatta + '_' + df.race + '_' + df.competitor_name
            df['regatta_race_competitor_to_id'] = df.regatta_race_competitor_id + '_' + df.to
            df['regatta_race_competitor_legnr_id'] = df.regatta_race_competitor_id + '_' + df.leg_nr.apply(str)
            # df = df.drop(['regatta', 'race'], axis = 1)
            return df

        elif feature == "markpassings":
            df = pd.DataFrame({k: [v] for k, v in data.items()})
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

            df['regatta_race_competitor_legnr_id'] = df.regatta + '_' + df.race + '_' + df['competitor.name']+ \
                                                '_' + df.zeroBasedWaypointIndex.apply(str)
            df['regatta_race_competitor_time_id'] = df.regatta + '_' + df.race + '_' + df['competitor.name']+ \
                                                '_' + df.during_leg_ms.apply(str)
            # df = df.drop(['regatta', 'race', 'index'], axis = 1)
            return df

        elif feature == "course":
            df = pd.DataFrame({k: [v] for k, v in data.items()})
            df = self.expandRecord(df, 'data').drop('name', axis = 1)
            df = self.expandListToRows(df, 'waypoints')
            df = self.expandRecord(df, 'waypoints', columnsToKeep =['name'])
            df['mark_nr'] = df.groupby(['regatta','race']).cumcount()
            df = df.iloc[::-1]
            df['mark_nr_from_finish'] = df.groupby(['regatta','race']).cumcount()
            df = df.iloc[::-1]

            df['regatta_race_to_id'] = df.regatta + '_' + df.race + '_' + df.name
            return df

        elif feature == 'firstlegbearing':
            df = pd.DataFrame({k: [v] for k, v in data.items()})
            df = self.expandRecord(df, 'data')
            df['regatta_race_id'] = df.regatta + '_' + df.race
            # df = df.drop(['regatta','race'], axis = 1)
            return df

        elif feature == 'competitor_positions':
            df = pd.DataFrame({k: [v] for k, v in data.items()}).drop('regatta', axis = 1)
            df = self.expandRecord(df, 'data').drop('name', axis = 1)
            df = self.expandListToRows(df, 'competitors')
            df = self.expandRecord(df, 'competitors', columnsToKeep = ['name', 'track'])
            df = self.expandListToRows(df, 'track')
            df = self.expandRecord(df, 'track')
            df = df.rename(columns={"timepoint-ms": "timepoint_ms"})

            df['regatta_race_competitor_time_id'] =  df[['regatta', 'race', 'name']].apply(self.mergeColumns, axis=1) + \
                                          '_' + df['timepoint_ms'].apply(str)
            # df = df.drop(['regatta','race', 'name'], axis = 1)
            return df

        elif feature == 'maneuvers':
            df = pd.DataFrame({k: [v] for k, v in data.items()})
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

        elif feature in ['AvgSpeed_Per_Competitor-LegType', 'DistanceTraveled_Per_Competitor-LegType']:
            df = pd.DataFrame({k: [v] for k, v in data.items()}).drop('regatta', axis = 1)
            df = self.expandRecord(df, 'data', columnsToDiscard =['state',
                                    'calculationDuration-s'])
            df = self.expandListToRows(df, 'results')
            df = self.expandRecord(df, 'results')
            df = self.expandListToColumns(df, 'groupKey', ['competitor', 'leg_type'])
            df = self.expandListToRows(df, 'competitor')
            df = self.expandListToRows(df, 'leg_type')
            description = df.loc[0, 'description']


            df = df.pivot_table(index = ['regatta', 'competitor'], columns = 'leg_type', values = 'value')
            df.columns = [' '.join([description, col]) for col in df.columns]
            df = df.reset_index()
            df['regatta_competitor_id'] = df[['regatta', 'competitor']].apply(self.mergeColumns, axis=1)
            return df

        elif feature in ['AvgSpeed_Per_Competitor', 'DistanceTraveled_Per_Competitor',
                        'Maneuvers_Per_Competitor']:
            df = pd.DataFrame({k: [v] for k, v in data.items()}).drop('regatta', axis = 1)
            df = self.expandRecord(df, 'data')
            df = self.expandListToRows(df, 'results')
            df = self.expandRecord(df, 'results')
            df = self.expandListToRows(df, 'groupKey')
            description = df.loc[0, 'description']
            df = df.rename(columns = {'groupKey' : 'competitor', 'value' : description })

            df['regatta_competitor_id'] = df[['regatta', 'competitor']].apply(self.mergeColumns, axis=1)
            df = df[['regatta_competitor_id', 'regatta', 'competitor', description]]
            return df

        elif feature == 'targettime':
            df = pd.DataFrame({k: [v] for k, v in data.items()})
            df = self.expandRecord(df, 'data')
            df = self.expandListToRows(df, 'legs')
            df = self.expandRecord(df, 'legs')
            df['leg_nr'] = df.groupby(['regatta','race']).cumcount() + 1
            df = df.iloc[::-1]
            df['leg_nr_from_finish'] = df.groupby(['regatta','race']).cumcount() + 1
            df = df.iloc[::-1]

            df['regatta_race_legnr_id'] = df[['regatta', 'race']].apply(self.mergeColumns, axis=1) + \
                                            '_' + df.leg_nr.apply(str)
            # df = df.drop(columns = ['regatta', 'race'])
            return df

        elif feature == 'times': ## begin en eindtijd race
            df = pd.DataFrame({k: [v] for k, v in data.items()}).drop(columns = 'regatta')
            df = self.expandRecord(df, 'data').drop(columns = 'name')
            df['regatta_race_id'] = df[['regatta', 'race']].apply(self.mergeColumns, axis=1)
            # df = df.drop(columns = ['regatta', 'race', 'markPassings', 'legs'])
            return df

        elif feature == 'wind':
            df = pd.DataFrame({k: [v] for k, v in data.items()}).drop(columns = 'regatta')
            df = self.expandRecord(df, 'data').drop(columns = 'name')
            df = df.drop(columns = 'availableWindSources') ## Weet niet waar dit nuttig voor zou zijn
            df = self.expandListToRows(df, 'windSources')
            df = self.expandRecord(df, 'windSources')
            df = self.expandListToRows(df, 'COMBINED')
            df = self.expandRecord(df, 'COMBINED')

            df['timepoint-ms'] = df['timepoint-ms'].apply(lambda x: round(x, -3))

            df['regatta_race_id'] = df[['regatta', 'race']].apply(self.mergeColumns, axis=1)
            df['regatta_race_time_id'] = df.regatta_race_id  + '_' + df['timepoint-ms'].apply(str)
            m = df['regatta_race_time_id'].duplicated(keep='first')
            # print(sum(m), len(df))
            df = df[~m]                      ### delete duplicate id's
            # df = df.drop(columns = ['race', 'regatta'])
            return df

        elif feature == 'marks_positions':
            df = pd.DataFrame({k: [v] for k, v in data.items()}).drop(columns = 'regatta')
            df = self.expandRecord(df, 'data').drop(columns = 'name')
            df = self.expandListToRows(df, 'marks')
            df = self.expandRecord(df, 'marks')
            df = self.expandListToRows(df, 'track')
            df = self.expandRecord(df, 'track')

            df['regatta_race_mark_id'] = df[['regatta', 'race', 'name']].apply(self.mergeColumns, axis=1)
            df['regatta_race_mark_time_id'] = df.regatta_race_mark_id + '_' + df['timepoint-ms'].apply(str)
            # df = df.drop(columns = ['regatta', 'race'])
            return df
        else:
            print('WARNING: empty dataframe')
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
