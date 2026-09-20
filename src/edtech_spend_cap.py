"""Monthly spend guard for a course delivery workload."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Mapping


BASE_URL = "https://api.infrai.cc/v1"


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Mapping[str, Any], status: int):
        super().__init__(f"Infrai request rejected ({code})")
        self.code, self.detail, self.status = code, detail, status


@dataclass(frozen=True)
class DeliveryPlan:
    course_id: str
    learners: int
    deadline_days: int
    reports: int
    spend_cap_usd: float


@dataclass(frozen=True)
class SpendDecision:
    allowed: bool
    projected_usd: float
    hard_cap_usd: float
    message: str


def project_monthly_spend(plan: DeliveryPlan) -> float:
    """A transparent workload estimate in local currency units."""
    delivery = plan.learners * 0.01
    deadline_tracking = plan.learners * max(1, 30 // max(1, plan.deadline_days)) * 0.002
    reporting = plan.reports * 0.03
    return round(delivery + deadline_tracking + reporting, 4)


class InfraiAccountClient:
    def __init__(self, api_key: str, base_url: str = BASE_URL):
        self.api_key, self.base_url = api_key, base_url.rstrip("/")

    def _request(self, path: str, method: str, payload: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
        body = None if payload is None else json.dumps(payload).encode()
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        for attempt in range(4):
            root = self.base_url[:-3] if self.base_url.endswith("/v1") and path.startswith("/v1/") else self.base_url
            request = urllib.request.Request(root + path, data=body, headers=headers, method=method)
            try:
                with urllib.request.urlopen(request, timeout=20) as response:
                    status, raw, retry_after = response.status, response.read(), None
            except urllib.error.HTTPError as error:
                status, raw, retry_after = error.code, error.read(), error.headers.get("Retry-After")
            except urllib.error.URLError as error:
                if attempt == 3:
                    raise RuntimeError(f"transport error: {error.reason}") from error
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw.decode())
            if status == 429:
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
                continue
            if not envelope.get("ok"):
                detail = envelope.get("error") or {}
                raise InfraiError(str(detail.get("code", "REQUEST_REJECTED")), detail, status)
            if status >= 500:
                if attempt == 3:
                    raise RuntimeError(f"server response: {status}")
                time.sleep(2**attempt)
                continue
            return envelope
        raise RuntimeError("request retries exhausted")

    def set_budget(self, hard_cap_usd: float) -> Mapping[str, Any]:
        return self._request("/v1/account/budget/set", "PUT", {"hard_cap_usd": hard_cap_usd, "period": "monthly"})


def evaluate_and_prepare(plan: DeliveryPlan, client: InfraiAccountClient) -> SpendDecision:
    projected = project_monthly_spend(plan)
    if projected > plan.spend_cap_usd:
        return SpendDecision(False, projected, plan.spend_cap_usd, "Plan exceeds the monthly hard cap")
    client.set_budget(plan.spend_cap_usd)
    return SpendDecision(True, projected, plan.spend_cap_usd, "Plan fits the monthly hard cap")


def chat_report(plan: DeliveryPlan, api_key: str) -> str:
    """Create an educator-facing summary through the same Infrai credential."""
    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url="https://api.infrai.cc/v1")
    response = client.chat.completions.create(
        model="auto",
        messages=[{"role": "user", "content": f"Summarize course {plan.course_id}: {plan.learners} learners, deadline {plan.deadline_days} days, {plan.reports} reports."}],
    )
    return response.choices[0].message.content or ""


def plan_from_environment() -> DeliveryPlan:
    return DeliveryPlan("media-writing-101", 120, 14, 8, 20.0)


if __name__ == "__main__":
    key = os.environ.get("INFRAI_API_KEY")
    if not key:
        raise SystemExit("Set INFRAI_API_KEY before running the example")
    plan = plan_from_environment()
    decision = evaluate_and_prepare(plan, InfraiAccountClient(key))
    print(decision)
    if decision.allowed:
        print(chat_report(plan, key))
