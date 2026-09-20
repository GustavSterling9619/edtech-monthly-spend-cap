from edtech_spend_cap import DeliveryPlan, evaluate_and_prepare, project_monthly_spend


class RecordingClient:
    def __init__(self):
        self.calls = []

    def set_budget(self, hard_cap_usd):
        self.calls.append(hard_cap_usd)
        return {"ok": True}


def test_over_cap_plan_is_rejected_before_budget_call():
    plan = DeliveryPlan("course", learners=1000, deadline_days=1, reports=100, spend_cap_usd=1.0)
    client = RecordingClient()
    decision = evaluate_and_prepare(plan, client)
    assert project_monthly_spend(plan) > 1.0
    assert decision.allowed is False
    assert client.calls == []


def test_within_cap_plan_sets_monthly_budget():
    plan = DeliveryPlan("course", learners=10, deadline_days=30, reports=1, spend_cap_usd=20.0)
    client = RecordingClient()
    decision = evaluate_and_prepare(plan, client)
    assert decision.allowed is True
    assert client.calls == [20.0]
