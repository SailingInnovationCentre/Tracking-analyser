#!/usr/local/bin/python3

"""
Library to download desired data from SAP server and save in '.\data' folder

List of all possible data:
https://www.sapsailing.com/sailingserver/webservices/api/v1/index.html

https://hwcs2020-round1.sapsailing.com/sailingserver/api/v1/
https://tokyo2019.sapsailing.com/sailingserver/api/v1/
and other events

author: Nerine Usman
created: 03-09-2019
"""

import os, sys ,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
# sys.path.append('X:\\TU_Delft\\2_Master\\3_Stage\\2_Code\\SAPDataAnalysis\\lib')

import urllib, json, requests

from Utilities.converter import *
from Utilities.globalVar import *


## Defaults
urlbase = "https://www.sapsailing.com/sailingserver/api/v1/"
generallandingpage = 'www'
outdirbase = r"data/raw/"

## Global
suffix = '.json'


class download(object):
    def __init__(self, server = generallandingpage, outdir = outdirbase, \
     regattasContaining = '', racesContaining = ''):
        self.urlbase  = urlbase.replace(generallandingpage, server)
        self.outdir = outdir + server + '/'
        self.regattasContaining = regattasContaining
        self.racesContaining = racesContaining

    def run(self, NormalData = True, DataMining = True, WindSummary = True, \
     Entries = True):
        print('Collecting structure of server')
        self.saveRegattas()
        self.saveQueryIdentifiers()
        self.saveAllRaces()
        if Entries:
            print('Collecting entries')
            self.saveEntries()
        if NormalData:
            print('Collecting data for all races')
            self.saveDataRaces()
        if DataMining:
            print('Collecting data from data mining functions')
            self.saveDataMining()
        if WindSummary:
            print('Collecting data from windsummary')
            self.saveWindSummary()

    def saveData(self, loc):
        """ save data from server which is at loc """
        url = self.urlbase + loc
        url = url.encode('utf-8')

        # print(r)
        filename = self.outdir + webAddressToFilename(loc) + suffix

        if not os.path.exists(filename):
            try:
                r = requests.get(url).json()
                # r = json.loads(response.read())
            except ValueError:
                ## TODO: delete the right events from regatta list
                print("Oops! ", loc , " did not contain the right data for the races, it is deleted from the regatta list")
                return ValueError

            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'w') as outfile:
                print('Created new file:', filename)
                json.dump(r, outfile)

    def saveRegattas(self):
        loc = "regattas"
        self.saveData(loc)

    def saveQueryIdentifiers(self):
        loc = "regattas/datamining"
        self.saveData(loc)

    def saveRaces(self,regattaName):
        loc = "regattas/" + regattaName + "/races"
        self.saveData(loc)

    def saveEntries(self):
        for reg in self.getRegattas():
            # if regattasContaining in reg['name']:
                loc = "regattas/" + reg['name'] + "/entries"
                self.saveData(loc)

    def saveWindSummary(self):
        for reg in self.getRegattas():
            # if regattasContaining in reg['name']:
                loc = "regattas/" + reg['name'] + "/windsummary"
                self.saveData(loc)

    def saveAllRaces(self):
        for reg in self.getRegattas():
            # if regattasContaining in reg['name']:
                self.saveRaces(reg['name'])

    def saveDataRaces(self):
        for reg in self.getRegattas():
            # if regattasContaining in reg['name']:
                races = self.getRaces(reg['name'])
                for race in races:
                    raceloc = "regattas/" + reg['name'] + "/races/" +  race['name'] + "/"
                    for feat in raceFeatures:
                        timeInt = ''
                        if feat == 'wind':
                            timeInt = '?fromtime=' + BeginTime + '&totime=' + EndTime
                        self.saveData(raceloc + feat + timeInt)

    def saveDataMining(self):
        for reg in self.getRegattas():
            for qid in self.getQueryIdentifiers():
                loc = 'regattas/'+ reg['name'] + '/datamining/' + qid['Identifier']
                self.saveData(loc)

    def getData(self, loc):         ## TODO implement warning if not availible
        filename = webAddressToFilename(self.outdir + loc + suffix)
        with open(filename) as json_file:
            data = json.load(json_file)
        return data

    def getRegattas(self):
        loc = "regattas"
        regattas = self.getData(loc)
        regattas[:] = [tup for tup in regattas if (self.regattasContaining in tup['name'])]
        return regattas

    def getQueryIdentifiers(self):
        loc = "regattas/datamining"
        return self.getData(loc)

    def getRaces(self, regattaName):
        loc = "regattas/" + regattaName + "/races"
        races = self.getData(loc)['races']
        races[:] = [tup for tup in races if (self.racesContaining in tup['name'])]
        return races



if __name__ == "__main__":
    serv = Enoshima[0]
    print(serv)
    d = download(server = "hwcs2020-round1", regattasContaining = 'Laser')
    d.run(NormalData = False)


    print('everything done')
