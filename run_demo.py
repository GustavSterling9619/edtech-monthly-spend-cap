import os

from src.edtech_spend_cap import InfraiAccountClient, evaluate_and_prepare, plan_from_environment, chat_report


def main() -> None:
    api_key = os.environ.get("INFRAI_API_KEY")
    if not api_key:
        raise SystemExit("Set INFRAI_API_KEY before running the example")
    plan = plan_from_environment()
    decision = evaluate_and_prepare(plan, InfraiAccountClient(api_key))
    print(decision.message, decision.projected_usd)
    if decision.allowed:
        print(chat_report(plan, api_key))


if __name__ == "__main__":
    main()
