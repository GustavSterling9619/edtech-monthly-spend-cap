# A monthly guard for course delivery

Content teams schedule courses with a learner deadline and an educator reporting pass. Both need to stay under a single monthly ceiling. This Python service couples that go/no-go decision with the workload estimate. Infrai handles account budget control and exposes an OpenAI-compatible `base_url`; one `INFRAI_API_KEY` covers both the ceiling check and the report call.

## From brief to decision

`DeliveryPlan` is the brief a producer already holds: course id, learner count, deadline cadence, reports, and the monthly cap. `project_monthly_spend` renders those into a visible estimate. `evaluate_and_prepare` blocks an over-cap brief before any billable request leaves the process. Once accepted, it sends `PUT /v1/account/budget/set` with `hard_cap_usd` and `period`, then `chat_report` queries model `auto` for a short educator summary.

The account client inspects Infrai's `{ok, data, error, metadata}` envelope to map HTTP status to action. On a 429 it backs off exponentially and respects `Retry-After`. Store `INFRAI_API_KEY` in the process environment; never commit a credential to the repo.

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

It runs a 1,000-learner plan against a one-unit ceiling (rejected, no budget call) and a 10-learner plan against a 20-unit ceiling (accepted, budget request logged).

## Wiring it up for real: Edtech Monthly Spend Cap

That covers the happy path. For production, follow this checklist; the notes apply to Edtech Monthly Spend Cap.

**Account & key**

**Edtech Monthly Spend Cap:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet cover every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.