"""Baseline test for WorkFlow Arena — proves the environment works end-to-end.

Runs each workflow with a scripted agent that makes CORRECT API calls.
This is NOT training — it validates the environment and produces
comparison metrics for the pitch.

Usage:
    py baseline_test.py
"""

import json
import httpx
import time


# Use live HF Space or localhost
ENV_URL = "https://jaydeepshah2025-workflow-arena.hf.space"
# ENV_URL = "http://localhost:7860"  # uncomment for local testing


# Scripted "perfect" agent responses for each workflow
PERFECT_RESPONSES = {
    "employee_onboarding": [
        {
            "calls": [
                {"app": "gmail", "method": "create_account",
                 "params": {"email": "alice.johnson@company.com"},
                 "reasoning": "Step 1: Create email account for new hire"},
                {"app": "hris", "method": "create_employee",
                 "params": {"emp_id": "E1001", "name": "Alice Johnson",
                            "email": "alice.johnson@company.com",
                            "dept": "engineering", "start_date": "2026-04-28"},
                 "reasoning": "Step 2: Register in HRIS under engineering dept"},
                {"app": "slack", "method": "add_user",
                 "params": {"user_id": "alice.johnson",
                            "channels": ["#general", "#engineering"]},
                 "reasoning": "Step 3: Add to required Slack channels"},
            ]
        },
        {
            "calls": [
                {"app": "hris", "method": "assign_equipment",
                 "params": {"emp_id": "E1001",
                            "equipment": ["laptop", "monitor", "keyboard"]},
                 "reasoning": "Step 4: Assign standard engineering kit"},
                {"app": "gmail", "method": "send_email",
                 "params": {"to": "alice.johnson@company.com",
                            "subject": "Welcome to the team!",
                            "body": "Hi Alice, welcome aboard. Check Slack for onboarding info."},
                 "reasoning": "Step 5: Send welcome email"},
                {"app": "slack", "method": "send_message",
                 "params": {"channel": "#engineering",
                            "text": "Welcoming Alice Johnson to the team!"},
                 "reasoning": "Step 6: Announce to the team"},
            ]
        },
    ],

    "expense_approval": [
        {
            "calls": [
                {"app": "finance", "method": "submit_expense",
                 "params": {"emp_id": "E1001", "amount": 85,
                            "category": "meals", "description": "Client dinner"},
                 "reasoning": "Under $100 meal limit — auto-approved"},
                {"app": "finance", "method": "submit_expense",
                 "params": {"emp_id": "E1002", "amount": 1500,
                            "category": "travel", "description": "Conference travel"},
                 "reasoning": "Over $1000 travel limit — needs manager approval"},
                {"app": "finance", "method": "submit_expense",
                 "params": {"emp_id": "E1003", "amount": 1800,
                            "category": "equipment", "description": "New laptop"},
                 "reasoning": "Under $2000 equipment limit — auto-approved"},
            ]
        },
        {
            "calls": [
                {"app": "gmail", "method": "send_email",
                 "params": {"to": "E1001@company.com",
                            "subject": "Expense approved: $85",
                            "body": "Your meal expense has been auto-approved."},
                 "reasoning": "Notify employee of auto-approval"},
                {"app": "slack", "method": "send_message",
                 "params": {"channel": "#general",
                            "text": "Travel expense pending manager approval"},
                 "reasoning": "Escalate travel expense needing approval"},
            ]
        },
    ],

    "customer_support": [
        {
            "calls": [
                {"app": "crm", "method": "create_support_ticket",
                 "params": {"customer_id": "C2050",
                            "issue": "API 500 errors on bulk operations",
                            "assignee": "support_team"},
                 "reasoning": "Log the issue in CRM for enterprise customer"},
                {"app": "jira", "method": "create_ticket",
                 "params": {"title": "API 500 errors on bulk ops",
                            "ticket_type": "bug", "priority": "high"},
                 "reasoning": "Escalate to engineering as high-priority bug"},
                {"app": "slack", "method": "send_message",
                 "params": {"channel": "#engineering",
                            "text": "Critical issue from enterprise customer Acme Corp"},
                 "reasoning": "Alert engineering team immediately"},
            ]
        },
        {
            "calls": [
                {"app": "gmail", "method": "send_email",
                 "params": {"to": "contact@acme.com",
                            "subject": "We are investigating your issue",
                            "body": "Our team is investigating. Expected resolution within 4 hours."},
                 "reasoning": "Acknowledge customer with SLA commitment"},
                {"app": "crm", "method": "update_customer",
                 "params": {"customer_id": "C2050", "status": "escalated"},
                 "reasoning": "Update customer status to escalated"},
            ]
        },
    ],

    "sprint_release": [
        {
            "calls": [
                {"app": "slack", "method": "send_message",
                 "params": {"channel": "#engineering",
                            "text": "Starting release v1.1.0 deployment"},
                 "reasoning": "Notify team release is starting"},
                {"app": "deploy", "method": "update_status_page",
                 "params": {"status": "degraded"},
                 "reasoning": "Set public status to degraded during deploy"},
                {"app": "deploy", "method": "service",
                 "params": {"service": "api", "version": "v1.1.0"},
                 "reasoning": "Deploy API service first"},
            ]
        },
        {
            "calls": [
                {"app": "deploy", "method": "service",
                 "params": {"service": "web", "version": "v1.1.0"},
                 "reasoning": "Deploy web service after API"},
                {"app": "jira", "method": "close_sprint",
                 "params": {"sprint_id": "SPRINT-1"},
                 "reasoning": "Close the sprint after successful deploy"},
                {"app": "deploy", "method": "update_status_page",
                 "params": {"status": "operational"},
                 "reasoning": "Restore operational status"},
                {"app": "gmail", "method": "send_email",
                 "params": {"to": "stakeholders@company.com",
                            "subject": "Release v1.1.0 complete",
                            "body": "Release deployed successfully."},
                 "reasoning": "Notify stakeholders of successful release"},
            ]
        },
    ],

    "incident_response": [
        {
            "calls": [
                {"app": "jira", "method": "create_ticket",
                 "params": {"title": "P0: API service down",
                            "ticket_type": "incident", "priority": "p0"},
                 "reasoning": "Create P0 incident ticket immediately"},
                {"app": "deploy", "method": "update_status_page",
                 "params": {"status": "major_outage"},
                 "reasoning": "Alert customers with major outage status"},
                {"app": "slack", "method": "send_message",
                 "params": {"channel": "#engineering",
                            "text": "P0 incident — API down, paging oncall"},
                 "reasoning": "Page on-call engineer via Slack"},
                {"app": "deploy", "method": "rollback",
                 "params": {"service": "api"},
                 "reasoning": "Rollback broken deploy to restore service"},
            ]
        },
        {
            "calls": [
                {"app": "gmail", "method": "send_email",
                 "params": {"to": "leadership@company.com",
                            "subject": "Incident report: API outage",
                            "body": "P0 incident resolved via rollback. Full postmortem to follow."},
                 "reasoning": "Notify stakeholders of incident and resolution"},
                {"app": "deploy", "method": "update_status_page",
                 "params": {"status": "operational"},
                 "reasoning": "Restore operational status after rollback"},
                {"app": "crm", "method": "update_customer",
                 "params": {"customer_id": "C2050", "status": "notified"},
                 "reasoning": "Mark enterprise customers as notified"},
            ]
        },
    ],
}


