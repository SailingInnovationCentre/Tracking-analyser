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
    where abs(p.timepoint_ms - cl.start_ms) < 500
    group by cl.leg_id) as sub
on sub.leg_id = l.leg_id
    
update l
set l.end_lat = avg_end_lat, l.end_lng = avg_end_lng
from powertracks.legs l
inner join (
    select cl.leg_id, avg(p.lat_deg) as avg_end_lat, avg(p.lng_deg) as avg_end_lng
    from  powertracks.comp_leg as cl 
    inner join powertracks.positions as p on p.comp_leg_id = cl.comp_leg_id
    where abs(p.timepoint_ms - cl.end_ms) < 500
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


-- Compute average side, most_left and most_right. 
update cl
set avg_side = sub.avg_side, most_left = sub.most_left, most_right = sub.most_right
from powertracks.comp_leg cl 
inner join 
    (select p.comp_leg_id, 
        100 * avg(
        ( (l.end_lat - l.start_lat) * (l.start_lng - p.lng_deg) - (l.start_lat - p.lat_deg) * (l.end_lng - l.start_lng) ) /
        ( (power(l.end_lat - l.start_lat, 2) + power(l.end_lng - l.start_lng, 2)) / 2.0 )) avg_side,
        100 * min(
        ( (l.end_lat - l.start_lat) * (l.start_lng - p.lng_deg) - (l.start_lat - p.lat_deg) * (l.end_lng - l.start_lng) ) /
        ( (power(l.end_lat - l.start_lat, 2) + power(l.end_lng - l.start_lng, 2)) / 2.0 )) most_left,
        100 * max(
        ( (l.end_lat - l.start_lat) * (l.start_lng - p.lng_deg) - (l.start_lat - p.lat_deg) * (l.end_lng - l.start_lng) ) /
        ( (power(l.end_lat - l.start_lat, 2) + power(l.end_lng - l.start_lng, 2)) / 2.0 )) most_right
    from powertracks.positions p
    inner join powertracks.comp_leg cl on p.comp_leg_id = cl.comp_leg_id
    inner join powertracks.legs l on cl.leg_id = l.leg_id
    where l.start_lat is not null and l.end_lat is not null and (abs(l.end_lat - l.start_lat) > 0.01 or abs(l.end_lng - l.start_lng) > 0.01)
    group by p.comp_leg_id) sub
on cl.comp_leg_id = sub.comp_leg_id

-- Compute relative ranks of a few measures. 
update cl
set rel_rank = sub.avg_side_rank, rel_average_sog = sub.rel_average_sog, rel_distance_traveled = sub.rel_distance_traveled
from powertracks.comp_leg cl
inner join 
    (select comp_leg_id,  
     100 * (rank() over (partition by leg_id order by avg_side) - 1.0) /
           (count(*) over (partition by leg_id) - 1.0) avg_side_rank,
     100 * (rank() over (partition by leg_id order by average_sog_kts) - 1.0) /
           (count(*) over (partition by leg_id) - 1.0) rel_average_sog,
     100 * (rank() over (partition by leg_id order by distance_traveled_m) - 1.0) /
           (count(*) over (partition by leg_id) - 1.0) rel_distance_traveled
     from powertracks.comp_leg) sub on cl.comp_leg_id = sub.comp_leg_id; 