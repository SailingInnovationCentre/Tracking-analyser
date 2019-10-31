import pyodbc

server = 'nerinedb.database.windows.net'
database = 'nerinedatabase'
username = 'nerineadmin'
password = 'ZeilenIsLeuk!'
driver= '{ODBC Driver 17 for SQL Server}'
cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)


cursor = cnxn.cursor()
# for row in cursor.tables():
#     print(row.table_name)

# create regattas table

cursor.execute("""
CREATE TABLE regattas
(regatta varchar(50) PRIMARY KEY,
boatType varchar(50) NULL)
""")

cursor.execute("""
CREATE TABLE races
(regatta varchar(50) NOT NULL,
race varchar(50) NOT NULL,
raceShort varchar(50) NOT NULL,
raceId varchar(50) NOT NULL,
maxWindSpd_kts decimal(20) NULL,
minWindSpd_kts decimal(20) NULL,
avgWindDir_deg decimal(20) NULL,
firstlegbearing_deg decimal(20) NULL
)
CREATE UNIQUE INDEX idx_rac ON races (regatta, race);
CREATE INDEX idx_reg ON races (regatta);

""")

cursor.execute("""
CREATE TABLE regatta_race_times
(regatta varchar(50) NOT NULL,
race varchar(50) NOT NULL,
timestamp_ms int NOT NULL,
lat_deg decimal(20) NULL,
lon_deg decimal(20) NULL,
WindSpd_kts decimal(20) NULL,
WindDir_deg decimal(20) NULL,
dampened_WindSpd_kts decimal(20) NULL,
dampened_WindDir_deg decimal(20) NULL)

CREATE UNIQUE INDEX idx ON regatta_race_times (regatta, race, timestamp_ms );
CREATE INDEX idx_race ON regatta_race_times (regatta, race);

""")

cursor.execute("""
CREATE TABLE regatta_race_comp
(regatta varchar(50) NOT NULL,
race varchar(50) NOT NULL,
comp_id varchar(50) NOT NULL,
rank int NULL)

CREATE UNIQUE INDEX idx ON regatta_race_comp (regatta, race, comp_id);
CREATE INDEX idx_race ON regatta_race_comp (regatta, race);
CREATE INDEX idx_comp ON regatta_race_comp (regatta, comp_id);

""")


cursor.execute("""
CREATE TABLE regatta_comp
(regatta varchar(50) NOT NULL,
comp_id varchar(50) NOT NULL,
comp_name text NULL,
avgSpeed decimal(20) NULL,
avgSpeed_upwind decimal(20) NULL,
avgSpeed_downwind decimal(20) NULL,
avgSpeed_reaching decimal(20) NULL,
traveledDistance_sum decimal(20) NULL,
traveledDistance_sum_upwind decimal(20) NULL,
traveledDistance_sum_downwind decimal(20) NULL,
traveledDistance_sum_reaching decimal(20) NULL,
overall_rank int NULL)

CREATE UNIQUE INDEX idx ON regatta_comp (regatta, comp_id);

""")

cursor.execute("""
CREATE TABLE regatta_race_leg_comp
(regatta varchar(50) NOT NULL,
race varchar(50) NOT NULL,
leg_nr int NOT NULL,
comp_id varchar(50) NOT NULL,
[competitor_distanceTraveled-m] decimal(20) NULL,
competitor_averageSOG_kts decimal(20) NULL,
competitor_tacks int NULL,
competitor_jibes int NULL,
competitor_penaltyCircles int NULL,
competitor_rank int NULL,
competitor_gapToLeader_s decimal(20) NULL,
competitor_gapToLeader_m decimal(20) NULL,
competitor_started bit NULL,
competitor_finished bit NULL
)

CREATE UNIQUE INDEX idx ON regatta_race_leg_comp (regatta, race, leg_nr, comp_id);
CREATE INDEX idx_rac_com ON regatta_race_leg_comp (regatta, race, comp_id);
CREATE INDEX idx_leg ON regatta_race_leg_comp (regatta, race, leg_nr);

""")

cursor.execute("""
CREATE TABLE regatta_race_leg
(regatta varchar(50) NOT NULL,
race varchar(50) NOT NULL,
leg_nr int NOT NULL,
fromWaypointId varchar(50) NULL,
toWaypointId varchar(50) NULL,
upOrDownwindLeg bit NULL,
leg_nr_from_finish int NULL,
distance decimal(20) NULL
)

CREATE UNIQUE INDEX idx ON regatta_race_leg (regatta, race, leg_nr);

""")

cursor.execute("""
CREATE TABLE regatta_race_marks
(regatta varchar(50) NOT NULL,
race varchar(50) NOT NULL,
waypointId varchar(50) NOT NULL,
lat decimal(20) NULL,
lon decimal(20) NULL,
waypointName text NULL
)

CREATE UNIQUE INDEX idx ON regatta_race_marks (regatta, race, waypointId);

""")


cursor.execute("""
CREATE TABLE regatta_race_leg_comp_time
(regatta varchar(50) NOT NULL,
race varchar(50) NOT NULL,
leg_nr int NOT NULL,
comp_id varchar(50) NOT NULL,
timestamp_ms int NOT NULL,
lat decimal(20) NULL,
lon decimal(20) NULL,
spd decimal(20) NULL,
bearing_deg decimal(20) NULL
)

CREATE UNIQUE INDEX idx ON regatta_race_leg_comp_time (regatta, race, leg_nr, comp_id, timestamp_ms);
CREATE INDEX idx_leg ON regatta_race_leg_comp_time (regatta, race, leg_nr, comp_id);

""")



cursor.execute("""
ALTER TABLE races
   ADD CONSTRAINT FK_races_regattas FOREIGN KEY (regatta)
      REFERENCES regattas (regatta)
      ON DELETE CASCADE
      ON UPDATE CASCADE
;
""")

cursor.execute("""
ALTER TABLE regatta_race_times
   ADD CONSTRAINT FK_regatta_race_times_regatta_race FOREIGN KEY (regatta, race)
      REFERENCES races (regatta, race)
      ON DELETE CASCADE
      ON UPDATE CASCADE
""")

cursor.execute("""
ALTER TABLE regatta_race_comp
   ADD CONSTRAINT FK_regatta_race_comp_regatta_race FOREIGN KEY (regatta, race)
      REFERENCES races (regatta, race),
    CONSTRAINT FK_regatta_race_comp_regatta_comp FOREIGN KEY(regatta, comp_id)
      REFERENCES regatta_comp (regatta, comp_id)
      ON DELETE CASCADE
      ON UPDATE CASCADE
""")

cursor.execute("""
ALTER TABLE regatta_race_leg_comp
   ADD CONSTRAINT FK_regatta_race_leg_comp_regatta_race_comp FOREIGN KEY (regatta, race, comp_id)
      REFERENCES regatta_race_comp (regatta, race,  comp_id),
      CONSTRAINT FK_regatta_race_leg_comp_regatta_race_leg FOREIGN KEY (regatta, race, leg_nr)
      REFERENCES regatta_race_leg (regatta, race, leg_nr)
      ON DELETE CASCADE
      ON UPDATE CASCADE
""")

cursor.execute("""
ALTER TABLE regatta_race_leg_comp_time
   ADD CONSTRAINT FK_regatta_race_leg_time_comp_regatta_race_leg_comp FOREIGN KEY (regatta, race, leg_nr, comp_id)
      REFERENCES regatta_race_leg_comp (regatta, race, leg_nr, comp_id)
      ON DELETE CASCADE
      ON UPDATE CASCADE
""")


cnxn.commit()
