-- Story 3.1: append-only outcome event/observation ledgers and rebuildable projection.
-- Ledger rows are immutable at the database boundary. candidate_outcome is deliberately
-- mutable because later stories rebuild and advance it by replaying the ledgers.
begin;

create table public.outcome_events (
  event_id uuid primary key default gen_random_uuid(),
  ticker text not null check (length(btrim(ticker)) > 0),
  strategy text not null check (strategy in ('A', 'B', 'C')),
  command_type text not null check (length(btrim(command_type)) > 0),
  logical_run_key text not null references public.logical_runs(logical_run_key),
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create table public.outcome_observations (
  outcome_id uuid not null,
  evaluation_trading_day date not null,
  high numeric not null check (
    high > 0 and high not in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric)
  ),
  low numeric not null check (
    low > 0 and low not in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric)
  ),
  close numeric not null check (
    close > 0 and close not in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric)
  ),
  result_code text not null check (length(btrim(result_code)) > 0),
  primary key (outcome_id, evaluation_trading_day)
);

create table public.candidate_outcome (
  outcome_id uuid primary key default gen_random_uuid(),
  ticker text not null check (length(btrim(ticker)) > 0),
  strategy text not null check (strategy in ('A', 'B', 'C')),
  entry_date date not null,
  entry_price numeric not null check (
    entry_price > 0 and entry_price not in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric)
  ),
  status text not null check (status in ('TP', 'SL', 'TIMEOUT', 'OPEN', 'SUSPENDED', 'DELISTED')),
  exit_date date,
  exit_price numeric check (
    exit_price is null or (
      exit_price > 0 and exit_price not in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric)
    )
  ),
  return_pct numeric check (
    return_pct is null or return_pct not in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric)
  ),
  cutoff_n integer not null default 30 check (cutoff_n > 0),
  holding_days integer not null default 0 check (holding_days >= 0),
  unique (ticker, strategy, entry_date)
);

create unique index candidate_outcome_one_open_per_ticker_strategy_idx
  on public.candidate_outcome(ticker, strategy)
  where status = 'OPEN';

create or replace function public.reject_outcome_ledger_mutation()
returns trigger
language plpgsql
set search_path = public
as $$
begin
  raise exception using
    errcode = '55000',
    message = format('%I.%I is append-only; %s is forbidden', tg_table_schema, tg_table_name, tg_op);
end;
$$;

create trigger outcome_events_append_only
before update or delete on public.outcome_events
for each row execute function public.reject_outcome_ledger_mutation();

create trigger outcome_observations_append_only
before update or delete on public.outcome_observations
for each row execute function public.reject_outcome_ledger_mutation();

comment on table public.outcome_events is 'Outcome command/event append-only ledger. UPDATE and DELETE are rejected by trigger.';
comment on table public.outcome_observations is 'Outcome daily observation append-only ledger. It intentionally has no FK to rebuildable candidate_outcome.';
comment on table public.candidate_outcome is 'Current outcome projection rebuilt from outcome ledgers. Source provenance is joined through candidate_source_contrib.';

alter table public.outcome_events enable row level security;
alter table public.outcome_observations enable row level security;
alter table public.candidate_outcome enable row level security;

commit;
