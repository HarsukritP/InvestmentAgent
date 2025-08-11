## Background Actions (Rules) – Design Document

This document specifies a full-stack feature for persistent, background “Actions” (automation rules) that monitor market events and execute portfolio operations automatically when user-defined conditions occur. The feature integrates with the existing FastAPI backend, Supabase/Postgres database, React frontend UX, and AI chat.

### Goals
- **Persistent rules**: Users can define actions that run in the background until paused/expired/completed.
- **Event-driven**: Actions watch market conditions and trigger when criteria are met.
- **Portfolio operations**: When triggered, actions can buy, sell, rebalance, or notify.
- **AI integration**: The AI chat can create/manage actions from natural language.
- **Seamless UX**: Dedicated “Actions” page with familiar styling, CRUD controls, and an “Add Action” modal.

### Current System Overview (as context)
- Backend: FastAPI app (`backend/main.py`) exposes portfolio, trade, chat, monitoring, auth, market, and health endpoints. Uses dependency services: `PortfolioManager`, `MarketDataService`, `AIPortfolioAgent`, `AuthenticationService`, `MarketContextService`, `DatabaseService` (Supabase).
- Database: Supabase/Postgres via `backend/database.py` with methods for users, portfolios, holdings, and transactions.
- Market data: `backend/market_data.py` integrates Twelve Data API + collaborative caching; supports watchlist and auto-refresh loop.
- Scheduling/monitoring: `backend/scheduler.py` runs background checks; `backend/monitoring_service.py` aggregates health.
- AI chat: `backend/ai_agent.py` (OpenAI function calling) handles portfolio and market requests; `/chat` endpoint wires data and calls the agent.
- Frontend: React app with routes (`frontend/src/App.js`) and sidebar nav (`frontend/src/components/Navigation.js`). Pages include Dashboard, Portfolio, Chat, Actions Log, Stock Detail.

### Core Concepts
- **Action**: A user-defined rule with type, target (symbol/portfolio), trigger conditions, execution payload, scheduling window, recurrence policy, and lifecycle state.
- **Trigger**: The event condition that causes an action to fire, e.g., price crosses threshold, percent change over window, time-based, trailing stop, etc.
- **Execution**: The side-effect when an action fires (buy/sell/rebalance/notify). Must be idempotent and recorded.

### Database Schema (Supabase/Postgres)
Create a new table `actions` and a related table `action_executions` for audit and retries.

actions
- id: uuid (pk, default gen_random_uuid())
- user_id: uuid (fk to users.id, not null, indexed)
- portfolio_id: uuid (fk to portfolios.id, nullable; default user’s primary portfolio if null)
- status: text (enum-like: 'active' | 'paused' | 'completed' | 'cancelled' | 'failed') default 'active'
- action_type: text (e.g., 'BUY' | 'SELL' | 'REBALANCE' | 'NOTIFY') not null
- symbol: text (nullable for REBALANCE/NOTIFY)
- quantity: numeric (nullable; for BUY/SELL exact size)
- amount_usd: numeric (nullable; alternative to quantity)
- trigger_type: text (e.g., 'price_above', 'price_below', 'change_pct', 'time_of_day', 'trailing_stop', 'ma_cross', 'volume_above') not null
- trigger_params: jsonb (thresholds, window, lookback, percent, schedule, timezone, etc.) not null
- valid_from: timestamptz (nullable; default now())
- valid_until: timestamptz (nullable; expiry)
- max_executions: int (nullable; default 1)
- executions_count: int (not null default 0)
- cooldown_seconds: int (nullable; minimum gap before re-trigger)
- last_triggered_at: timestamptz (nullable)
- last_evaluated_at: timestamptz (nullable)
- processing_lease_until: timestamptz (nullable; for concurrency control)
- notes: text (nullable)
- created_at: timestamptz default now()
- updated_at: timestamptz default now()

Indexes
- actions_user_idx on (user_id)
- actions_status_idx on (status)
- actions_symbol_idx on (symbol)
- actions_trigger_idx on (trigger_type)
- partial index for active evaluable actions (status='active' AND valid_until IS NULL OR valid_until > now())

action_executions
- id: uuid (pk)
- action_id: uuid (fk to actions.id, indexed)
- triggered_at: timestamptz not null default now()
- execution_status: text ('success' | 'failed') not null
- details: jsonb (snapshot of evaluation context, market data, request payload, etc.)
- transaction_id: uuid (nullable; link to portfolio transaction if applicable)
- error: text (nullable)

Notes on constraints
- For BUY/SELL, require at least one of quantity or amount_usd.
- For SELL, must validate available shares at execution time.
- Ensure `processing_lease_until > now()` is respected to avoid duplicate concurrent execution.

### Backend: New Service Layer (Database)
Extend `DatabaseService` with async methods:
- create_action(action: dict) -> action
- update_action(action_id, patch: dict) -> action
- get_actions(user_id, filters: dict) -> List[action]
- get_action_by_id(action_id, user_id) -> action
- delete_action(action_id, user_id) -> bool
- lease_actions_for_evaluation(limit: int, lease_seconds: int) -> List[action]
- record_action_execution(action_id, status, details, transaction_id=None) -> execution

Implementation details
- Use Supabase table RPC via `.table('actions')...` similar to existing holdings/transactions methods.
- Implement row-level ownership checks with user_id in queries.
- For leasing: single UPDATE with WHERE status='active' AND (processing_lease_until IS NULL OR processing_lease_until < now()) returning rows, setting `processing_lease_until = now() + interval` to gain a short evaluation lease.

