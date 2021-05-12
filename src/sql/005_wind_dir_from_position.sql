
drop table powertracks.dominant_directions; 

-- Create a matrix of races and degrees. 
select r.race_id, r.regatta_id, r.race_name, d.deg as bearing, 0 as cnt, 0 as cnt_smooth, 0 as offset, 1 as active 
into powertracks.dominant_directions
from powertracks.races r, powertracks.degrees d;

CREATE CLUSTERED INDEX dd_ci
ON powertracks.dominant_directions(race_id, bearing);


-- Assign the number of measurements for each bearing in each race. 
update dd
set cnt = sub.cnt 
from powertracks.dominant_directions dd 
inner join (
    select r.race_id, cast(round(p.true_bearing_deg,0) as int) % 360 bearing, count(*) cnt
    from powertracks.races r 
    inner join powertracks.legs l on r.race_id = l.race_id 
    inner join powertracks.comp_leg cl on l.leg_id = cl.leg_id
    inner join powertracks.positions p on p.comp_leg_id = cl.comp_leg_id
    where p.timepoint_ms between r.start_of_race_ms and r.start_of_race_ms + 300000
    group by r.race_id, cast(round(p.true_bearing_deg, 0) as int) % 360
) sub on dd.race_id = sub.race_id and dd.bearing = sub.bearing;

-- Create a rolling average, to smooth out the counts a bit. 
-- We need this to roll over the 360 degrees boundary, so a bit a creativity is used here. 

update dd 
set cnt_smooth = sub.cnt_smooth
from powertracks.dominant_directions dd 
inner join ( 
  select race_id, bearing, 
         cast((cnt + lead(cnt) over (partition by race_id order by bearing) + lag(cnt) over (partition by race_id order by bearing))/3 as int) cnt_smooth
  from powertracks.dominant_directions
) sub on dd.race_id = sub.race_id and dd.bearing = sub.bearing
where sub.bearing between 1 and 358;

-- hihi 
update dd 
set cnt_smooth = sub.cnt_smooth 
from powertracks.dominant_directions dd 
inner join (
    select dd359.race_id, cast( (dd359.cnt + dd0.cnt + dd1.cnt) / 3 as int) cnt_smooth
    from (select race_id, cnt from powertracks.dominant_directions where bearing = 359) dd359
    inner join (select race_id, cnt from powertracks.dominant_directions where bearing = 0) dd0 on dd359.race_id = dd0.race_id
    inner join (select race_id, cnt from powertracks.dominant_directions where bearing = 1) dd1 on dd359.race_id = dd1.race_id
) sub on dd.race_id = sub.race_id
where dd.bearing = 0;

-- haha
update dd 
set cnt_smooth = sub.cnt_smooth 
from powertracks.dominant_directions dd 
inner join (
    select dd359.race_id, cast( (dd358.cnt + dd359.cnt + dd0.cnt) / 3 as int) cnt_smooth
    from (select race_id, cnt from powertracks.dominant_directions where bearing = 358) dd358
    inner join (select race_id, cnt from powertracks.dominant_directions where bearing = 359) dd359 on dd358.race_id = dd359.race_id
    inner join (select race_id, cnt from powertracks.dominant_directions where bearing = 0) dd0 on dd358.race_id = dd0.race_id
) sub on dd.race_id = sub.race_id
where dd.bearing = 359;

-- Check correctness. 
select top(10000) * 
from powertracks.dominant_directions
where bearing < 10 or bearing > 350 
order by race_id, bearing;

-- Six races without any positioning. 
select race_id, max(cnt_smooth) m
from powertracks.dominant_directions
group by race_id
order by max(cnt_smooth) asc;

-- Every race contains at least 150 rows where cnt is 0. 
select min(m) from (
select race_id, count(*) m
from powertracks.dominant_directions 
where cnt < 15
group by race_id) x;

-- Keep doing this query until no rows change. 
update dd 
set bearing = (bearing + 10) % 360, offset = offset + 15
from powertracks.dominant_directions dd 
inner join (
    select distinct race_id 
    from powertracks.dominant_directions 
    where cnt > 15 and (bearing = 0 or bearing = 359)
) sub on dd.race_id = sub.race_id;


alter table powertracks.races add dominant_bearing_1 int, dominant_bearing_2 int; 

update powertracks.races 
set dominant_bearing_1 = 0, dominant_bearing_2 = 0; 

update r 
set dominant_bearing_1 = iif(sub.bearing - sub.offset < 0, sub.bearing - sub.offset + 360, sub.bearing - sub.offset)
from powertracks.races r
inner join (
    select race_id, bearing, offset 
    from (
        select *, ROW_NUMBER() over (partition by race_id order by cnt_smooth desc) as rnk
        from powertracks.dominant_directions
        where cnt_smooth > 30
    ) s
    where rnk = 1
) sub on r.race_id = sub.race_id; 

update dd 
set active = 0
from powertracks.dominant_directions dd 
inner join (
    select r.race_id, bearing, offset
    from powertracks.dominant_directions dd2 
    inner join powertracks.races r on dd2.race_id = r.race_id
    where bearing between r.dominant_bearing_1 - 30 and r.dominant_bearing_1 + 30
) sub on dd.race_id = sub.race_id and dd.bearing = sub.bearing;


update r 
set dominant_bearing_2 = sub.bearing 
from powertracks.races r
inner join (
    select race_id, bearing 
    from (
        select *, ROW_NUMBER() over (partition by race_id order by cnt_smooth desc) as rnk
        from powertracks.dominant_directions 
        where active = 1 
    ) s
    where rnk = 1
) sub on r.race_id = sub.race_id; 

update powertracks.races 
set wind_dir_based_on_bearing = 
       (180 + iif(abs(dominant_bearing_1-dominant_bearing_2) > 180, 
                  (360 + dominant_bearing_1 + dominant_bearing_2) / 2,
                  (dominant_bearing_1 + dominant_bearing_2) / 2)) % 360;

select dominant_bearing_1, dominant_bearing_2,
       (180 + iif(abs(dominant_bearing_1-dominant_bearing_2) > 180, 
                  (360 + dominant_bearing_1 + dominant_bearing_2) / 2,
                  (dominant_bearing_1 + dominant_bearing_2) / 2)) % 360 diff, startwind_angle
from powertracks.races;

update powertracks.races 
set startline_startwind_angle_diff_bearing = ((wind_dir_based_on_bearing-startline_angle+90+180) % 360) - 180;

select startline_startwind_angle_diff_bearing, startline_startwind_angle_diff
from powertracks.races;