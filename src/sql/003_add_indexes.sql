-- Remove useless data. 

delete from powertracks.comp_leg
where started = 0 or finished = 0; 


-- Adding indexes after adding the data results in improved efficiency for both uploading and querying. 

CREATE NONCLUSTERED INDEX races_nci_idx
ON powertracks.races(regatta_id);

CREATE CLUSTERED INDEX race_comp_nci_idx
ON powertracks.race_comp(race_id, comp_id);

CREATE CLUSTERED INDEX wind_ci_idx
ON powertracks.wind(race_id, timepoint_ms);

CREATE CLUSTERED INDEX marks_ci_idx
ON powertracks.marks(race_id, mark_id); 

CREATE CLUSTERED INDEX marks_positions_ci_idx
ON powertracks.marks_positions(mark_id, timepoint_ms);

CREATE CLUSTERED INDEX legs_ci_idx
ON powertracks.legs(leg_id);

CREATE CLUSTERED INDEX comp_leg_ci_idx
ON powertracks.comp_leg(leg_id, comp_leg_id);

CREATE NONCLUSTERED INDEX comp_leg_nci_comp_idx
ON powertracks.comp_leg(comp_id);

CREATE NONCLUSTERED INDEX comp_leg_nci_rank_idx
ON powertracks.comp_leg(rank);

CREATE NONCLUSTERED INDEX comp_leg_nci_race_comp_idx
ON powertracks.comp_leg(race_comp_id);

CREATE NONCLUSTERED INDEX positions_ci_idx
ON powertracks.positions(comp_leg_id, timepoint_ms);

CREATE NONCLUSTERED INDEX pruned_positions_ci_idx
ON powertracks.pruned_positions(comp_leg_id, timepoint_ms);

