-- Find for each leg its start and end point, based on the positions of the boats, when their leg starts/ends. 

alter table powertracks.legs add
start_lat decimal(9,6),
start_lng decimal(9,6), 
end_lat decimal(9,6),
end_lng decimal(9,6);

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
        ( (l.end_lat - l.start_lat) * (l.start_lng - p.lng_deg) - (l.start_lat - p.lat_deg) * (l.end_lng - l.start_lng) ) /
        ( (power(l.end_lat - l.start_lat, 2) + power(l.end_lng - l.start_lng, 2)) / 2.0E0 )) avg_side,
        100 * min(
        ( (l.end_lat - l.start_lat) * (l.start_lng - p.lng_deg) - (l.start_lat - p.lat_deg) * (l.end_lng - l.start_lng) ) /
        ( (power(l.end_lat - l.start_lat, 2) + power(l.end_lng - l.start_lng, 2)) / 2.0E0 )) most_left,
        100 * max(
        ( (l.end_lat - l.start_lat) * (l.start_lng - p.lng_deg) - (l.start_lat - p.lat_deg) * (l.end_lng - l.start_lng) ) /
        ( (power(l.end_lat - l.start_lat, 2) + power(l.end_lng - l.start_lng, 2)) / 2.0E0 )) most_right
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
    distance_traveled_rel_rank = sub.distance_traveled_rel_rank
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
           (count(*) over (partition by leg_id) - 1.0) distance_traveled_rel_rank
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
update r
set r.startline_pin_lat = sub.start_lat, r.startline_pin_lng = sub.start_lng
from powertracks.races r 
inner join (
    select r.race_id, avg(mp.lat_deg) start_lat, avg(mp.lng_deg) start_lng
    from powertracks.races r
    inner join powertracks.marks_positions mp on r.startline_pin_id = mp.mark_id and abs(r.start_of_race_ms - mp.timepoint_ms) < 660000  -- 11 minutes: 5 before and 5 after start of race
    group by r.regatta_id, r.race_id, r.race_name, r.start_of_race_ms) sub on r.race_id = sub.race_id

-- Data quality
select r.regatta_id, r.race_name, r.race_id, r.start_of_race_ms, r.startline_pin_lat, r.startline_pin_lng
from powertracks.races r
where r.startline_pin_lat is null

