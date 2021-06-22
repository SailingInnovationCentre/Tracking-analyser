-- Step 0: Easy updates in races table. 

update powertracks.races 
set first_leg_bearing_deg_int = round(first_leg_bearing_deg, 0) % 360, avg_wind_dir_deg_int = round(avg_wind_dir_deg, 0) % 360;

update powertracks.races 
set start_of_race_dt = DATEADD(HOUR, 9, DATEADD(MILLISECOND, start_of_race_ms  % 1000, DATEADD(SECOND, start_of_race_ms / 1000, '19700101')));

update powertracks.races set visualize = 1; 

insert into powertracks.races(race_id, visualize) values ('dummy', 0); 

-- Some races do not link to a regatta, so we need to add these regattas manually. 
select race_id, race_name, r.regatta_id, rg.regatta_id
from powertracks.regattas rg
right outer join powertracks.races r on r.regatta_id = rg.regatta_id
where rg.regatta_id is null;

insert into powertracks.regattas(regatta_id, boatclass) values ('Tokyo 2019 - Nacra 17', 'Nacra 17 Foiling');
insert into powertracks.regattas(regatta_id, boatclass) values ('HWCS 2020 Round 1 - Nacra 17', 'Nacra 17 Foiling');

-- Step 1: Find for each leg its start and end point, based on the positions of the boats, when their leg starts/ends. 

-- Updated variant! Run this query after calculating the start line!!
update l 
set l.start_lat = sub.start_lat, 
    l.start_lng = sub.start_lng 
from powertracks.legs l 
inner join (
    select l.leg_id, 
           (r.startline_pin_lat + r.startline_rc_lat) / 2 start_lat, 
           (r.startline_pin_lng + r.startline_rc_lng) / 2 start_lng
    from   powertracks.legs l
    inner join powertracks.races r on l.race_id = r.race_id 
    where l.leg_nr = 0 
) sub on l.leg_id = sub.leg_id;


select start_lat, start_lng, r.startline_pin_lat, r.startline_pin_lng, r.startline_rc_lat, r.startline_rc_lng
from powertracks.legs l
inner join powertracks.races r on l.race_id = r.race_id 
where leg_nr = 0; 

update l
set l.start_lat = avg_start_lat, l.start_lng = avg_start_lng
from powertracks.legs l
inner join (
    select cl.leg_id, avg(p.lat_deg) as avg_start_lat, avg(p.lng_deg) as avg_start_lng
    from  powertracks.comp_leg as cl 
    inner join powertracks.positions as p on p.comp_leg_id = cl.comp_leg_id
    where abs(p.timepoint_ms - cl.start_ms) < 2000
    group by cl.leg_id) as sub
on sub.leg_id = l.leg_id
    
update l
set l.end_lat = avg_end_lat, l.end_lng = avg_end_lng
from powertracks.legs l
inner join (
    select cl.leg_id, avg(p.lat_deg) as avg_end_lat, avg(p.lng_deg) as avg_end_lng
    from  powertracks.comp_leg as cl 
    inner join powertracks.positions as p on p.comp_leg_id = cl.comp_leg_id
    where abs(p.timepoint_ms - cl.end_ms) < 2000
    group by cl.leg_id) as sub
on sub.leg_id = l.leg_id

-- Data quality

select * 
from powertracks.legs 
where start_lat is null or end_lat is null

select l1.end_lat, l1.end_lng, l2.start_lat, l2.start_lng, abs(l2.start_lat - l1.end_lat), abs(l2.start_lng - l1.end_lng)
from powertracks.legs l1 
inner join powertracks.legs l2 on l1.race_id = l2.race_id and l1.leg_nr + 1 = l2.leg_nr
where abs(l2.start_lat - l1.end_lat) > 0.0005 or abs(l2.start_lng - l1.end_lng) > 0.0005


-- Later in this file, we will be calculating distances. We cannot assume that a certain difference in latitude 
-- equates the same difference in longitude. Therefore, we need to scale this. Taking the average position of 
-- (35.273, 139.512), moving in latitude by 0.01 degrees yields a distance of 1.112, whereas moving 0.01 degrees 
-- in longitude yields a distance of 0.908.
-- Source: https://latlongdata.com/distance-calculator/

