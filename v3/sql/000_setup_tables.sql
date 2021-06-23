-- If really starting from blank: 
CREATE SCHEMA powertracks3;

-- REGATTAS

DROP TABLE IF EXISTS powertracks3.regattas;

CREATE TABLE powertracks3.regattas
(
    regatta_id varchar(100) PRIMARY KEY,
    boatclass varchar(50),
    course_area_id varchar(40)
);


-- RACES

DROP TABLE IF EXISTS powertracks3.races;

CREATE TABLE powertracks3.races
(
    race_id varchar(40) PRIMARY KEY,      -- GUID
    regatta_id varchar(100),              -- just the name
    race_name varchar(50),                -- e.g. R4 (49ER)
    race_short_name varchar(50),          -- e.g. R4
    start_of_race_ms bigint,
    start_of_race_dt datetime, 
    end_of_race_ms bigint,
    end_of_race_dt datetime,
    startline_rc_lat decimal(9,5),
    startline_rc_lng decimal(9,5), 
    startline_pin_lat decimal(9,5),
    startline_pin_lng decimal(9,5),
    startline_angle int, 
    max_wind_speed_kts decimal(10,2),
    min_wind_speed_kts decimal(10,2),
    wind_dir_deg int,
    first_leg_bearing_deg int,
    dominant_bearing_1 int,
    dominant_bearing_2 int,
    wind_dir_based_on_bearing int,
    startline_startwind_angle_diff_bearing int
);


-- COMPETITORS

DROP TABLE IF EXISTS powertracks3.competitors;

CREATE TABLE powertracks3.competitors
(
    comp_id    varchar(40) PRIMARY KEY, -- GUID
    comp_name  varchar(200),
    regatta_id varchar(100)
);

-- COURSE AREAS

DROP TABLE IF EXISTS powertracks3.course_areas;

CREATE TABLE powertracks3.course_areas (
	id int PRIMARY KEY,
    course_area varchar(20),
    lat_deg decimal(9,6),
    lat_deg_to_km float,
    lng_deg decimal(9,6),
    lng_deg_to_km float
);

INSERT INTO powertracks.course_areas(id, course_area, lat_deg, lng_deg)
VALUES 
    (1, 'Enoshima', 35.2927, 139.4918),
    (2, 'Fujisawa', 35.2638, 139.4867),
    (3, 'Kamakura', 35.2907, 139.5132),
    (4, 'Sagami',   35.2522, 139.5172),
    (5, 'Zushi',    35.2702, 139.5398),
    (6, 'Hayama',   35.2402, 139.5475);
