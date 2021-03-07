CREATE SCHEMA powertracks; 
GO; 

DROP TABLE IF EXISTS powertracks.regattas;

CREATE TABLE powertracks.regattas
(
    regatta_id varchar(50) PRIMARY KEY,
    boatclass varchar(50) NULL,
    course_area_id nvarchar(40) NULL
);

-- Add indexes for boatclass and course area id? 






CREATE TABLE powertracks.races
(
    race_id binary(16) NOT NULL,
    regatta_id varchar(50) NOT NULL,
    race varchar(50) NOT NULL,
    raceShort varchar(50) NOT NULL,
    fleet varchar(20),
    maxWindSpd_kts decimal(10,2) NULL,
    minWindSpd_kts decimal(10,2) NULL,
    avgWindDir_deg decimal(10,2) NULL,
    firstlegbearing_deg decimal(10,2) NULL,
    course_area_id int NULL,
    nr_competitors int NULL,
    startOfRace_ms bigint,
    endOfRace_ms bigint,
    start_wind_dir decimal(5,2),
    stl_bearing decimal(5,2),
    stl_bearing_diff_wind decimal(5,2),
    stl_fav_side varchar(10),
    sail_style_id int
);

CREATE UNIQUE CLUSTERED INDEX idx_rac ON powertracks.races (race_id);
CREATE INDEX idx_reg ON powertracks.races (regatta);




CREATE TABLE competitors
(
    regatta varchar(50) NOT NULL,
    comp_id binary(16) NOT NULL,
    comp_name varchar(100) NULL,
    nationality varchar(3) NULL,
    sailId varchar(10) NULL,
    [Speed (kts) (Average)] decimal(10,2) NULL,
    [Speed (kts) (Average) UPWIND] decimal(10,2) NULL,
    [Speed (kts) (Average) DOWNWIND] decimal(10,2) NULL,
    [Speed (kts) (Average) REACHING] decimal(10,2) NULL,
    [Distance Traveled (Sum)] decimal(10,2) NULL,
    [Distance Traveled (Sum) UPWIND] decimal(10,2) NULL,
    [Distance Traveled (Sum) DOWNWIND] decimal(10,2) NULL,
    [Distance Traveled (Sum) REACHING] decimal(10,2) NULL,
    [Speed (kts) (Average) null] decimal(10,2) NULL,
    [Distance Traveled (Sum) null] decimal(10,2) NULL,
    overall_rank int NULL,
    [Number of Maneuvers (Sum)] decimal(10,2) NULL
)

CREATE UNIQUE CLUSTERED INDEX idx ON competitors (regatta, comp_id);
CREATE INDEX idx_comp ON competitors (comp_id);




CREATE TABLE windsources (
    race_id binary(16) NOT NULL,
    typeName varchar(100),
    id varchar(50) NOT NULL,
    rc bit
);

CREATE UNIQUE CLUSTERED INDEX idx ON windsources (race_id, typeName, id);




CREATE TABLE wind (
    race_id binary(16) NOT NULL,
    windSource varchar(100) NOT NULL,
    windSource_id varchar(50) NULL,
    [trueBearing-deg] decimal(5,2) NULL,
    [speed-kts] decimal(5,2) NULL,
    [speed-m/s] decimal(5,2) NULL,
    [timepoint-ms] bigint NULL,
    [dampenedTrueBearing-deg] decimal(5,2) NULL,
    [dampenedSpeed-kts] decimal(5,2) NULL,
    [dampenedSpeed-m/s] decimal(5,2) NULL,
    [lat-deg] decimal(10,7) NULL,
    [lng-deg] decimal(10,7) NULL
);

CREATE UNIQUE CLUSTERED INDEX idx ON wind (race_id, windSource, windSource_id, [timepoint-ms]);
CREATE INDEX idx_race On wind (race_id);




