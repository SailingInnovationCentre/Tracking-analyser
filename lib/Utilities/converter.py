import os, sys ,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from Utilities.globalVar import *

class degInterval(object):
    def __init__(self, middle, deviation):
        self.lower = middle - abs(deviation)
        self.upper = middle + abs(deviation)

    def __contains__(self, item):
        a = self.lower <= item <= self.upper
        b,c = False, False
        if self.upper >= degMax:
            b = degMin <= item <= (self.upper - degMax)
        if self.lower <= degMin:
            c = self.lower  + degMax <= item <= degMax
        return a or b or c


def filenameToWebAddress(filename):
    wa = filename.replace('---', '\\' )
    wa = wa.replace('__', ':' )
    wa = wa.replace('--', '?')
    return wa

def webAddressToFilename(webAddress):
    f = webAddress.replace('\\','---')
    f = f.replace(':', '__')
    f = f.replace('?', '--')
    return f

def regattaLoc(regattaName):
    return "regattas/" + regattaName + "/"

def raceLoc(regattaName, raceName):
    return regattaLoc(regattaName) + "races/" +  raceName + "/"

def degToWindName(deg):
    n = len(windDirectionNames)
    intSize = degMax/n
    for i in range(0,n):
        if deg in degInterval(i*intSize, intSize/2):
            return windDirectionNames[i]
    return None

def spdToWindCats(spd):
    n = len(windSpeedCats)
    for i in range(0,n-1):
        if windSpeedCats[i] <= spd < windSpeedCats[i+1]:
            return str(windSpeedCats[i]) + ' - ' + str(windSpeedCats[i+1]) + ' '
    return str(windSpeedCats[-1]) + "+ "
