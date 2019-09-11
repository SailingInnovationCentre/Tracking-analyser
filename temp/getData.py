# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 12:13:58 2019

@author: Nerine
"""

## List of all possible data:
## https://www.sapsailing.com/sailingserver/webservices/api/v1/index.html

import urllib, json
import requests
import numpy as np
import matplotlib.pyplot as plt
url = "https://www.sapsailing.com/sailingserver/api/v1/regattas/WCS%202019%20Enoshima%20-%20Nacra%2017/races/R8/wind?fromtimeasmillis=1536814500000&totimeasmillis=1536817003572"


r = requests.get(url)
#print(r.json())

urlbase = "https://www.sapsailing.com/sailingserver/api/v1/"
regattaName = "WCS 2019 Enoshima - RS:X Women"
raceName = "R2"


def getListRaces(regattaName):
    url = urlbase + "/regattas/" + regattaName + "/races"
    r = requests.get(url).json()
    races = []
    for race in r['races']:
        races.append(race['name'])
    return races

def getEntries(regattaName,raceName):
    url = urlbase + "/regattas/" + regattaName + "/races/" + raceName + "/entries"
    r = requests.get(url).json()
    cmpts = []
    for cmpt in r['competitors']:
        cmpts.append(cmpt['name'])
    return cmpts

def getMarkPassingsByWayPoint(regattaName,raceName, nrBuoy):
    url = urlbase + "/regattas/" + regattaName + "/races/" + raceName + "/markpassings"
    r = requests.get(url).json()
    data_bw = r['bywaypoint'][nrBuoy]['markpassings']
    cmpts = []
    for cmpt in data_bw:
        cmpts.append(cmpt['competitor']['name'])
    return cmpts

def getBuoys(regattaName,raceName):
    url = urlbase + "/regattas/" + regattaName + "/races/" + raceName + "/markpassings"
    r = requests.get(url).json()
    data_bw = r['bywaypoint']
    b = []
    for buoy in data_bw:
        b.append(buoy['waypointName'])
    return b

def getBuoysPos(regattaName,raceName):
    url = urlbase + "/regattas/" + regattaName + "/races/" + raceName + "/marks/positions"
    r = requests.get(url).json()
    data = r['marks']
    name = []
    x = []
    y = []
    for mark in data:
        track = mark['track'][0]
        name.append(mark['name'])
        x.append(track['lng-deg'])
        y.append(track['lat-deg'])
    return name,x,y,data

getBuoys(regattaName,raceName)

def getTimeRoundingBuoy(regattaName, raceName, nrBuoy, competitor):
    url = urlbase + "/regattas/" + regattaName + "/races/" + raceName + "/markpassings"
    r = requests.get(url).json()
    data_bw = r['bywaypoint'][nrBuoy]['markpassings']
    for cmpt in data_bw:
        if cmpt['competitor']['name'] == competitor:
            time = cmpt['timeasmillis']
            return time

def getTrack(regattaName, raceName, competitor, nrBuoyStart = 0, nrBuoyEnd = -1):
    url = urlbase + "/regattas/" + regattaName + "/races/" + raceName + "/competitors/positions"
    r = requests.get(url).json()
    data = r['competitors']
    for entry in data:
        if entry['name'] == competitor:
            track = entry['track']
    starttime = getTimeRoundingBuoy(regattaName,raceName,nrBuoyStart, competitor)
    endtime = getTimeRoundingBuoy(regattaName,raceName,nrBuoyEnd, competitor)
    x = []
    y = []
    for pos in track:
        if starttime < pos['timepoint-ms']<endtime:
            x.append(pos['lng-deg'])
            y.append(pos['lat-deg'])
    return x,y

def getWindDir(regattaName, raceName):
    url = urlbase + "/regattas/" + regattaName + "/windsummary"
    r = requests.get(url).json()
    for val in r:
        if val['racecolumn'] == raceName:
            wd = val['trueWindDirectionInDegrees']
    return wd

def getTopThree(regattaName,raceName):
    finish = len(getBuoys(regattaName,raceName)) - 1
    ranking = getMarkPassingsByWayPoint(regattaName,raceName,finish)
    return ranking[0:3]

def plotRaceTrackTopThree(regattaName,raceName,nrBuoyStart = 0, nrBuoyEnd = -1):
    tt = getTopThree(regattaName,raceName)
    for sailor in tt:
        x,y = getTrack(regattaName,raceName,sailor, nrBuoyStart, nrBuoyEnd)
        plt.plot(x,y)
    plt.legend(tt)
    print('average wind direction = ', getWindDir(regattaName,raceName))

def plotMarks(regattaName, raceName):
    name ,x,y, __ = getBuoysPos(regattaName, raceName)
    fig, ax = plt.subplots()
    ax.scatter(x, y)
    for i, txt in enumerate(name):
        ax.annotate(txt, (x[i], y[i]))


def getMiddleStartLine(startbuoy1,startbuoy2):
    return (startbuoy1+startbuoy2)/2

def distanceToCentreLine(mark1, mark2, loc):
    return ((mark2[1]-mark1[1])*loc[0]  - (mark2[0]-mark1[0])*loc[1] + mark2[0]*mark1[1]-mark2[1]*mark1[0])/ np.linalg.norm(np.array(mark1)-np.array(mark2))

def leftOrRightFirstLeg(regattaName,raceName, competitor):
    track = getTrack(regattaName, raceName, competitor, nrBuoyStart, nrBuoyEnd)
    name, x, y, buoys = getBuoysPos(regattaName,raceName)
    sb = []
    for mark in buoys[0]:
        print(mark)
        if mark['name'] == 'Start':
            sb.append([mark[0]['lng-deg'], mark[0]['lat-deg']])
        if mark['name'] == 'Mark 1':
            mark1 = [mark[0]['lng-deg'], mark[0]['lat-deg']]
    msl = getMiddleStartline(sb[0],sb[1])
#    print(msl)
    side = []
    for val in track:
        x=2


plt.close()

races = getListRaces(regattaName)
entr = getEntries(regattaName,raceName)
first_buoy = getMarkPassingsByWayPoint(regattaName,raceName,1)
print(first_buoy)
#x,y = getTrack(regattaName, raceName, entr[0])

nrBuoy = 1
competitor = entr[0]
raceName = races[0]
nrBuoyStart = 0
nrBuoyEnd = 1

# leftOrRightFirstLeg(regattaName,raceName, competitor)
t = getTimeRoundingBuoy(regattaName, raceName, nrBuoy, competitor)
plotMarks(regattaName, raceName)
plotRaceTrackTopThree(regattaName,raceName, nrBuoyStart, nrBuoyEnd)
plt.show()




##X plot track for one competitor
##X Plot track of best three competitor
## Plot track of best three competitors for multiple races
## """" all with northern wind

##X times when rounding
##X track seperated per leg
## define going to the right or left
