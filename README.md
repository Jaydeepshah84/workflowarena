---
title: WorkFlow Arena
emoji: 🏢
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
tags:
  - openenv
---

# 🏢 WorkFlow Arena — Multi-App Enterprise Workflow RL Environment

> **Train AI agents to orchestrate real enterprise workflows across Gmail, Slack, Jira, HRIS, CRM, and more. Every reward is VERIFIED via actual API responses.**

**Theme 3.1 + Scaler AI Labs Sub-theme** — Multi-App RL Environment for Enterprise Workflows

Meta PyTorch OpenEnv Hackathon Grand Finale Submission.

## The Problem

Enterprise agents today can generate text, but can they actually **do the job**? Completing real business workflows — onboarding employees, triaging support tickets, managing releases, responding to incidents — requires orchestrating dozens of apps with correct sequencing, error handling, and business rules.

Existing RL environments test agents on games, puzzles, or code — not real enterprise work. WorkFlow Arena fills that gap.

## What Makes This Different

- **7 Simulated Enterprise Apps** — Gmail, Slack, Jira, HRIS, CRM, Deploy, Finance — with realistic API contracts
- **100% Verifiable Rewards** — every reward comes from actual API response success, not LLM judgment
- **Business Rule Enforcement** — validates department assignments, policy limits, priority levels, status transitions
- **Multi-Step Orchestration** — agents must execute 5–7 sequential actions across multiple apps
- **Priority-Aware Grading** — bonus reward for completing actions in the correct business order

## 5 Enterprise Workflows

| # | Workflow | Difficulty | Apps Used | Required Actions |
|---|----------|-----------|-----------|------------------|
| 1 | **Employee Onboarding** | Easy | Gmail, HRIS, Slack | 6 |
| 2 | **Customer Support Triage** | Medium | CRM, Jira, Slack, Gmail | 5 |
| 3 | **Expense Approval** | Medium | Finance, Gmail, Slack | 5 |
| 4 | **Sprint Release Management** | Hard | Slack, Deploy, Jira, Gmail | 7 |
| 5 | **P0 Incident Response** | Expert | Jira, Deploy, Slack, Gmail, CRM | 7 |

## Action Format

```json
{
  "calls": [
    {
      "app": "gmail",
      "method": "create_account",
      "params": {"email": "alice.johnson@company.com"},
      "reasoning": "Step 1: Create email account for new employee"
    },
    {
      "app": "hris",
      "method": "create_employee",
      "params": {
        "emp_id": "E1001",
        "name": "Alice Johnson",
        "email": "alice.johnson@company.com",
        "dept": "engineering",
        "start_date": "2026-04-28"
      },
      "reasoning": "Step 2: Create HRIS record for engineering dept"
    }
  ]
}
```

## Available APIs (7 apps, 15+ methods)

| App | Methods |
|-----|---------|
| **gmail** | `create_account(email)`, `send_email(to, subject, body)` |
| **slack** | `add_user(user_id, channels)`, `send_message(channel, text)` |
| **jira** | `create_ticket(title, ticket_type, priority, assignee)`, `update_ticket(ticket_id, status)`, `close_sprint(sprint_id)` |
| **hris** | `create_employee(emp_id, name, email, dept, start_date)`, `assign_equipment(emp_id, equipment)` |
| **crm** | `update_customer(customer_id, status, tier)`, `create_support_ticket(customer_id, issue, assignee)` |
| **deploy** | `service(service, version)`, `rollback(service)`, `update_status_page(status)` |
| **finance** | `submit_expense(emp_id, amount, category, description)`, `approve_expense(expense_id, approver)` |

## Reward Function (5 components)

| Component | Weight | What it rewards |
|-----------|--------|----------------|
| Correct API call | 70% | API call succeeds AND matches a required action |
| Reasoning quality | 15% | Agent explains WHY it made the call |
| Priority order | 15% | Completing actions in the correct business sequence |
| False positive | 0% | Failed API calls get no reward (no penalty to encourage exploration) |

Rewards are scaled and clamped to (0.01, 0.99). Cumulative score tracked across the episode.

## Why "Multi-App Enterprise Workflow"?

Scaler AI Labs sub-theme asks: *"Create RL environments to demonstrate complex workflows, business rule nuances etc in a large enterprise."* WorkFlow Arena delivers exactly that:

- ✅ Complex multi-step workflows (5–7 sequential actions)
- ✅ Business rule nuances (department configs, priority levels, policy limits)
- ✅ Large enterprise apps (Gmail, Slack, Jira, HRIS, CRM, Deploy, Finance)
- ✅ Verifiable rewards via API responses
- ✅ Adjustable difficulty (5 levels from onboarding to incident response)

## Setup

```bash
pip install -r requirements.txt
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

```bash
docker build -t workflow-arena .
docker run -p 7860:7860 workflow-arena
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/reset` | Start workflow — `{"task_name": "employee_onboarding"}` |
| `POST` | `/step` | Submit API calls |
| `GET` | `/state?session_id=...` | Current state |
| `GET` | `/tasks` | List all workflows |
| `WS` | `/ws` | WebSocket session |

## Running Baseline Inference

```bash
export API_BASE_URL="https://your-llm-api/v1"
export API_KEY="your-api-key"
export MODEL_NAME="gpt-4o-mini"
python inference.py
```

## Project Structure

```
├── server/
│   ├── __init__.py
│   ├── app.py             FastAPI server + Gradio UI mount
│   ├── environment.py     Core RL env with API execution
│   └── Dockerfile
├── mock_apps.py           Simulated Gmail/Slack/Jira/HRIS/CRM/Deploy/Finance
├── workflows.py           5 enterprise workflow definitions
├── models.py              Pydantic types
├── ui.py                  Gradio UI
├── client.py              HTTP client
├── inference.py           Baseline inference script
├── openenv.yaml           OpenEnv metadata
├── pyproject.toml         Package definition
├── Dockerfile             Container definition
├── requirements.txt       Dependencies
└── README.md
```

## Live Demo

**https://huggingface.co/spaces/jaydeepshah2025/workflow-arena**
