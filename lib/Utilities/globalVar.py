raceFeatures = ['entries', 'firstlegbearing', 'markpassings', \
         'competitors/positions' , 'competitors/live', 'competitors/legs', \
         'marks/positions', 'course', 'times', 'targettime', 'wind', 'maneuvers']

BeginTime = '2012-01-01T10:12:03Z'
EndTime = '2019-12-31T10:12:03Z'
timeInt = '?fromtime=' + BeginTime + '&totime=' + EndTime

degMax = 360
degMin = 0
windDirectionNames = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S',
                      'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
windSpeedCats = [0, 1, 3, 6, 10, 16, 21, 27, 33 ]

## Servers containing information about Enoshima
Enoshima = [{'name' :  'tokyo2019', 'AllRegattas': True, 'regattaNameContaining': ''}, {'name' : \
 'hwcs2020-round1', 'AllRegattas' : True, 'regattaNameContaining': ''}, {'name' : 'www', 'AllRegattas' : \
 False, 'regattaNameContaining': 'Enoshima'}]

Tokyo2019TestEvent = [{'name' :  'tokyo2019', 'AllRegattas': True, 'regattaNameContaining': '', 'raceNameContaining': ''}]

Tokyo2019Test = [{'name' : 'tokyo2019', 'AllRegattas': False, 'regattaNameContaining': 'Laser', 'raceNameContaining': ''}]
Tokyo2019laserR = [{'name' : 'tokyo2019', 'AllRegattas': False, 'regattaNameContaining': 'Laser', 'raceNameContaining': 'R'}]

## Defaults
urlbase = "https://www.sapsailing.com/sailingserver/api/v1/"
generallandingpage = 'www'
outdirbase = r"data/raw/"

## Global
suffix = '.json'

AllFilenames = [
             'windsummary',
             'course',
             'entries',
             'firstlegbearing',
             'markpassings',
             # 'targettime',
             # 'times',
             # 'wind--fromtime=2012-01-01T10__12__03Z&totime=2019-12-31T10__12__03Z',
             'legs',
             'positions',
             'maneuvers',
             'AvgSpeed_Per_Competitor-LegType',
             'AvgSpeed_Per_Competitor',
             'DistanceTraveled_Per_Competitor-LegType',
             'DistanceTraveled_Per_Competitor',
             'Maneuvers_Per_Competitor',
             ]
