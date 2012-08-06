
drop table if exists fec_candidates;
create table fec_candidates (
    cycle int,
    candidate_id varchar(9),
    candidate_name varchar(200),
    party varchar(3),
    election_year integer,
    office_state varchar(2),
    office varchar(1),
    office_district varchar(2),
    incumbent_challenger_open varchar(1),
    candidate_status varchar(1),
    committee_id varchar(9),
    street1 varchar(34),
    street2 varchar(34),
    city varchar(30),
    state varchar(2),
    zipcode varchar(9)
);

drop table if exists fec_committees;
create table fec_committees (
    cycle int,
    committee_id varchar(9),
    committee_name varchar(200),
    treasurers_name varchar(90),
    street1 varchar(34),
    street2 varchar(34),
    city varchar(30),
    state varchar(2),
    zipcode varchar(9),
    committee_designation varchar(1),
    committee_type varchar(1),
    committee_party varchar(3),
    filing_frequency varchar(1),
    interest_group varchar(1),
    connected_org varchar(200),
    candidate_id varchar(9)
);

drop table if exists fec_indiv;
create table fec_indiv (
    cycle int,
    filer_id varchar(9),
    amendment varchar(1),
    report_type varchar(3),
    election_type varchar(5),
    microfilm_location varchar(11),
    transaction_type varchar(3),
    entity_type varchar(3),
    contributor_name varchar(200),
    city varchar(30),
    state varchar(2),
    zipcode varchar(9),
    employer varchar(38),
    occupation varchar(38),
    date date,
    amount numeric(14,2),
    other_id varchar(9),
    transaction_id varchar(32),
    file_num varchar(22),
    memo_code varchar(1),
    memo_text varchar(100),
    fec_record varchar(19)
);

drop table if exists fec_pac2cand;
create table fec_pac2cand (
    cycle int,
    filer_id varchar(9),
    amendment varchar(1),
    report_type varchar(3),
    election_type varchar(5),
    microfilm_location varchar(11),
    transaction_type varchar(3),
    entity_type varchar(3),
    contributor_name varchar(200),
    city varchar(30),
    state varchar(2),
    zipcode varchar(9),
    employer varchar(38),
    occupation varchar(38),
    date date,
    amount numeric(14,2),
    other_id varchar(9),
    candidate_id varchar(9),
    transaction_id varchar(32),
    file_num varchar(22),
    memo_code varchar(1),
    memo_text varchar(100),
    fec_record varchar(19)
);

drop table if exists fec_pac2pac;
CREATE TABLE fec_pac2pac (
    cycle int,
    filer_id varchar(9),
    amendment varchar(1),
    report_type varchar(3),
    election_type varchar(5),
    microfilm_location varchar(11),
    transaction_type varchar(3),
    entity_type varchar(3),
    contributor_name varchar(200),
    city varchar(30),
    state varchar(2),
    zipcode varchar(9),
    employer varchar(38),
    occupation varchar(38),
    date date,
    amount numeric(14,2),
    other_id varchar(9),
    transaction_id varchar(32),
    file_num varchar(22),
    memo_code varchar(1),
    memo_text varchar(100),
    fec_record varchar(19)
);

