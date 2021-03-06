-- If really starting from blank: 
-- CREATE SCHEMA powertracks; 

-- REGATTAS

DROP TABLE IF EXISTS powertracks.regattas;

CREATE TABLE powertracks.regattas
(
    regatta_id varchar(100) PRIMARY KEY,
    boatclass varchar(50),
    course_area_id varchar(40)
);


-- RACES

DROP TABLE IF EXISTS powertracks.races;

CREATE TABLE powertracks.races
(
    race_id varchar(40) PRIMARY KEY,      -- GUID
    regatta_id varchar(100),              -- just the name
    race_name varchar(50),                -- e.g. R4 (49ER)
    race_short_name varchar(50),          -- e.g. R4
    max_wind_speed_kts decimal(10,2), 
    min_wind_speed_kts decimal(10,2), 
    avg_wind_dir_deg decimal(10,2), 
    avg_wind_dir_deg_int int, 
    first_leg_bearing_deg decimal(10,2),
    first_leg_bearing_deg_int int,
    course_area_id int,
    start_of_race_ms bigint,
    start_of_race_dt datetime, 
    end_of_race_ms bigint,
    startline_rc_id varchar(40), 
    startline_rc_lat decimal(9,5), 
    startline_rc_lng decimal(9,5), 
    startline_pin_id varchar(40), 
    startline_pin_lat decimal(9,5), 
    startline_pin_lng decimal(9,5),
    startline_angle int, 
    startwind_angle int,
    startline_startwind_angle_diff int,
    visualize bit,
    dominant_bearing_1 int, 
    dominant_bearing_2 int,
    wind_dir_based_on_bearing int,
    startline_startwind_angle_diff_bearing int
);


-- COMPETITORS

DROP TABLE IF EXISTS powertracks.competitors; 