-- Compute a few statistics on comp_leg level, regarding rank, side, average speed, and traveled distance. 
-- Step 1: Compute side. This query uses the positions table. 
-- Basic formula is: https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line , normalized by length of leg. 
-- 100% = two angles of 45 degrees, forming a triangle with the line between the waypoints. 


update cl
set avg_side = sub.avg_side, most_left_side = sub.most_left, most_right_side = sub.most_right
from powertracks.comp_leg cl 
inner join 
    (select p.comp_leg_id, 
        100 * avg(
        ( 1.112 * (l.end_lat - l.start_lat) * 0.908 * (l.start_lng - p.lng_deg) - 1.112 * (l.start_lat - p.lat_deg) * 0.908 * (l.end_lng - l.start_lng) ) /
        ( (power(1.112 * (l.end_lat - l.start_lat), 2) + power(0.908 * (l.end_lng - l.start_lng), 2)) / 4.0E0 )) avg_side,
        100 * min(
        ( 1.112 * (l.end_lat - l.start_lat) * 0.908 * (l.start_lng - p.lng_deg) - 1.112 * (l.start_lat - p.lat_deg) * 0.908 * (l.end_lng - l.start_lng) ) /
        ( (power(1.112 * (l.end_lat - l.start_lat), 2) + power(0.908 * (l.end_lng - l.start_lng), 2)) / 4.0E0 )) most_left,
        100 * max(
        ( 1.112 * (l.end_lat - l.start_lat) * 0.908 * (l.start_lng - p.lng_deg) - 1.112 * (l.start_lat - p.lat_deg) * 0.908 * (l.end_lng - l.start_lng) ) /
        ( (power(1.112 * (l.end_lat - l.start_lat), 2) + power(0.908 * (l.end_lng - l.start_lng), 2)) / 4.0E0 )) most_right
    from powertracks.positions p
    inner join powertracks.comp_leg cl on p.comp_leg_id = cl.comp_leg_id
    inner join powertracks.legs l on cl.leg_id = l.leg_id
    where l.start_lat is not null and l.end_lat is not null and
          sqrt(power(l.end_lat - l.start_lat, 2) + power(l.end_lng - l.start_lng, 2)) > 0.0001
    group by p.comp_leg_id) sub
on cl.comp_leg_id = sub.comp_leg_id



-- Data quality. 
select l.leg_nr, case when avg_side is null then 0 else 1 end is_null, count(*)
from powertracks.comp_leg cl
     inner join powertracks.legs l on cl.leg_id = l.leg_id
group by l.leg_nr, case when avg_side is null then 0 else 1 end
order by l.leg_nr, case when avg_side is null then 0 else 1 end

-- Step 2: Compute relative ranks of a few measures. 
update cl
set rel_rank = sub.rel_rank, 
    avg_side_rel_rank = sub.avg_side_rel_rank, 
    average_sog_rel_rank = sub.average_sog_rel_rank, 
    distance_traveled_rel_rank = sub.distance_traveled_rel_rank,
    average_sog_ratio_to_mean = sub.average_sog_ratio_to_mean,
    average_distance_ratio_to_mean = sub.average_distance_ratio_to_mean
from powertracks.comp_leg cl
inner join 
    (select comp_leg_id,  
     100 * (rank() over (partition by leg_id order by rank) - 1.0) /
           (count(*) over (partition by leg_id) - 1.0) rel_rank,
     100 * (rank() over (partition by leg_id order by avg_side) - 1.0) /
           (count(*) over (partition by leg_id) - 1.0) avg_side_rel_rank,
     100 * (rank() over (partition by leg_id order by average_sog_kts) - 1.0) /
           (count(*) over (partition by leg_id) - 1.0) average_sog_rel_rank,
     100 * (rank() over (partition by leg_id order by distance_traveled_m) - 1.0) /
           (count(*) over (partition by leg_id) - 1.0) distance_traveled_rel_rank,
     iif(distance_traveled_m = 0, 0.0, 100 * distance_traveled_m / (avg(distance_traveled_m) over (partition by leg_id))) average_distance_ratio_to_mean, 
     iif(average_sog_kts = 0,     0.0, 100 * average_sog_kts     / (avg(average_sog_kts)     over (partition by leg_id))) average_sog_ratio_to_mean
     from powertracks.comp_leg) sub on cl.comp_leg_id = sub.comp_leg_id; 