drop table if exists fec_candidate_summaries;
CREATE TABLE fec_candidate_summaries (
    cycle int,
    candidate_id varchar(9),
    candidate_name varchar(200),
    incumbent_challenger_open varchar(1),
    party varchar(1),
    party_affiliation varchar(3),
    total_receipts numeric(14,2),                            -- 22
    authorized_transfers_from numeric(14,2),                 -- 18
    total_disbursements numeric(14,2),                       -- 30
    transfers_to_authorized numeric(14,2),                   -- 24
    beginning_cash numeric(14,2),                            -- 6
    ending_cash numeric(14,2),                               -- 10
    contributions_from_candidate numeric(14,2),              -- 17d
    loans_from_candidate numeric(14,2),                      -- 19a
    other_loans numeric(14,2),                               -- 19b
    candidate_loan_repayments numeric(14,2),                 -- 27a
    other_loan_repayments numeric(14,2),                     -- 27b
    debts_owed_by numeric(14,2),                             -- 12
    total_individual_contributions numeric(14,2),            -- 17a
    state varchar(2),
    district varchar(2),
    special_election_status varchar(1),
    primary_election_status varchar(1),
    runoff_election_status varchar(1),
    general_election_status varchar(1),
    general_election_ct numeric(7,4),
    contributions_from_other_committees numeric(14,2),       -- 17c
    contributions_from_party_committees numeric(14,2),       -- 17b
    ending_date date,
    refunds_to_individuals numeric(14,2),                    -- 28a
    refunds_to_committees numeric(14,2)                      -- 28b & 28c?
);

drop table if exists fec_committee_summaries;
CREATE TABLE fec_committee_summaries (
    cycle int,
    committee_id varchar(9),
    committee_name varchar(200),
    committee_type varchar(1),
    committee_designation varchar(1),
    filing_frequency varchar(1),
    total_receipts numeric(14,2),
    transfers_from_affiliates numeric(14,2),
    individual_contributions numeric(14,2),
    contributions_from_other_committees numeric(14,2),
    contributions_from_candidate numeric(14,2),
    candidate_loans numeric(14,2),
    total_loans_received numeric(14,2),
    total_disbursements numeric(14,2),
    transfers_to_affiliates numeric(14,2),
    refunds_to_individuals numeric(14,2),
    refunds_to_committees numeric(14,2),
    candidate_loan_repayments numeric(14,2),
    loan_repayments numeric(14,2),
    cash_beginning_of_year numeric(14,2),
    cash_close_of_period numeric(14,2),
    debts_owed numeric(14,2),
    nonfederal_transfers_received numeric(14,2),
    contributions_to_committees numeric(14,2),
    independent_expenditures_made numeric(14,2),
    party_coordinated_expenditures_made numeric(14,2),
    nonfederal_expenditure_share numeric(14,2),
    through_date date
);







drop view if exists fec_candidate_itemized;
create view fec_candidate_itemized as
select
    contributor_name, date, amount, contributor_type, transaction_type, 
    employer, occupation, i.city, i.state, i.zipcode, 
    candidate_name, party, office, office_state, office_district, incumbent_challenger_open as status, committee_id, candidate_id
from fec_candidates c
inner join (
    select filer_id as committee_id, 'indiv' as contributor_type, contributor_name,
        i.city, i.state, i.zipcode, employer, occupation,
        date, amount, transaction_type
    from fec_indiv i

    union all

    select other_id, 'pac', committee_name,
        t.city, t.state, t.zipcode, connected_org, '',
        date, amount, transaction_type
    from fec_pac2cand t
    inner join fec_committees c on (c.committee_id = t.filer_id)) i using (committee_id);


drop view if exists fec_committee_itemized;
create view fec_committee_itemized as
select
    contributor_name, date, amount, contributor_type, contributor_committee_id, transaction_type, 
    employer, occupation, i.city, i.state, i.zipcode, 
    committee_name, committee_id, committee_designation, committee_type, committee_party, interest_group, connected_org, candidate_id
from fec_committees c
inner join (
    select filer_id as committee_id, 'indiv' as contributor_type, contributor_name, '' as contributor_committee_id,
        city, state, zipcode, employer, occupation,
        date, amount, transaction_type
    from fec_indiv

    union all

    select filer_id, 'pac', contributor_name, other_id,
        city, state, zipcode, '', occupation,
        date, amount, transaction_type
    from fec_pac2pac) i using (committee_id)
where
    -- only transaction types 10-19 are money coming in. 20-29 are money going out, which we're not interested in here.
    substring(transaction_type for 2)::integer between 10 and 19;