CREATE TABLE legs
(
    race_id binary(16),
    leg_nr int NOT NULL,
    fromWaypointId binary(16) NULL,
    toWaypointId binary(16) NULL,
    [to] varchar(20) NULL,
    [from] varchar(20) NULL,
    upOrDownwindLeg bit NULL,
    leg_nr_from_finish int NULL,
    distance decimal(20,2) NULL,
    correlation_tacks decimal(5,4),
    correlation_side decimal(5,4),
    correlation_avgSOG decimal(5,4),
    correlation_traveledDistance decimal(5,4),
    correlation_jibes decimal(5,4),
    pos_startline_abs_x decimal(4,3)
    ,pos_startline_abs_y decimal(4,3)
    ,pos_startline_rel decimal(4,3)
    ,cor_side_pos_startline_abs decimal(4,3)
    ,cor_side_pos_startline_rel decimal(4,3)
    ,avg_spd decimal(5,3)
    ,[avg_distanceTraveled-m] decimal (6,2)
)

CREATE UNIQUE CLUSTERED INDEX idx_ ON legs (race_id, leg_nr);
CREATE INDEX idx_race ON legs (race_id);




CREATE TABLE race_comp
(
    race_id binary(16),
    comp_id binary(16) NOT NULL,
    regatta varchar(50) NOT NULL,
    rank int,
    pos_startline_abs_x decimal(3, 2),
    pos_startline_abs_y decimal(7, 5),
    pos_startline_rel decimal(4, 2) NULL
);

CREATE UNIQUE CLUSTERED INDEX idx ON race_comp (race_id, comp_id);
CREATE INDEX idx_race ON race_comp (race_id);
CREATE INDEX idx_comp ON race_comp (comp_id);



CREATE TABLE comp_leg
(
    race_id binary(16),
    leg_nr int NOT NULL,
    comp_id binary(16) NOT NULL,
    [competitor_distanceTraveled-m] decimal(10,2) NULL,
    [competitor_averageSOG-kts] decimal(5,2) NULL,
    competitor_tacks int NULL,
    competitor_jibes int NULL,
    competitor_penaltyCircles int NULL,
    competitor_rank int NULL,
    [competitor_gapToLeader-s] decimal(10,2) NULL,
    [competitor_gapToLeader-m] decimal(10,2) NULL,
    competitor_started bit NULL,
    competitor_finished bit NULL,
    avg_side decimal(5,2) NULL,
    most_left decimal(5,2) NULL,
    most_right decimal(5,2) NULL,
    rel_rank decimal(3,2) NULL,
    rel_averageSOG decimal (5,3) NULL, 
    rel_distanceTraveled decimal(5,3) NULL
)

CREATE UNIQUE CLUSTERED INDEX idx ON comp_leg (race_id, leg_nr, comp_id);
CREATE INDEX idx_rac_com ON comp_leg (race_id, comp_id);
CREATE INDEX idx_leg ON comp_leg (race_id, leg_nr);




CREATE TABLE positions
(
    race_id binary(16) NOT NULL,
    leg_nr int NULL,
    comp_id binary(16) NOT NULL,
    timepoint_ms bigint NOT NULL,
    [lat-deg] decimal(20,10) NULL,
    [lng-deg] decimal(20,10) NULL,
    [speed-kts] decimal(10,2) NULL,
    [truebearing-deg] decimal(10,2) NULL,
    calculated_windSpd decimal(10,2) NULL,
    calculated_windDir decimal(10,2) NULL,
    [rel_spd-kts] decimal(5,3)
)

CREATE UNIQUE CLUSTERED INDEX idx ON positions (race_id, leg_nr, comp_id, timepoint_ms ASC);
CREATE INDEX idx_legnr ON positions (leg_nr) 
CREATE INDEX idx_leg ON positions (race_id, leg_nr, comp_id);
CREATE INDEX idx_comp ON positions (race_id, comp_id)




