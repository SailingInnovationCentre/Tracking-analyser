#!/usr/local/bin/python3

"""
Library to calculate stats of windsummaries

author: Nerine Usman
created: 05-09-2019
"""

import os, sys ,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
import pandas as pd
import matplotlib.pyplot as plt
import gmplot
import plotly.express as px
import itertools


import Download.download as download
from Utilities.converter import *
from Utilities.globalVar import *
from Visualisation.visualise import *

class wind(object):
    def __init__(self, eventSelection = Enoshima):
        self.eventSelection = eventSelection
        self.windsummary = []
        self.combineWindSummaries()
        self.combineWind()
        self.wind = self.addWindCategories(self.wind)
        self.n = self.windsummary.shape[0]

    def combineWindSummaries(self):
        totalws = []
        for serv in self.eventSelection:
            d = download.download(server = serv['name'], regattasContaining = serv['regattaNameContaining'],\
             racesContaining = serv['raceNameContaining'])
            for regatta in d.getRegattas():
                loc = "regattas/" + regatta['name'] + "/windsummary"
                windsummary = d.getData(loc)
                windsummary[:] = [tup for tup in windsummary if (d.racesContaining in tup['racecolumn'])]
                for race in windsummary:
                    race['regatta'] = regatta['name']
                totalws += windsummary
        self.windsummary = pd.DataFrame(totalws)
        return self.windsummary

    def combineWind(self):
        totalw = []
        for serv in self.eventSelection:
            d = download.download(server = serv['name'], regattasContaining = serv['regattaNameContaining'],\
             racesContaining = serv['raceNameContaining'])
            for regatta in d.getRegattas():
                regloc = "regattas/" + regatta['name'] + "/races/"
                for race in d.getRaces(regatta['name']):
                    loc = regloc + race['name'] + "/wind" + timeInt
                    wind = d.getData(loc)
                    winddata = wind['windSources'][0]['COMBINED']
                    for datapoint in winddata:
                        datapoint['regattaName'] = regatta['name']
                        datapoint['raceName'] = race['name']
                    totalw += winddata
        self.wind = pd.DataFrame(totalw)
        return self.wind

    def addWindCategories(self, df):
        df['windDirCat'] = df.apply (lambda row: degToWindName(row['dampenedTrueBearing-deg']), axis=1)
        df['WindSpdCat'] = df.apply (lambda row: spdToWindCats(row['dampenedSpeed-kts']), axis=1)
        return df

    def makeFrequenciesWind(self): ###TODO
        data_dict = {"Wind Direction": windDirectionNames, "Wind spd": windSpeedCats}

        rows = itertools.product(*data_dict.values())
        df = pd.DataFrame.from_records(rows, columns=data_dict.keys())
        df['Wind Speed'] = df.apply (lambda row: spdToWindCats(row['Wind spd']), axis=1)
        df = df.drop(['Wind spd'], axis=1)

        df['Frequency'] = df.apply (lambda row: self.countWindSamples(row['Wind Direction'], row['Wind Speed']), axis=1)

        return df

    def countWindSamples(self, dirCat, spdCat):
        df = self.wind
        df = df[(df['windDirCat']== dirCat) & (df['WindSpdCat'] == spdCat)]
        return df.shape[0]

    def getVariablesSummary(self):
        """ Get random regatta to find variables available in windsummary """
        d = download.download(server = Enoshima[0]['name'])
        reg = d.getRegattas()[0]
        loc = "regattas/" + reg['name'] + "/windsummary"
        windsummary = d.getData(loc)[0]
        return [*windsummary]

    def getVariables(self):
        """ Get random race to find variables available in windsummary """
        d = download.download(server = Enoshima[0]['name'])
        reg = d.getRegattas()[0]
        race = d.getRaces(reg["name"])[0]
        raceloc = "regattas/" + reg['name'] + "/races/" +  race['name'] + "/wind"
        loc = raceloc  + timeInt
        wind = d.getData(loc)
        windsources = wind['windSources'][0]
        combined = windsources['COMBINED'][0]
        return [*combined]


    def histWindSummary(self, windDir = [0,360]):
        if windDir[0]<= windDir[1]:
            condition = (windDir[0]<=self.windsummary['trueWindDirectionInDegrees']) \
             &  (self.windsummary['trueWindDirectionInDegrees']<= windDir[1])
        else:
            condition = (windDir[0]<=self.windsummary['trueWindDirectionInDegrees']) \
             |  (self.windsummary['trueWindDirectionInDegrees']<= windDir[1])
        subws = self.windsummary[condition]
        hist = subws.hist()

    def histWind(self):
        hist = self.wind.hist()

if __name__ == "__main__":
    x = 3
    wind = wind(eventSelection = Tokyo2019Test)
    print('pos variables windsummary', wind.getVariablesSummary())
    print('pos variables all wind', wind.getVariables())
    print('nr of observed races = ', wind.n)
    # wind.histWindDir() ### gives plot of spreading wind directions
    # wind.histWind() ### gives plot of spreading wind spds, opt: given directions
    # wind.histWind()
    # wind.histWindSummary()

    # plt.figure()
    # plt.plot(wind.wind['lng-deg'], wind.wind['lat-deg'], '.')
    # latitude_list = wind.wind['lat-deg']
    # longitude_list = wind.wind['lng-deg']
    # # wind.addWindCategories(wind.wind)
    windfreq = wind.makeFrequenciesWind()
    print(windfreq.head())
    ################
    # fig = visualise.plotWindFreq(windfreq)
    # fig.show()

    # px.set_mapbox_access_token('pk.eyJ1IjoibmVyaW5ldSIsImEiOiJjazA4Nnp6cGMwM3N4M2JteWw3c3ZpdjB1In0.wv-VE3NZ6K0hMobfSqkG4A')
    # fig = px.scatter_mapbox(wind.wind, lat="lat-deg", lon="lng-deg", color="speed-m/s",
    #               color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10)
    #
    # # fig = px.scatter_geo(wind.wind, locations="iso_alpha",
    #                      )
    # plt.show()



    #################
    # px.set_mapbox_access_token(open(".mapbox_token").read())
    # carshare = px.data.carshare()
    # fig = px.scatter_mapbox(carshare, lat="centroid_lat", lon="centroid_lon",     color="peak_hour", size="car_hours",
    #                   color_continuous_scale=px.colors.cyclical.IceFire, size_max=15, zoom=10)
    # fig.show()


    # print(wind.wind)
    # with pd.option_context('display.max_rows', 30, 'display.max_columns', 20):  # more options can be specified also
    #     print(wind.wind)

    # plot wind van een race tegen de tijd


    print('everything done')
