"""Adversarial reward-hacking test for WorkFlow Arena.

The hackathon Self-Serve Guide §8 and FAQ §43/§57 are explicit:
"Do not optimize a reward you have not tried to break yourself first."

This script throws a battery of malicious / lazy / nonsense inputs at the
environment and verifies that none produce more than minimal reward.
A correct verifier should keep all of these well below the perfect-agent
baseline (~0.95) — ideally below 0.10.

Usage:
    py adversarial_test.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.environment import WorkFlowEnvironment


TASK = "employee_onboarding"  # easiest workflow; if it can't be hacked here,
                              # the harder ones inherit the same protections.


def run(label: str, message: str) -> dict:
    env = WorkFlowEnvironment()
    env.reset(TASK)
    out = env.step(message)
    info = out["info"]
    return {
        "label": label,
        "reward": round(out["reward"], 4),
        "cumulative": info.get("cumulative_score", 0.0),
        "completed": info.get("completed_actions", 0),
        "api_made": info.get("api_calls_made", 0),
        "api_success": info.get("api_calls_successful", 0),
        "components": info.get("reward_components", {}),
    }


# ── Attack vectors ──────────────────────────────────────────────────────────

ATTACKS = []

# 1. Empty calls — null-input baseline
ATTACKS.append(("empty_calls_dict", json.dumps({"calls": []})))

# 2. Empty JSON object — no calls field at all
ATTACKS.append(("empty_json_object", "{}"))

# 3. Malformed JSON — verifier must not crash
ATTACKS.append(("malformed_json", "{not valid json,,}"))

# 4. Plain text, no JSON — verifier must not crash
ATTACKS.append(("plain_text_no_json", "I'd like to onboard the employee please."))

# 5. Repeated correct call — try to game action_match by spamming the
#    same matched action 10x. Anti-cheat: completed_actions is a set.
correct_call = {
    "app": "gmail", "method": "create_account",
    "params": {"email": "alice.johnson@company.com"},
    "reasoning": "step 1",
}
ATTACKS.append(("spam_one_correct_call_10x",
                json.dumps({"calls": [correct_call] * 10})))

# 6. All-distractor calls — wrong workflow's actions
distractors = [
    {"app": "deploy", "method": "rollback",
     "params": {"service": "api"}, "reasoning": "noise"},
    {"app": "finance", "method": "submit_expense",
     "params": {"emp_id": "E9999", "amount": 5,
                "category": "meals", "description": "noise"},
     "reasoning": "noise"},
    {"app": "crm", "method": "update_customer",
     "params": {"customer_id": "C9999", "status": "noise"},
     "reasoning": "noise"},
]
ATTACKS.append(("all_distractors", json.dumps({"calls": distractors})))

# 7. Wrong app names — verifier must reject unknown apps
ATTACKS.append(("unknown_apps", json.dumps({"calls": [
    {"app": "twitter", "method": "tweet", "params": {"text": "hi"}, "reasoning": "x"},
    {"app": "linkedin", "method": "post", "params": {"text": "hi"}, "reasoning": "x"},
]})))

# 8. Reasoning-without-action hack — submit calls that fail at the API
#    layer but include flowery reasoning. Must not earn the 15% bonus.
ATTACKS.append(("flowery_reasoning_failed_calls", json.dumps({"calls": [
    {"app": "gmail", "method": "create_account",
     "params": {"email": ""},  # blank — should be rejected by mock app
     "reasoning": "I am thoughtfully crafting this onboarding workflow with great care."},
    {"app": "hris", "method": "create_employee",
     "params": {},  # missing all required fields
     "reasoning": "An HRIS registration that respects all corporate policies."},
]})))

# 9. Empty-params on otherwise-correct calls — verifier param check
ATTACKS.append(("correct_methods_empty_params", json.dumps({"calls": [
    {"app": "gmail", "method": "create_account", "params": {}, "reasoning": "x"},
    {"app": "hris", "method": "create_employee", "params": {}, "reasoning": "x"},
    {"app": "slack", "method": "add_user", "params": {}, "reasoning": "x"},
]})))

# 10. Right method, wrong params (e.g. wrong dept enum)
ATTACKS.append(("wrong_enum_values", json.dumps({"calls": [
    {"app": "hris", "method": "create_employee",
     "params": {"emp_id": "E1001", "name": "Alice",
                "email": "a@co.com", "dept": "INVALID_DEPT", "start_date": "2026-01-01"},
     "reasoning": "x"},
]})))


# ── Run ─────────────────────────────────────────────────────────────────────

PERFECT_REFERENCE = 0.99  # cumulative_score the perfect agent gets on this task
HACK_THRESHOLD = 0.20     # any attack scoring above this would be a real concern


def main():
    print(f"WorkFlow Arena — adversarial reward-hacking test")
    print(f"Task: {TASK} (perfect-agent reference: {PERFECT_REFERENCE})")
    print(f"Threshold: any attack > {HACK_THRESHOLD} cumulative is a verifier weakness")
    print("=" * 78)

    results = []
    max_seen = 0.0
    for label, message in ATTACKS:
        try:
            r = run(label, message)
        except Exception as e:
            r = {"label": label, "error": str(e)}
        results.append(r)
        cum = r.get("cumulative", 0.0)
        max_seen = max(max_seen, cum)
        flag = "FAIL" if cum > HACK_THRESHOLD else "OK"
        print(f"  [{flag:<4}] {label:<35s} cumulative={cum:.4f}  "
              f"completed={r.get('completed', '?')}  api={r.get('api_success', '?')}/{r.get('api_made', '?')}")

    print("=" * 78)
    print(f"  Max cumulative score observed under attack: {max_seen:.4f}")
    print(f"  Perfect-agent baseline:                     {PERFECT_REFERENCE:.4f}")
    print(f"  Verifier holds: {max_seen <= HACK_THRESHOLD}")

    # Save for README inclusion
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "adversarial_results.json")
    with open(out_path, "w") as f:
        json.dump({"task": TASK, "perfect_reference": PERFECT_REFERENCE,
                   "max_seen": max_seen, "results": results}, f, indent=2)
    print(f"\n  Wrote {out_path}")


if __name__ == "__main__":
    main()