CREATE TABLE courses (
    race_id binary(16) NOT NULL,
    name varchar(50) NULL,
    passingInstruction varchar(50) NULL,
    [controlPoint.@class] varchar(50) NULL,
    [controlPoint.name] varchar(50) NULL,
    [controlPoint.id] binary(16) NULL,
    [controlPoint.left.@class]varchar(50) NULL,
    [controlPoint.left.name] varchar(50) NULL,
    [controlPoint.left.id] binary(16) NULL,
    [controlPoint.left.type] varchar(50) NULL,
    [controlPoint.right.@class]varchar(50) NULL,
    [controlPoint.right.name] varchar(50) NULL,
    [controlPoint.right.id] binary(16) NULL,
    [controlPoint.right.type] varchar(50) NULL,
    [controlPoint.type] varchar(50) NULL,
    mark_nr int NOT NULL,
    mark_nr_from_finish int NULL
);

CREATE UNIQUE CLUSTERED INDEX idx ON courses (race_id, mark_nr);
CREATE INDEX idx_race ON courses (race_id);





CREATE TABLE marks (
    race_id binary(16) NOT NULL,
    id binary(16) NOT NULL,
    name varchar(50) NULL
);

CREATE UNIQUE CLUSTERED INDEX idx ON marks (race_id, id);
CREATE INDEX idx_race ON marks (race_id);

CREATE TABLE marks_positions
(
    race_id binary(16) NOT NULL,
    id binary(16) NOT NULL,
    [lat-deg] decimal(10,7) NULL,
    [lng-deg] decimal(10,7) NULL,
    [timepoint-ms] bigint,
);

CREATE UNIQUE CLUSTERED INDEX idx ON marks_positions (race_id, id, [timepoint-ms]);
CREATE INDEX idx_mrks ON marks_positions (race_id, id);




CREATE TABLE course_areas (
	id int,
    course_area varchar(20),
    lat_deg decimal(10,7),
    lng_deg decimal(10,7)
);

CREATE UNIQUE INDEX idx ON course_areas (id);

INSERT INTO course_areas(id, course_area, lat_deg, lng_deg)
VALUES (1, 'Enoshima', 35.1756, 139.2951),
(2, 'Fujisawa',35.1583, 139.2920),
(3, 'Kamakura', 35.1744, 139.3079),
(4, 'Sagami', 35.1513, 139.3103),
(5, 'Zushi', 35.1621, 139.3239),
(6, 'Hayama', 35.1441, 139.3285);




CREATE TABLE sailing_style
(
    id int NOT NULL,
    style varchar(50) NOT NULL,
    tacks_lower decimal(3,2),
    tacks_upper decimal(3,2),
    side_lower decimal(3,2),
    side_upper decimal(3,2),
    speed_lower decimal(3,2),
    speed_upper decimal(3,2),
    distance_lower decimal(3,2),
    distance_upper decimal(3,2)
)


CREATE UNIQUE CLUSTERED INDEX idx ON sailing_style (id);

INSERT INTO sailing_style
VALUES (1, 'Oscillating', -1, .1, 0, .2, -.1, 0, .5, 1),
(2, 'Persistent', .5, 1, .5, 1, -.2, .2, .5, 1),
(3, 'Geographical', -.2, .2, .5, 1, -1, -.3, .3, -1),
(4, 'Connect Pressure', -.5, 0, 0,.2, -1, -.8, -1, 0),
(5, 'Random', 0,0, 0, 0, 0, 0, 0, 0);




CREATE TABLE temp_markpassings
(
    regatta varchar(50) NOT NULL,
    race varchar(50) NOT NULL,
    race_id binary(16),
    comp_id binary(16) NOT NULL,
    leg_nr int NOT NULL,
    begin_leg_ms bigint NULL,
    end_leg_ms bigint NULL
);

CREATE UNIQUE INDEX idx ON temp_markpassings (regatta, race, leg_nr, comp_id);
CREATE CLUSTERED INDEX idx_2 ON temp_markpassings (regatta, race, comp_id);