### Backend: REST API (FastAPI)
Add endpoints (all require auth):
- GET /actions → list user actions with filters (status, symbol, type)
- POST /actions → create a new action
- GET /actions/{id} → fetch single action
- PATCH /actions/{id} → update fields (pause/resume, edit thresholds)
- DELETE /actions/{id} → soft-cancel by setting status='cancelled'
- POST /actions/{id}/simulate → preview evaluation given mocked market inputs
- POST /actions/{id}/execute-now → attempt to execute immediately (bypasses trigger)

Payloads
- Creation payload mirrors the schema fields, with validation on `action_type`, `trigger_type`, and `trigger_params` per trigger.
- PATCH supports toggling `status` and editing `trigger_params`, `quantity`, etc.

### Backend: Evaluator (Background Worker)
Add `ActionScheduler` similar to `MonitoringScheduler`:
- Loop interval: 10s-30s; dynamic based on market open/closed (reuse `MarketDataService.is_market_open()` to select shorter intervals during market hours).
- On each loop:
  1) Lease up to N actions (e.g., 100) via `lease_actions_for_evaluation`.
  2) Aggregate symbols and fetch quotes using `MarketDataService.get_multiple_quotes_optimized`.
  3) Evaluate triggers per action:
     - price_above/price_below: compare current price to threshold
     - change_pct: compare percent change over lookback (requires historical price, fall back to cached series; if unavailable, pull compact intraday)
     - trailing_stop: track peak and trigger when drawdown >= threshold (store peak in `trigger_params.runtime_state`)
     - time_of_day: check window with timezone
     - ma_cross: compute MA short/long and detect crossing (optional initial support)
  4) Enforce `valid_from/until`, `cooldown_seconds`, and `max_executions`.
  5) If triggered, execute:
     - BUY/SELL via `PortfolioManager` using current price, after cash/position checks
     - REBALANCE (defer to later iteration; out of scope for MVP if needed)
     - NOTIFY via email_service or chat notification
  6) Record `action_executions` and update action fields: `executions_count`, `last_triggered_at`, possibly mark `status='completed'` if max reached.
  7) Clear the lease.

Concurrency and reliability
- Use short `processing_lease_until` to avoid duplicate evaluation across instances.
- Wrap evaluation+execution in try/except; record failed executions.
- Idempotency: For BUY/SELL, dedupe by checking recent execution for same action inside lease window.

Watchlist integration
- Add symbols from all active actions to `MarketDataService._watchlist_symbols` to leverage auto-refresh.

### AI Chat Integration
Extend `AIPortfolioAgent.function_definitions` and handlers:
- add: `create_action` with parameters like `{ action_type, symbol, quantity|amount_usd, trigger_type, trigger_params, valid_until, notes }`.
- optionally add: `list_actions`, `update_action`, `cancel_action`.

Natural language examples
- “Sell 10 AAPL if price drops below 150 by Friday.” → `action_type=SELL`, `symbol=AAPL`, `quantity=10`, `trigger_type=price_below`, `trigger_params={threshold:150}`, `valid_until=<Friday EOD>`
- “Buy $2000 of MSFT when it rises 3% today.” → `action_type=BUY`, `amount_usd=2000`, `trigger_type=change_pct`, `trigger_params={window:'1d', change:3, direction:'up'}`

### Frontend UX
Routes and Navigation
- Add new route `/actions` and nav item “Actions” (separate from existing “Actions Log”).

Actions Page
- Table of actions: status, type, symbol, trigger, next evaluation, last triggered, executions, controls (Pause/Resume, Edit, Delete, Execute Now).
- Empty state with CTA to “Add Action”.
- Pagination and filters by status/symbol/type.

Add Action Modal
- Step 1: Choose Action Type (Buy, Sell, Rebalance, Notify)
- Step 2: Configure Target (symbol, quantity or amount)
- Step 3: Choose Trigger (price threshold, percent change, time window, trailing stop)
- Step 4: Schedule and Limits (validity window, cooldown, max executions)
- Step 5: Review & Create

Implementation
- New page `frontend/src/pages/ActionsPage.js` with styles matching `DashboardPage.css`/`PortfolioPage.css`.
- Reusable `ActionForm` component for the modal.
- Use axios calls to `/actions` endpoints; reflect changes immediately.

### Security & Validation
- All endpoints require JWT auth. Scope to `user_id` (row-level filters in DB queries).
- Server-side validation of payloads, symbols, and limits.
- Prevent self-trading errors (e.g., SELL > holdings).

### Telemetry & Monitoring
- Extend `/monitoring/status` to include action scheduler status: active, loop interval, counts of active/paused/completed, last evaluation time, recent errors.
- Email critical alerts only if persistent failures occur.

### Migration & Deployment
- Add SQL file `create_actions_table.sql` with DDL for `actions` and `action_executions`.
- Backend changes: database service methods, new API routes, scheduler wiring in `startup_event` alongside existing monitoring.
- Frontend changes: route, page, modal, navigation item.

### MVP Scope vs Iterations
MVP
- Triggers: price_above, price_below, change_pct (1d), time_of_day
- Actions: BUY, SELL, NOTIFY
- Cooldown, validity window, max_executions
- AI: create_action, list_actions

Later Iterations
- Trailing stop and MA cross
- REBALANCE strategies
- Advanced backtesting/simulation
- Bulk import/export of actions

### Testing Plan
- Unit tests for trigger evaluation logic (price thresholds, percent change, windows, cooldown).
- Integration tests for end-to-end create→evaluate→execute path using mock market data.
- Frontend e2e tests for creating, editing, pausing, and executing actions.

### Open Questions
- Do we enforce a minimum trade size or brokerage limits? (Assumed yes via existing portfolio validation.)
- Should action notifications also appear in Chat history? (Planned: optional.)
- Multi-portfolio support in UI? (MVP: single default portfolio.)


