-- Actions automation tables

-- Enable needed extensions (if not already enabled in Supabase)
-- create extension if not exists pgcrypto; -- for gen_random_uuid() in some Postgres setups

create table if not exists public.actions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  portfolio_id uuid null,
  status text not null default 'active',
  action_type text not null,
  symbol text null,
  quantity numeric null,
  amount_usd numeric null,
  trigger_type text not null,
  trigger_params jsonb not null,
  valid_from timestamptz null default now(),
  valid_until timestamptz null,
  max_executions int null default 1,
  executions_count int not null default 0,
  cooldown_seconds int null,
  last_triggered_at timestamptz null,
  last_evaluated_at timestamptz null,
  processing_lease_until timestamptz null,
  notes text null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_actions_user on public.actions(user_id);
create index if not exists idx_actions_status on public.actions(status);
create index if not exists idx_actions_symbol on public.actions(symbol);
create index if not exists idx_actions_trigger on public.actions(trigger_type);

-- Track executions for audit and idempotency checks
create table if not exists public.action_executions (
  id uuid primary key default gen_random_uuid(),
  action_id uuid not null references public.actions(id) on delete cascade,
  triggered_at timestamptz not null default now(),
  execution_status text not null,
  details jsonb null,
  transaction_id uuid null,
  error text null
);

create index if not exists idx_action_exec_action on public.action_executions(action_id);

-- Helpful partial index to quickly fetch evaluable actions
create index if not exists idx_actions_active_evaluable on public.actions ((status)) where status = 'active';

-- Update updated_at trigger
create or replace function set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists set_updated_at_actions on public.actions;
create trigger set_updated_at_actions
before update on public.actions
for each row execute function set_updated_at();


