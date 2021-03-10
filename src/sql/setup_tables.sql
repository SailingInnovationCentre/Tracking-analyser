CREATE SCHEMA powertracks; 
GO; 

DROP TABLE IF EXISTS powertracks.regattas;

CREATE TABLE powertracks.regattas
(
    regatta_id varchar(50) PRIMARY KEY,
    boatclass varchar(50),
    course_area_id varchar(40)
);

-- Add indexes for boatclass and course area id? 






CREATE TABLE powertracks.races
(
    race_id varchar(40) PRIMARY KEY,      -- GUID
    regatta_id varchar(50),               -- just the name
    race_name varchar(50),                -- e.g. R4 (49ER)
    race_short_name varchar(50),          -- e.g. R4
    fleet varchar(20),
    max_wind_speed_kts decimal(10,2), 
    min_wind_speed_kts decimal(10,2), 
    avg_wind_dir_deg decimal(10,2), 
    first_leg_bearing_deg decimal(10,2),
    course_area_id int,
    nr_competitors int,
    start_of_race_ms bigint,
    end_of_race_ms bigint,
    start_wind_dir decimal(10,2),
    stl_bearing decimal(10,2),
    stl_bearing_diff_wind decimal(10,2),
    stl_fav_side varchar(10),
    sail_style_id int
);

CREATE UNIQUE CLUSTERED INDEX idx_rac ON powertracks.races (race_id);
CREATE INDEX idx_reg ON powertracks.races (regatta);




CREATE TABLE powertracks.competitors
(
    comp_id varchar(40) PRIMARY KEY,       -- GUID
    comp_name varchar(100),
    nationality varchar(3),
    regatta_id varchar(50),
    sail_id varchar(10),
    speed_kts_avg decimal(10,2),
    speed_kts_upwind_avg decimal(10,2),
    speed_kts_downwind_avg decimal(10,2),
    speed_kts_reaching_avg decimal(10,2),
    distance_sum decimal(10,2),
    distance_sum_upwind decimal(10,2),
    distance_sum_downwind decimal(10,2),
    distance_sum_reaching decimal(10,2),
    overall_rank int,
    sum_nr_maneuvers decimal(10,2)
);

CREATE UNIQUE CLUSTERED INDEX idx ON competitors (regatta, comp_id);
CREATE INDEX idx_comp ON competitors (comp_id);



CREATE TABLE powertracks.wind (
    race_id varchar(40),                       -- Redundant, but can improve query speed. 
    timepoint_ms bigint,
    true_bearing_deg decimal(5,2),
    speed_kts decimal(5,2),
    speed_ms decimal(5,2),
    dampened_true_bearing_deg decimal(5,2),
    dampened_speed_kts decimal(5,2),
    dampened_speed_ms decimal(5,2),
    lat_deg decimal(10,7),
    lon_deg decimal(10,7)
);




CREATE TABLE legs
(
    race_id varchar(40),
    leg_nr int,
    fromWaypointId binary(16),
    toWaypointId binary(16),
    [to] varchar(20),
    [from] varchar(20),
    upOrDownwindLeg bit,
    leg_nr_from_finish int,
    distance decimal(20,2),
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
    comp_id binary(16),
    regatta varchar(50),
    rank int,
    pos_startline_abs_x decimal(3, 2),
    pos_startline_abs_y decimal(7, 5),
    pos_startline_rel decimal(4, 2)
);

CREATE UNIQUE CLUSTERED INDEX idx ON race_comp (race_id, comp_id);
CREATE INDEX idx_race ON race_comp (race_id);
CREATE INDEX idx_comp ON race_comp (comp_id);



CREATE TABLE comp_leg
(
    race_id binary(16),
    leg_nr int,
    comp_id binary(16),
    [competitor_distanceTraveled-m] decimal(10,2),
    [competitor_averageSOG-kts] decimal(5,2),
    competitor_tacks int,
    competitor_jibes int,
    competitor_penaltyCircles int,
    competitor_rank int,
    [competitor_gapToLeader-s] decimal(10,2),
    [competitor_gapToLeader-m] decimal(10,2),
    competitor_started bit,
    competitor_finished bit,
    avg_side decimal(5,2),
    most_left decimal(5,2),
    most_right decimal(5,2),
    rel_rank decimal(3,2),
    rel_averageSOG decimal (5,3), 
    rel_distanceTraveled decimal(5,3)
)

CREATE UNIQUE CLUSTERED INDEX idx ON comp_leg (race_id, leg_nr, comp_id);
CREATE INDEX idx_rac_com ON comp_leg (race_id, comp_id);
CREATE INDEX idx_leg ON comp_leg (race_id, leg_nr);




CREATE TABLE positions
(
    race_id binary(16),
    leg_nr int,
    comp_id binary(16),
    timepoint_ms bigint,
    [lat-deg] decimal(20,10),
    [lng-deg] decimal(20,10),
    [speed-kts] decimal(10,2),
    [truebearing-deg] decimal(10,2),
    calculated_windSpd decimal(10,2),
    calculated_windDir decimal(10,2),
    [rel_spd-kts] decimal(5,3)
)

CREATE UNIQUE CLUSTERED INDEX idx ON positions (race_id, leg_nr, comp_id, timepoint_ms ASC);
CREATE INDEX idx_legnr ON positions (leg_nr) 
CREATE INDEX idx_leg ON positions (race_id, leg_nr, comp_id);
CREATE INDEX idx_comp ON positions (race_id, comp_id)




CREATE TABLE courses (
    race_id binary(16),
    name varchar(50),
    passingInstruction varchar(50),
    [controlPoint.@class] varchar(50),
    [controlPoint.name] varchar(50),
    [controlPoint.id] binary(16),
    [controlPoint.left.@class]varchar(50),
    [controlPoint.left.name] varchar(50),
    [controlPoint.left.id] binary(16),
    [controlPoint.left.type] varchar(50),
    [controlPoint.right.@class]varchar(50),
    [controlPoint.right.name] varchar(50),
    [controlPoint.right.id] binary(16),
    [controlPoint.right.type] varchar(50),
    [controlPoint.type] varchar(50),
    mark_nr int,
    mark_nr_from_finish int
);

CREATE UNIQUE CLUSTERED INDEX idx ON courses (race_id, mark_nr);
CREATE INDEX idx_race ON courses (race_id);





CREATE TABLE marks (
    race_id binary(16),
    id binary(16),
    name varchar(50)
);

CREATE UNIQUE CLUSTERED INDEX idx ON marks (race_id, id);
CREATE INDEX idx_race ON marks (race_id);

CREATE TABLE marks_positions
(
    race_id binary(16),
    id binary(16),
    [lat-deg] decimal(10,7),
    [lng-deg] decimal(10,7),
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
    id int,
    style varchar(50),
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
    regatta varchar(50),
    race varchar(50),
    race_id binary(16),
    comp_id binary(16),
    leg_nr int,
    begin_leg_ms bigint,
    end_leg_ms bigint
);

CREATE UNIQUE INDEX idx ON temp_markpassings (regatta, race, leg_nr, comp_id);
CREATE CLUSTERED INDEX idx_2 ON temp_markpassings (regatta, race, comp_id);