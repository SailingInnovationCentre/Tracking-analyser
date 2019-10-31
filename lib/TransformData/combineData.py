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
import re
import uuid


class combineData():
    def __init__(self, server = Tokyo2019Test[0]):
        self.server = server
        self.featureSaved =[]
        self.s = sql.sql()

    def saveJsonAtSQLServer(self, data, feature, **race):
        df = self.transformJsonToPD(data, feature)
        keep = (feature in self.featureSaved)
        self.s.saveDataFrame(df, filename = feature, keepExisting = keep )
        self.featureSaved.append(feature)
        return df


    def transformJsonToPD(self, data, feature, **race):
        pd.set_option('display.max_columns', 500)
        if feature == 'regattas':
            regattas = pd.DataFrame(data)[['name', 'boatclass', 'courseAreaId']]
            regattas = regattas.rename(columns = {'name' : 'regatta'})
            df = regattas[regattas['regatta'].str.contains(self.server['regattaNameContaining'])]
            return df

        elif feature == 'races':
            df = pd.DataFrame({k: [v] for k, v in data.items()}).drop(columns = 'regatta')
            df = self.expandRecord(df, 'data')
            df = self.expandListToRows(df, 'races')
            df = self.expandRecord(df, 'races')
            df = df.rename(columns={"name": "race", "id": "raceId"})
            df['raceShort'] = df.race.apply(lambda x: 'M' if ('Medal' in x) else 'R' + re.findall(r'\d+',x)[0])  # x.split(' ')[0]
            df['raceShort'] = df.raceShort.apply(lambda x: x if ('R0' not in x) else x.replace('R0', 'R'))
            df.raceId = df.raceId.apply(lambda x: uuid.UUID(r"".join(x.replace("-", ""))).bytes)
            return df

        elif feature == 'entries':
            df = pd.DataFrame({k: [v] for k, v in data.items()})
            df = self.expandRecord(df, 'data').drop(columns = 'name')
            df = self.expandListToRows(df, 'competitors')
            df = self.expandRecord(df, 'competitors')
            df = df[['regatta', 'name', 'id', 'nationality', 'boat.sailId' ]]
            df = df.rename(columns={"name": "comp_name",
                                    "id" : "comp_id",
                                    "boat.sailId" : "sailId"})
            df.comp_id = df.comp_id.apply(lambda x: uuid.UUID(x).bytes)
            return df

        elif feature == 'windsummary':
            df = pd.DataFrame(data)
            df = self.expandRecord(df, 'data').drop(columns = 'fleet')
            df = df.rename(columns={"racecolumn": "raceShort",
                                    "trueLowerboundWindInKnots": "minWindSpd_kts" ,
                                    "trueUppwerboundWindInKnots": "maxWindSpd_kts",
                                    "trueWindDirectionInDegrees": "avgWindDir_deg"})
            return df

        elif feature == 'entries_race':
            df = pd.DataFrame({k: [v] for k, v in data.items()})
            df = self.expandRecord(df, 'data').drop('name', axis = 1)
            df = self.expandListToRows(df, 'competitors')
            df = self.expandRecord(df, 'competitors', prefix = 'competitor_',
                                    columnsToKeep = ['id', 'name', 'nationality',
                                                    'boat.sailId',
                                                    'boat.boatClass.displayName'])
            return df

        elif feature == 'legs':
            df = pd.DataFrame({k: [v] for k, v in data.items()})
            df = df.drop('regatta', axis = 1)
            df = self.expandRecord(df, 'data').drop('name', axis = 1)
            df = self.expandListToRows(df, 'legs')
            df = self.expandRecord(df, 'legs')
            df = df.drop_duplicates(subset = ['regatta', 'race', 'from', 'to', 'fromWaypointId']).reset_index()
            df['leg_nr'] = df.groupby(['regatta','race']).cumcount() + 1
            df = df.iloc[::-1]
            df['leg_nr_from_finish'] = df.groupby(['regatta','race']).cumcount() + 1
            df = df.iloc[::-1]

            df = df[['race','regatta','fromWaypointId', 'from', 'toWaypointId', 'to','upOrDownwindLeg','leg_nr','leg_nr_from_finish']]
            df.toWaypointId = df.toWaypointId.apply(lambda x: uuid.UUID(x).bytes)
            df.fromWaypointId = df.fromWaypointId.apply(lambda x: uuid.UUID(x).bytes)

            return df

        elif feature == 'comp_leg':
            df = pd.DataFrame({k: [v] for k, v in data.items()})
            df = df.drop('regatta', axis = 1)
            df = self.expandRecord(df, 'data').drop('name', axis = 1)
            df = self.expandListToRows(df, 'legs')
            df = self.expandRecord(df, 'legs')
            df = df.drop_duplicates(subset = ['regatta', 'race', 'from', 'fromWaypointId' ]).reset_index()
            df['leg_nr'] = df.groupby(['regatta','race']).cumcount() + 1
            df = df.iloc[::-1]
            df['leg_nr_from_finish'] = df.groupby(['regatta','race']).cumcount() + 1
            df = df.iloc[::-1]
            df = self.expandListToRows(df, 'competitors')
            df = self.expandRecord(df, 'competitors', prefix = 'competitor_',
                                    ).drop('competitor_color', axis = 1)
            cols = ['index','leg_nr_from_finish', 'startOfRace-ms', 'from', 'fromWaypointId','to',
                                    'toWaypointId','upOrDownwindLeg', 'competitor_name', 'competitor_sailNumber',
                                    'competitor_timeSinceGun-ms', 'competitor_distanceSinceGun-m', 'competitor_distanceTraveledIncludingGateStart-m' ]
            cols= [c for c in cols if c in df.columns]
            df = df.drop(columns = cols)
            df = df.rename(columns = {'competitor_id': 'comp_id'})
            df.comp_id = df.comp_id.apply(lambda x: uuid.UUID(x).bytes)
            decimals = pd.Series([2,2,2,2], index=[ 'competitor_averageSOG-kts', 'competitor_distanceTraveled-m',
                                            'competitor_gapToLeader-s', 'competitor_gapToLeader-m'])
            df['competitor_gapToLeader-s'] = df['competitor_gapToLeader-s'].apply(lambda x: 0 if x < 0 else x) ## niet getest
            df = df.round(decimals)


            return df

        elif feature == "markpassings":
            df = pd.DataFrame({k: [v] for k, v in data.items()})
            df = self.expandRecord(df, 'data').drop('bywaypoint', axis = 1)
            df = self.expandListToRows(df, 'bycompetitor')
            df = self.expandRecord(df, 'bycompetitor', columnsToKeep = ['markpassings', 'competitor.id'])
            df = self.expandListToRows(df, 'markpassings')
            if df.empty:   ## bit of a hack, but some files contain no markpassings, so we have to skip them
                return df
            df = self.expandRecord(df, 'markpassings').reset_index()
            df['timeasmillis'] = df['timeasmillis'].apply(lambda x: round(x, -4))
            df['begin_leg_ms'] = df.groupby(['regatta', 'race', 'competitor.id'])['timeasmillis'].transform(lambda x: x.shift())
            df = df.rename(columns={"timeasmillis": "end_leg_ms",
                                    "competitor.id" : 'comp_id',
                                    "zeroBasedWaypointIndex" : 'leg_nr'})
            df = df.dropna(subset=['begin_leg_ms']) ## delete rows where begin time was not defined
            df = df[df.leg_nr != 0]
            df = df[['regatta', 'race', 'comp_id', 'leg_nr', 'begin_leg_ms', 'end_leg_ms']]
            df.comp_id = df.comp_id.apply(lambda x: uuid.UUID(x).bytes)

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
            df = df.rename(columns={"truebearingdegrees": "firstlegbearing_deg"})
            return df

        elif feature == 'competitor_positions':
            df = pd.DataFrame({k: [v] for k, v in data.items()}).drop('regatta', axis = 1)
            df = self.expandRecord(df, 'data').drop('name', axis = 1)
            df = self.expandListToRows(df, 'competitors')
            df = self.expandRecord(df, 'competitors', columnsToKeep = ['id', 'track'])
            df = self.expandListToRows(df, 'track')
            df = self.expandRecord(df, 'track')
            df = df.rename(columns={"timepoint-ms": "timepoint_ms", "id": "comp_id"})
            df.comp_id = df.comp_id.apply(lambda x: uuid.UUID(x).bytes)
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
            df = df.rename(columns = {'competitor' : 'comp_name'})
            return df

        elif feature in ['AvgSpeed_Per_Competitor', 'DistanceTraveled_Per_Competitor',
                        'Maneuvers_Per_Competitor']:
            df = pd.DataFrame({k: [v] for k, v in data.items()}).drop('regatta', axis = 1)
            df = self.expandRecord(df, 'data')
            df = self.expandListToRows(df, 'results')
            df = self.expandRecord(df, 'results')
            df = self.expandListToRows(df, 'groupKey')
            description = df.loc[0, 'description']
            df = df.rename(columns = {'groupKey' : 'comp_name', 'value' : description })
            df = df[['regatta', 'comp_name', description]]
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
            return df

        elif feature == 'times': ## begin en eindtijd race
            df = pd.DataFrame({k: [v] for k, v in data.items()}).drop(columns = 'regatta')
            df = self.expandRecord(df, 'data').drop(columns = 'name')
            df['regatta_race_id'] = df[['regatta', 'race']].apply(self.mergeColumns, axis=1)
            return df

        elif feature == 'wind':
            df = pd.DataFrame({k: [v] for k, v in data.items()}).drop(columns = 'regatta')
            df = self.expandRecord(df, 'data').drop(columns = 'name')
            df = df.drop(columns = 'availableWindSources') ## Weet niet waar dit nuttig voor zou zijn
            df = self.expandListToRows(df, 'windSources')
            df = self.expandRecord(df, 'windSources')
            df = self.expandListToRows(df, 'COMBINED')
            df = self.expandRecord(df, 'COMBINED').drop(columns = ['speed-m/s', 'dampenedSpeed-m/s'])
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