-- Data quality
select l.leg_id, rank, rel_rank, avg_side_rel_rank, average_sog_rel_rank, distance_traveled_rel_rank
from powertracks.comp_leg cl
inner join powertracks.legs l on cl.leg_id = l.leg_id
order by l.leg_id, rank, rel_rank


-- Step 3: Add race centroids
update r
set r.centroid_lat = sub.centroid_lat, 
    r.centroid_lng = sub.centroid_lng
from powertracks.races r
inner join (
    select r.race_id, 
           0.5 * (avg(l.start_lat) + avg(l.end_lat)) centroid_lat, 
           0.5 * (avg(l.start_lng) + avg(l.end_lng)) centroid_lng
    from powertracks.races r 
    inner join powertracks.legs l on r.race_id = l.race_id
    group by r.race_id
) sub on r.race_id = sub.race_id;


-- Step 4: Assign course area to races based on proximity of race centroid to course area centroid. 
update r
set r.course_area_id = sub.id
from powertracks.races r
inner join (
    select r.race_id, ca.id, ca.course_area, 
        sqrt(power(ca.lat_deg - r.centroid_lat, 2) + power(ca.lng_deg - r.centroid_lng, 2)) dist,
        rank() over (partition by r.race_id order by sqrt(power(ca.lat_deg - r.centroid_lat, 2) + power(ca.lng_deg - r.centroid_lng, 2))) dist_rank
    from powertracks.races r, powertracks.course_areas ca) sub on r.race_id = sub.race_id
where sub.dist_rank = 1
    

-- Step 5: Calculate position of startline. 
-- Pin is left side of startline, RC is right side of startline. 
update r
set r.startline_pin_lat = sub.lat_deg, r.startline_pin_lng = sub.lng_deg
from powertracks.races r 
inner join (
    select race_id, lat_deg, lng_deg
    from ( 
        select r.race_id, 
               mp.lat_deg, mp.lng_deg, 
               ROW_NUMBER() over (partition by r.race_id order by abs(r.start_of_race_ms - mp.timepoint_ms)) rnk
        from powertracks.races r
        inner join powertracks.marks_positions mp on r.startline_pin_id = mp.mark_id
    ) inner_sub
    where rnk = 1
) sub on r.race_id = sub.race_id;

update r
set r.startline_rc_lat = sub.lat_deg, r.startline_rc_lng = sub.lng_deg
from powertracks.races r 
inner join (
    select race_id, lat_deg, lng_deg
    from ( 
        select r.race_id, 
               mp.lat_deg, mp.lng_deg, 
               ROW_NUMBER() over (partition by r.race_id order by abs(r.start_of_race_ms - mp.timepoint_ms)) rnk
        from powertracks.races r
        inner join powertracks.marks_positions mp on r.startline_rc_id = mp.mark_id
    ) inner_sub
    where rnk = 1
) sub on r.race_id = sub.race_id;

-- Data quality
select r.regatta_id, r.race_name, r.race_id, r.start_of_race_ms, r.startline_pin_lat, r.startline_pin_lng
from powertracks.races r
where r.startline_pin_lat is null or r.startline_rc_lat is null; 


-- Step 6: Calculate relative start positions

-- Find start position for each first leg, for each competitor. 
update rc 
set rc.start_pos_lat = sub.lat_deg, rc.start_pos_lng = sub.lng_deg
from powertracks.race_comp rc 
inner join (
    select * 
    from (
        select l.race_id, cl.comp_id, lat_deg, lng_deg, 
            ROW_NUMBER() over (partition by cl.comp_leg_id order by abs(r.start_of_race_ms - p.timepoint_ms)) rnk 
        from powertracks.positions p 
        inner join powertracks.comp_leg cl on p.comp_leg_id = cl.comp_leg_id 
        inner join powertracks.legs l on cl.leg_id = l.leg_id
        inner join powertracks.races r on l.race_id = r.race_id
        where l.leg_nr = 0 and abs(r.start_of_race_ms - p.timepoint_ms) < 120000
    ) inner_sub
    where rnk = 1
) sub on rc.race_id = sub.race_id and rc.comp_id = sub.comp_id;

