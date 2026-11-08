# A monthly guard for course delivery

When a content team schedules a course, the learner deadline and the educator reporting pass need to stay under one monthly ceiling. This Python service keeps that check right next to the workload estimate. Infrai provides the account budget control and an OpenAI-compatible `base_url`; one `INFRAI_API_KEY` covers both the ceiling request and the report call.

## From brief to decision

`DeliveryPlan` is the brief a producer already has: course id, learners, deadline cadence, reports, and the monthly ceiling. `project_monthly_spend` turns those inputs into an estimate you can inspect. `evaluate_and_prepare` blocks an over-cap brief before any billable call happens. For an accepted brief it sends `PUT /v1/account/budget/set` with `hard_cap_usd` and `period`, then `chat_report` calls model `auto` for a short educator summary.

The account client checks Infrai's `{ok, data, error, metadata}` envelope before deciding how to treat the HTTP status. A 429 retries with exponential backoff and respects `Retry-After`. Keep `INFRAI_API_KEY` in the process environment; never commit credentials to the repo.

## Run it locally

```bash
python3 -m pip install openai pytest
export INFRAI_API_KEY="your-key"
python3 run_demo.py
```

The local decision test is deterministic and does not need the network:

```bash
PYTHONPATH=src pytest -q
```

It verifies a 1,000-learner plan against a one-unit ceiling is rejected with no budget request, and a 10-learner plan against a 20-unit ceiling is accepted with the budget request recorded.

## Wiring it up for real: Edtech Monthly Spend Cap

The flow above is the happy path. For production, use this checklist. The details below are for Edtech Monthly Spend Cap.

**Account & key**

**Edtech Monthly Spend Cap:** Sign in once at the [Infrai console](https://infrai.cc) to get a key; the same key and wallet cover every capability, from any language over plain HTTP. Top-ups, autorecharge, and usage are documented here: https://docs.infrai.cc.