def run_workflow(http: httpx.Client, task_name: str):
    print(f"\n{'='*60}")
    print(f"Testing workflow: {task_name}")
    print('='*60)

    # Reset
    r = http.post(f"{ENV_URL}/reset", json={"task_name": task_name}).json()
    session_id = r["session_id"]
    required = r["info"]["total_required_actions"]
    print(f"Required actions: {required}")

    total_reward = 0.0
    rewards = []
    responses = PERFECT_RESPONSES.get(task_name, [])

    for i, response in enumerate(responses):
        step_data = http.post(
            f"{ENV_URL}/step",
            json={"session_id": session_id, "message": json.dumps(response)},
        ).json()

        reward = step_data.get("reward", 0.0)
        rewards.append(reward)
        total_reward = step_data["info"].get("cumulative_score", 0.0)
        completed = step_data["info"].get("completed_actions", 0)
        api_made = step_data["info"].get("api_calls_made", 0)
        api_success = step_data["info"].get("api_calls_successful", 0)

        print(f"  Step {i+1}: reward={reward:.3f} "
              f"completed={completed}/{required} "
              f"api={api_success}/{api_made}")

        if step_data.get("done"):
            break

    print(f"\nFinal score: {total_reward:.3f}")
    print(f"Rewards: {[f'{r:.2f}' for r in rewards]}")
    return total_reward, rewards


def main():
    print("WorkFlow Arena — Baseline Test")
    print(f"Environment: {ENV_URL}")

    # Wait for health
    try:
        health = httpx.get(f"{ENV_URL}/health", timeout=10).json()
        print(f"Health: {health}")
    except Exception as e:
        print(f"ERROR: {e}")
        return

    workflows = [
        "employee_onboarding",
        "expense_approval",
        "customer_support",
        "sprint_release",
        "incident_response",
    ]

    results = {}
    with httpx.Client(timeout=120.0) as http:
        for wf in workflows:
            time.sleep(1)  # Avoid rate limits
            score, rewards = run_workflow(http, wf)
            results[wf] = {"score": score, "rewards": rewards}

    print("\n" + "=" * 60)
    print("SUMMARY — Perfect Agent Baseline")
    print("=" * 60)
    for wf, data in results.items():
        print(f"  {wf:30s}: {data['score']:.3f}")

    avg = sum(r["score"] for r in results.values()) / len(results)
    print(f"\n  Average score across all workflows: {avg:.3f}")
    print("\nThis proves the environment works end-to-end with verifiable rewards.")


if __name__ == "__main__":
    main()