-- Find relative start position on the start line. 0 -> left side; 100 -> right side. 
update rc
set start_pos_rel = sub.start_pos_rel
from powertracks.race_comp rc
inner join (
    select rc.race_id, rc.comp_id,
        powertracks.FindOrthPosOnLine(startline_rc_lat, startline_rc_lng, startline_pin_lat, startline_pin_lng, 
                                    rc.start_pos_lat, rc.start_pos_lng) start_pos_rel
    from powertracks.races r 
    inner join powertracks.race_comp rc on rc.race_id = r.race_id
) as sub on rc.race_id = sub.race_id and rc.comp_id = sub.comp_id

-- Find relative rank of start position (scaled from 0 to 100). 
update rc 
set start_pos_rel_rank = sub.sprl 
from powertracks.race_comp rc inner join (
    select rc.race_id, rc.comp_id, start_pos_rel,  
    100.0 * (rank() over (partition by rc.race_id order by start_pos_rel) - 1.0) /
            (count(*) over (partition by rc.race_id) - 1.0) sprl 
    from powertracks.race_comp rc 
    where start_pos_rel is not null
) sub on rc.race_id = sub.race_id and rc.comp_id = sub.comp_id;


-- Step 7: Calculate the 'real' wind direction from the wind data. 
update r
set startwind_angle = sub.startwind_angle
from powertracks.races r
inner join 
(
    select r2.race_id, avg(true_bearing_deg) startwind_angle
    from powertracks.races r2
    inner join powertracks.wind w on r2.race_id = w.race_id 
    where w.timepoint_ms between r2.start_of_race_ms and r2.start_of_race_ms + 20000
    group by r2.race_id 
) sub on r.race_id = sub.race_id;

-- In case the predominant wind direction is around 0 or 360 degress, the average will fail. This query will fix that (7 rows). 
update r 
set r.startwind_angle = sub.new_angle 
from powertracks.races r 
inner join 
(
    select r1.race_id, (avg( (180 + w.true_bearing_deg) % 360) + 180) % 360 new_angle
    from powertracks.races r1
    inner join powertracks.wind w on r1.race_id = w.race_id and w.timepoint_ms between r1.start_of_race_ms and r1.start_of_race_ms + 20000
    inner join (
        select r2.race_id
        from powertracks.races r2
        inner join powertracks.wind w1 on r2.race_id = w1.race_id and w1.timepoint_ms between r2.start_of_race_ms and r2.start_of_race_ms + 20000
        group by r2.race_id
        having max(true_bearing_deg) - min(true_bearing_deg) > 20
    ) sub2 on r1.race_id = sub2.race_id
    group by r1.race_id
) sub on r.race_id = sub.race_id

-- Convert bearing to wind direction. 
update powertracks.races 
set startwind_angle = (startwind_angle + 180) % 360;

-- Data quality
select count(*)
from powertracks.races
where startwind_angle is null; 



-- Step 8: Calculate angle of startline. 
update r
set startline_angle = sub.startline_angle
from powertracks.races r 
inner join (
    select race_id, 
           round(180 / PI() * 
                 iif (abs(startline_pin_lat - startline_rc_lat) = 0.0, 
                      0.5 * PI(), 
                      atn2( (startline_pin_lng - startline_rc_lng),
                             (1.125 * (startline_pin_lat - startline_rc_lat)))), 0) startline_angle
    from powertracks.races r2
) sub on r.race_id = sub.race_id;

-- Step 9: Compute difference between actual wind direction at start and expected wind direction based on startline. 
update powertracks.races 
set startline_startwind_angle_diff = (360 + 90 + startwind_angle - startline_angle) % 360 - 180;

-- Data quality 
select startline_startwind_angle_diff, count(*) 
from powertracks.races
group by startline_startwind_angle_diff
order by startline_startwind_angle_diff


-- Extra link necessary for power bi reporting. 
alter table powertracks.race_comp 
add race_comp_id INT IDENTITY(1,1); 

alter table powertracks.comp_leg 
add race_comp_id INT;

update cl 
set cl.race_comp_id = sub.race_comp_id 
from powertracks.comp_leg cl
inner join (
    select cl.comp_leg_id, rc.race_comp_id
    from powertracks.comp_leg cl 
    inner join powertracks.legs l on cl.leg_id = l.leg_id
    inner join powertracks.races r on r.race_id = l.race_id
    inner join powertracks.race_comp rc on rc.race_id = r.race_id and cl.comp_id = rc.comp_id
    group by cl.comp_leg_id, rc.race_comp_id
) sub on cl.comp_leg_id = sub.comp_leg_id;