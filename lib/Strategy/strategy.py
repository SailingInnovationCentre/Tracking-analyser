import os, sys ,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

class strategy(object):
    def __init__(regattaName = regattaName, raceName = raceName, competitor = competitorName):
        self.regattaName = regattaName
        self.raceName = raceName
        self.competitor = competitor
        x=2

    def avgLeftRight(self, leg):
        track = d.getTrack(self.regattaName, self.raceName, self.competitor, leg)
        return

if __name__ == "__main__":
    s = strategy(regattaName = "Tokyo 2019 - 49er", raceName = "R1 (49er)", competitor = "Frei/delpech" )
    s.LeftRight(1)
