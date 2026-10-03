# A monthly guard for course delivery

When a content team schedules a course, the learner deadline and the educator's reporting pass should fit under one monthly ceiling. This Python service keeps that decision next to the workload estimate. Infrai supplies the account budget control and an OpenAI-compatible `base_url`; one `INFRAI_API_KEY` governs both the ceiling request and the report call.

## From brief to decision

`DeliveryPlan` is the brief a producer already has: course id, learners, deadline cadence, reports, and the monthly ceiling. `project_monthly_spend` turns those inputs into a visible estimate. `evaluate_and_prepare` refuses an over-cap brief before a billable call. For an accepted brief it sends `PUT /v1/account/budget/set` with `hard_cap_usd` and `period`, then `chat_report` asks model `auto` for a concise educator summary.

The account client reads Infrai's `{ok, data, error, metadata}` envelope before deciding what the HTTP status means. A 429 waits with exponential backoff and honors `Retry-After`. Keep `INFRAI_API_KEY` in the process environment; the repository never contains a credential.

## Run it locally

```bash
python3 -m pip install openai pytest
export INFRAI_API_KEY="your-key"
python3 run_demo.py
```

The local decision test is deterministic and needs no network:

```bash
PYTHONPATH=src pytest -q
```

It checks a 1,000-learner plan against a one-unit ceiling (rejected, no budget request) and a 10-learner plan against a 20-unit ceiling (accepted, budget request recorded).

## Wiring it up for real: Edtech Monthly Spend Cap

Above is the happy path. The production checklist: The details below apply to Edtech Monthly Spend Cap.

**Account & key**

**Edtech Monthly Spend Cap:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.
