create index fec_indiv_cycle_id on fec_indiv (cycle);
create index fec_pac2cand_cycle_id on fec_pac2cand (cycle);
create index fec_pac2pac_cycle_id on fec_pac2pac (cycle);
create index fec_committee_cycle_id on fec_committes (cycle);
create index fec_candidates_cycle_id on fec_candidates (cycle);
create index fec_committee_summaries_cycle_id on fec_committee_summaries (cycle);
create index fec_candidate_summaries_cycle_id on fec_candidate_summaries (cycle);


create index fec_committee_summaries_committee_id on fec_committee_summaries (committee_id);
create index fec_candidate_summaries_candidate_id on fec_candidate_summaries (candidate_id);

create index fec_indiv_filer_id on fec_indiv (filer_id);
create index fec_pac2cand_other_id on fec_pac2cand (other_id);
create index fec_pac2cand_cand_id on fec_pac2cand (candidate_id);
create index fec_pac2pac_filer_id on fec_pac2pac (filer_id);
create index fec_pac2pac_other_id on fec_pac2pac (other_id);
