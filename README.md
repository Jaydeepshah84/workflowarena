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

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Jaydeepshah84/workflowarena/blob/main/train_workflow_arena.ipynb)
[![HF Space](https://img.shields.io/badge/🤗%20HF%20Space-Live-green)](https://huggingface.co/spaces/jaydeepshah2025/workflow-arena)
[![GitHub](https://img.shields.io/badge/GitHub-Code-black?logo=github)](https://github.com/Jaydeepshah84/workflowarena)

> **Train AI agents to orchestrate real enterprise workflows across Gmail, Slack, Jira, HRIS, CRM, Deploy, and Finance. Every reward is VERIFIED via actual API responses.**

**Meta PyTorch OpenEnv Hackathon — Grand Finale Submission**
**Theme 3.1 + Scaler AI Labs Sub-theme: Multi-App RL Environment for Enterprise Workflows**

---

## 🎯 Why This Exists

Every day, enterprises run workflows that cost **billions of dollars** in human labor:

- **Onboarding**: Create email → add to Slack → set up HRIS → assign equipment → send welcome
- **Incident response**: Create ticket → update status page → page on-call → rollback → notify
- **Release management**: Close sprint → deploy services → update status → notify stakeholders

Current AI agents can't handle these because they can't orchestrate multiple apps with business rules. Existing RL environments test games, puzzles, or code — **not real work**.

**WorkFlow Arena fills that gap.**

---

## ⭐ What Makes This Different

| | WorkFlow Arena | Other RL Environments |
|---|---|---|
| Reward verification | **API response state** | LLM judge / regex |
| Domain | **Real enterprise apps** | Games, puzzles, math |
| Business rules | **Enforced via enums + policies** | None |
| Multi-step orchestration | **5–7 required actions/workflow** | Single-step tasks |
| Priority ordering | **Graded** | Not considered |
| Failure modes | **Invalid inputs, policy violations** | Binary pass/fail |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│  AGENT (Qwen3-1.7B + GRPO)                              │
│  Submits: {"calls": [{app, method, params, reasoning}]} │
└──────────────────────┬───────────────────────────────────┘
                       │ HTTP/WebSocket
                       ▼
┌──────────────────────────────────────────────────────────┐
│  WORKFLOW ARENA ENVIRONMENT (OpenEnv)                   │
│  • Routes calls to mock apps                            │
│  • Verifies API responses                               │
│  • Grades against required actions                      │
│  • Returns reward in (0, 1)                             │
└──────────────────────┬───────────────────────────────────┘
                       │
    ┌──────────────────┼──────────────────┐
    ▼                  ▼                  ▼
┌─────────┐      ┌─────────┐      ┌─────────┐
│  Gmail  │      │  Slack  │      │  Jira   │    ...
│ API     │      │ API     │      │ API     │
└─────────┘      └─────────┘      └─────────┘
```

---

## 🔧 7 Simulated Enterprise Apps

| App | Purpose | Methods |
|-----|---------|---------|
| **Gmail** | Email | `create_account`, `send_email` |
| **Slack** | Team chat | `add_user`, `send_message` |
| **Jira** | Tracking | `create_ticket`, `update_ticket`, `close_sprint` |
| **HRIS** | HR system | `create_employee`, `assign_equipment` |
| **CRM** | Customers | `update_customer`, `create_support_ticket` |
| **Deploy** | Release mgmt | `service`, `rollback`, `update_status_page` |
| **Finance** | Expenses | `submit_expense`, `approve_expense` |

All apps enforce **real business rules**:
- Valid department enums (engineering, sales, marketing, hr, finance, support, operations)
- Expense policy limits (meals $100, travel $1000, equipment $2000, training $5000)
- Priority enums (low, medium, high, critical, p0)
- Valid Slack channels (#general, #engineering, #sales, #support, #hr)

---

## 📋 5 Workflows (Progressive Difficulty)

| # | Workflow | Difficulty | Apps Used | Required Actions |
|---|----------|-----------|-----------|------------------|
| 1 | **Employee Onboarding** | Easy | Gmail, HRIS, Slack | 6 |
| 2 | **Customer Support Triage** | Medium | CRM, Jira, Slack, Gmail | 5 |
| 3 | **Expense Approval** | Medium | Finance, Gmail, Slack | 5 |
| 4 | **Sprint Release** | Hard | Slack, Deploy, Jira, Gmail | 7 |
| 5 | **P0 Incident Response** | Expert | Jira, Deploy, Slack, Gmail, CRM | 7 |

**30 total required actions** across all workflows.

---

## 📝 Action Format

```json
{
  "calls": [
    {
      "app": "gmail",
      "method": "create_account",
      "params": {"email": "alice.johnson@company.com"},
      "reasoning": "Step 1: Create email account for new engineering hire"
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
      "reasoning": "Step 2: Register in HRIS before Slack/equipment setup"
    }
  ]
}
```

---

## 🎯 Reward Function (5-Component)

| Component | Weight | What it rewards |
|-----------|--------|-----------------|
| Correct API call | **70%** | API succeeds AND matches a required action |
| Reasoning quality | **15%** | Agent explains WHY it made the call |
| Priority order | **15%** | Completing actions in correct business sequence |
| Failed API call | 0% | No reward (but no penalty — encourages exploration) |

Rewards clamped to `(0.01, 0.99)` — always strictly between 0 and 1.

---

## 📊 Baseline Results

Perfect agent baseline (scripted correct responses):

| Workflow | Score |
|----------|-------|
| Employee Onboarding | **0.990** |
| Expense Approval | **0.990** |
| Customer Support | **0.990** |
| Sprint Release | **0.990** |
| Incident Response | **0.793** |
| **Average** | **0.951** |

Trained agent results (Qwen3-1.7B, 50 episodes of GRPO):

| Workflow | Before | After | Improvement |
|----------|--------|-------|-------------|
| Employee Onboarding | 0.15 | 0.72 | **4.8×** |
| Expense Approval | 0.10 | 0.65 | **6.5×** |
| Customer Support | 0.08 | 0.48 | **6.0×** |

---

## 🚀 Quick Start

### Try It Online (Easiest)

Visit the live Gradio UI: **[https://huggingface.co/spaces/jaydeepshah2025/workflow-arena](https://huggingface.co/spaces/jaydeepshah2025/workflow-arena)**

### Run Locally

```bash
git clone https://github.com/Jaydeepshah84/workflowarena.git
cd workflowarena
pip install -r requirements.txt
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

Open http://localhost:7860 in your browser.

### With Docker

```bash
docker build -t workflow-arena .
docker run -p 7860:7860 workflow-arena
```

### Validate Environment (no training needed)

```bash
python baseline_test.py
```

### Train with GRPO + Unsloth

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Jaydeepshah84/workflowarena/blob/main/train_workflow_arena.ipynb)

Or run locally:

```bash
export API_BASE_URL="https://api.openai.com/v1"
export API_KEY="your-openai-key"
export MODEL_NAME="gpt-4o-mini"
python inference.py
```

---

## 🌐 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/tasks` | List all workflows |
| `POST` | `/reset` | Start episode — `{"task_name": "employee_onboarding"}` |
| `POST` | `/step` | Submit API calls |
| `GET` | `/state?session_id=...` | Get episode state |
| `WS` | `/ws` | WebSocket session (persistent) |
| `GET` | `/` | Gradio UI (live demo) |

---

## 📂 Project Structure

```
workflowarena/
├── server/
│   ├── __init__.py
│   ├── app.py                    FastAPI server + Gradio mount
│   ├── environment.py            Core RL env with API routing
│   └── Dockerfile
├── mock_apps.py                  Gmail/Slack/Jira/HRIS/CRM/Deploy/Finance
├── workflows.py                  5 workflow definitions
├── models.py                     Pydantic types (Action/Observation/State)
├── ui.py                         Gradio UI
├── client.py                     HTTP client
├── inference.py                  Baseline inference with [START/STEP/END] logs
├── baseline_test.py              Validates env with scripted perfect agent
├── train_workflow_arena.ipynb    GRPO training notebook for Colab
├── openenv.yaml                  OpenEnv metadata
├── pyproject.toml                Package definition
├── Dockerfile                    Root Dockerfile
├── requirements.txt              Dependencies
├── uv.lock                       Locked versions
├── README.md                     This file
├── BLOG.md                       Mini-blog for submission
└── PITCH.md                      3-minute pitch script
```

---

## 🛠️ Tech Stack

- **Environment**: Python 3.11 + FastAPI + Pydantic
- **UI**: Gradio 4
- **Hosting**: HuggingFace Spaces (Docker)
- **Training**: TRL (GRPOTrainer) + Unsloth + vLLM (colocate)
- **Base Model**: Qwen3-1.7B (Colab T4 compatible)
- **Tracking**: trackio

---

## 🎓 For Judges

**Links:**
- 🏢 **Live Demo**: https://huggingface.co/spaces/jaydeepshah2025/workflow-arena
- 💻 **GitHub**: https://github.com/Jaydeepshah84/workflowarena
- 📓 **Training Notebook**: [Open in Colab](https://colab.research.google.com/github/Jaydeepshah84/workflowarena/blob/main/train_workflow_arena.ipynb)
- 📝 **Blog**: [BLOG.md](BLOG.md)
- 🎤 **3-Minute Pitch**: [PITCH.md](PITCH.md)

**What to check:**
1. **Innovation**: Verifiable API-based rewards — no LLM judges, no subjective grading
2. **Real-world relevance**: 7 mock apps modeling actual enterprise software
3. **Reward improvement**: See `train_workflow_arena.ipynb` for training curves
4. **Pipeline**: GRPO + Unsloth + TRL + OpenEnv — all frontier tooling
5. **Business rules**: Enums, policy limits, priority ordering all enforced

---

## 🙏 Acknowledgments

Built by **Jaydeep Shah** and **Snigdha Aswal** for the Meta PyTorch OpenEnv Hackathon 2026 Grand Finale at Scaler School of Technology, Bangalore.

Thanks to:
- **Meta PyTorch team** for OpenEnv
- **Hugging Face team** for TRL, Spaces, and hackathon infrastructure
- **Unsloth team** for efficient RL training
- **Scaler School of Technology** for hosting the grand finale

---

## 📜 License

MIT
