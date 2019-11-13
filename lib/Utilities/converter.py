import os, sys ,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from Utilities.globalVar import *

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
    return "/regattas/" + regattaName + "/"

def raceLoc(regattaName, raceName):
    return regattaLoc(regattaName) + "races/" +  raceName + "/"


def idToText(id): #TODO move to utilities
    return "0x{}".format(id.hex().upper())

def toDeg(a):
    return a*360/(2*pi)

def toRad(a):
    return a*2*pi/360

def bearing(a,b): ## a and b in lat and longitude
    lat1 = toRad(a['lat-deg'])
    lat2 = toRad(b['lat-deg'])
    lon1 = toRad(a['lng-deg'])
    lon2 = toRad(b['lng-deg'])

    y = sin(lon2-lon1)*cos(lat2)
    x = cos(lat1)*sin(lat2)-sin(lat1)*cos(lat2)*cos(lon2-lon1)
    theta = atan2(y,x)
    return toDeg(theta)

def startline(track_df, pin, rc):
    #transform to equidistant field
    phi_0 = pin['lat-deg'] ## latitude
    l_0 = pin['lng-deg'] ## longitude
    x = np.array(cos(phi_0 * 2 * pi/360) * (track_df['lng-deg']- l_0))
    y = np.array( track_df['lat-deg']- phi_0)

    rc_x = cos(phi_0 * 2 * pi/360) * (rc['lng-deg']- l_0)
    rc_y = rc['lat-deg'] - phi_0

    #rotate and scale competitors
    theta = -atan2(rc_y,rc_x)
    T = np.matrix([[cos(theta), -sin(theta)],[sin(theta), cos(theta)]])
    X = T*np.matrix([x,y])
    rc = T*np.matrix([[rc_x],[rc_y]])
    X = X/rc[0]
#     plt.plot(X[0], X[1], '.')
#     plt.axis('equal')
#     plt.show()
    return X

def dist_race_style(race, style):
    dist = 0
    if not (style.tacks_lower <= race.correlation_tacks <= style.tacks_upper):
        d = min(abs(style.tacks_lower -race.correlation_tacks ),
                    abs(style.tacks_upper-race.correlation_tacks))/2
#         print('tacks {:.2}'.format(d), end = "\t")
        dist += d
    if not (style.side_lower <= abs(race.correlation_side) <= style.side_upper):
        d =  min(abs(style.side_lower -abs(race.correlation_side )),
                    abs(style.side_upper-abs(race.correlation_side)))
#         print('side {}'.format(d), end = "\t")
        dist += d
    if not (style.speed_lower <= race.correlation_avgSOG <= style.speed_upper):
        d = min(abs(style.speed_lower -race.correlation_avgSOG),
                    abs(style.speed_upper-race.correlation_avgSOG))
#         print('speed {}'.format(d), end = "\t")
        dist += d
    if not (style.distance_lower <= race.correlation_traveledDistance <= style.distance_upper):
        d = min(abs(style.distance_lower -race.correlation_traveledDistance ),
                    abs(style.distance_upper-race.correlation_traveledDistance))
#         print('distance {}'.format(d), end = "\t")
        dist += d
#     print()
    return dist

def sailing_style(race, styles):
    for idx, style in styles.iterrows():
        x = dist_race_style(race, style)
        styles.loc[idx, 'dist'] = x
#         print(style.style, style.id, x)
    return styles.loc[styles['dist'].idxmin(), 'id']

def windUrl(regName, raceName, windSource = '', windSourceId = ''):
    if len(windSourceId)>0:
        windSourceId = '&windsourceid={}'.format(windSourceId)
    url = 'https://www.sapsailing.com/sailingserver/api/v1/regattas/{}/races/{}/wind?windsource={}{}&fromtime=2012-01-01T10:12:03Z&totime=2050-12-31T10:12:03Z'.format(regName, raceName, windSource, windSourceId)
    return url

def dataUrl(regName, raceName, dataName):
    if dataName == 'positions_comp':
        path = 'competitors/positions'
    elif dataName  == 'legs':
        path = 'competitors/legs'
    elif dataName  == 'positions_marks':
        path = 'marks/positions'
    else:
        path == 'dataName'
    url = 'https://www.sapsailing.com/sailingserver/api/v1/regattas/{}/races/{}/{}'.format(regName, raceName, path)
    return url


def trackStatistics(track_df):
    #transform to equidistant field
    phi_0 = track_df['lat-deg'][0] ## latitude
    l_0 = track_df['lng-deg'][0] ## longitude
    x = np.array(cos(phi_0 * 2 * pi/360) * (track_df['lng-deg']- l_0))
    y = np.array( track_df['lat-deg']- phi_0)

    #rotate and scale to 0-1
    theta = -atan2(y[-1:],x[-1:])
    T = np.matrix([[cos(theta), -sin(theta)],[sin(theta), cos(theta)]])
    X = T*np.matrix([x,y])
    X = X/(X[0,-1:])

    #statistics
    avg_side = np.mean(X[1])/.25 * 100
    most_left = np.max(X[1]) /.5 * 100
    most_right = -np.min(X[1]) /.5 *100

    return avg_side, most_left, most_right


def coordinatesToEquiv(track_df, centre = True):
    if centre:
        phi_0 = track_df['lat-deg'][0] ## latitude
        l_0 = track_df['lng-deg'][0] ## longitude
    else:
        phi_0 = 35.160967
        l_0 = 139.309617
    x = np.array(cos(phi_0 * 2 * pi/360) * (track_df['lng-deg']- l_0))
    y = np.array( track_df['lat-deg']- phi_0)
    return np.array([x, y])

def getArea(race, areas):
    sql = """SELECT TOP (1) *
      FROM positions
      WHERE regatta = '""" + race['regatta'] + \
      """'and race = '"""+ race['race'] + \
      """'and leg_nr = 1"""
    track = pd.read_sql_query(sql, con = engine)
    if track.empty:
        print('Track of race {} was empty'.format(race.race))
        return -1
    loc = coordinatesToEquiv(track, centre = False).reshape(1,2)
    areas['distance'] = areas.apply(lambda x: np.linalg.norm( x.equid -loc, ord = 1), axis =  1)
    area_id = areas.loc[areas[['distance']].idxmin(), 'id'].values[0]
    return area_id

## Actions
def toSql(df, table, engine, regName, raceName):
    try:
        print('Trying to upload', end = '\r')
        df.to_sql(table, con = engine, index = False, if_exists = 'append')
        print('Succesfully uploaded {} for regatta: \t{}, race: \t{}'.format(table, regName, raceName))
    except IntegrityError as e:
        print('IntegrityError: Failed to upload to sql :for regatta: \t{}, race: \t{}'.format(regName, raceName))
        return e
