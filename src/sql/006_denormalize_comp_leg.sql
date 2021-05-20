create or alter view powertracks.comp_leg_full_view as 
select     cl.comp_leg_id, 
           rg.regatta_id, 
           rg.boatclass, 
           r.race_name,
           r.race_short_name, 
           r.max_wind_speed_kts, 
           r.min_wind_speed_kts, 
           r.start_of_race_dt, 
           r.startline_angle, 
           r.startwind_angle, 
           r.startline_startwind_angle_diff, 
           r.wind_dir_based_on_bearing, 
           r.startline_startwind_angle_diff_bearing, 
           r.visualize, 
           c.comp_name,
           rc.rank, 
           rc.start_pos_rel, 
           rc.start_pos_rel_rank, 
           ca.course_area, 
           l.distance, 
           cl.tacks, 
           cl.jibes, 
           cl.penalty_circles, 
           cl.started,
           cl.finished, 
           cl.rel_rank, 
           cl.avg_side, 
           cl.avg_side_rel_rank, 
           cl.average_sog_rel_rank, 
           cl.distance_traveled_rel_rank,
           cl.average_sog_ratio_to_mean,
           cl.average_distance_ratio_to_mean
from       powertracks.comp_leg cl 
inner join powertracks.legs l on cl.leg_id = l.leg_id
inner join powertracks.races r on l.race_id = r.race_id 
inner join powertracks.regattas rg on r.regatta_id = rg.regatta_id
inner join powertracks.course_areas ca on r.course_area_id = ca.id
inner join powertracks.race_comp rc on cl.race_comp_id = rc.race_comp_id
inner join powertracks.competitors c on rc.comp_id = c.comp_id
where l.leg_nr = 0;