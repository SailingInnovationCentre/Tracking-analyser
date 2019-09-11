raceFeatures = ['entries', 'firstlegbearing', 'markpassings', \
         'competitors/positions' , 'competitors/live', 'competitors/legs', \
         'marks/positions', 'course', 'times', 'targettime', 'wind']

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

Tokyo2019Test = [{'name' : 'tokyo2019', 'AllRegattas': True, 'regattaNameContaining': 'Laser Radial', 'raceNameContaining': ''}]
Tokyo2019 = [{'name' : 'tokyo2019', 'AllRegattas': True, 'regattaNameContaining': '', 'raceNameContaining': ''}]