CREATE TABLE powertracks.competitors
(
    comp_id varchar(40) PRIMARY KEY,       -- GUID
    comp_name varchar(200),
    nationality varchar(3),
    regatta_id varchar(100),
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


-- RACE_COMP

DROP TABLE IF EXISTS powertracks.race_comp;

CREATE TABLE powertracks.race_comp
(
    race_comp_id int,      -- This is a primary key that is added later. 
    race_id varchar(40),
    comp_id varchar(40),
    rank int,
    start_pos_lat DECIMAL(9,5), 
    start_pos_lng DECIMAL(9,5), 
    start_pos_rel DECIMAL(9,3),
    start_pos_rel_rank DECIMAL(9,3)
);





-- LEGS

DROP TABLE IF EXISTS powertracks.legs; 

CREATE TABLE powertracks.legs
(
    leg_id varchar(40),    -- created by code. 
    race_id varchar(40),
    leg_nr int,
    from_waypoint_id varchar(40),
    from_waypoint_name varchar(20), 
    to_waypoint_id varchar(40),
    to_waypoint_name varchar(20),
    start_lat decimal(9,6),
    start_lng decimal(9,6), 
    end_lat decimal(9,6), 
    end_lng decimal(9,6)
);


-- COMP_LEG

DROP TABLE IF EXISTS powertracks.comp_leg; 

CREATE TABLE powertracks.comp_leg
(
    comp_leg_id varchar(40),    -- created by code. 
    leg_id varchar(40),
    comp_id varchar(40),
    start_ms bigint, 
    end_ms bigint, 
    distance_traveled_m decimal(9,2),
    average_sog_kts decimal(9,2),
    tacks int,
    jibes int,
    penalty_circles int,
    rank int,
    gap_to_leader_s decimal(9,2),
    gap_to_leader_m decimal(9,2),
    started bit,
    finished bit,
    rel_rank decimal(9,2), 
    avg_side decimal(9,2),
    most_left_side decimal(9,2),
    most_right_side decimal(9,2),
    avg_side_rel_rank decimal(9,2), 
    average_sog_rel_rank decimal(9,2), 
    distance_traveled_rel_rank decimal(9,2),
    average_sog_ratio_to_mean decimal(9,2),
    average_distance_ratio_to_mean decimal(9,2)
);


-- POSITIONS 

DROP TABLE IF EXISTS powertracks.positions; 

CREATE TABLE powertracks.positions
(
    comp_leg_id varchar(40), 
    timepoint_ms bigint,
    lat_deg decimal(9,6),
    lng_deg decimal(9,6),
    true_bearing_deg decimal(19,10),
    speed_kts decimal(9,3),
    calculated_wind_speed decimal(9,2),
    calculated_wind_direction decimal(9,2),
    relative_speed_kts decimal(9,3)
);

DROP TABLE IF EXISTS powertracks.pruned_positions; 

CREATE TABLE powertracks.pruned_positions
(
    comp_leg_id varchar(40), 
    timepoint_ms bigint,
    lat_deg decimal(9,6),
    lng_deg decimal(9,6),
    true_bearing_deg decimal(19,10),
    speed_kts decimal(9,3),
    calculated_wind_speed decimal(9,2),
    calculated_wind_direction decimal(9,2),
    relative_speed_kts decimal(9,3)
);


-- WIND

DROP TABLE IF EXISTS powertracks.wind; 

CREATE TABLE powertracks.wind (
    race_id varchar(40),                       -- Redundant, but can improve query speed. 
    timepoint_ms bigint,
    true_bearing_deg decimal(9,2),
    speed_kts decimal(9,2),
    speed_ms decimal(9,2),
    dampened_true_bearing_deg decimal(9,2),
    dampened_speed_kts decimal(9,2),
    dampened_speed_ms decimal(9,2),
    lat_deg decimal(9,6),
    lon_deg decimal(9,6)
);


-- MARKS

DROP TABLE IF EXISTS powertracks.marks;

CREATE TABLE powertracks.marks (
    mark_id varchar(40),
    mark_name varchar(50),
    race_id varchar(40)
);

DROP TABLE IF EXISTS powertracks.marks_positions; 

CREATE TABLE powertracks.marks_positions
(
    mark_id varchar(40),
    timepoint_ms bigint,
    race_id varchar(40),
    lat_deg decimal(9,6),
    lng_deg decimal(9,6)
);


-- COURSE AREAS

DROP TABLE IF EXISTS powertracks.course_areas;

CREATE TABLE powertracks.course_areas (
	id int PRIMARY KEY,
    course_area varchar(20),
    lat_deg decimal(9,6),
    lng_deg decimal(9,6),
);

INSERT INTO powertracks.course_areas(id, course_area, lat_deg, lng_deg)
VALUES 
    (1, 'Enoshima', 35.2927, 139.4918),
    (2, 'Fujisawa', 35.2638, 139.4867),
    (3, 'Kamakura', 35.2907, 139.5132),
    (4, 'Sagami',   35.2522, 139.5172),
    (5, 'Zushi',    35.2702, 139.5398),
    (6, 'Hayama',   35.2402, 139.5475);

-- Two auxiliary tables for PowerBI visualisation
CREATE TABLE powertracks.rank_filter
(
    id int primary key
);

CREATE TABLE powertracks.degree_selection
(
    angle_degrees int primary key, 
    angle_degrees_norm int,
);

CREATE TABLE powertracks.degrees
(
    deg int primary key
);



-- SAILING STYLE (niet nodig?)

DROP TABLE IF EXISTS powertracks.sailing_style;

CREATE TABLE powertracks.sailing_style
(
    id int primary key,
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

INSERT INTO powertracks.sailing_style
VALUES 
    (1, 'Oscillating', -1, .1, 0, .2, -.1, 0, .5, 1),
    (2, 'Persistent', .5, 1, .5, 1, -.2, .2, .5, 1),
    (3, 'Geographical', -.2, .2, .5, 1, -1, -.3, .3, -1),
    (4, 'Connect Pressure', -.5, 0, 0,.2, -1, -.8, -1, 0),
    (5, 'Random', 0,0, 0, 0, 0, 0, 0, 0);


