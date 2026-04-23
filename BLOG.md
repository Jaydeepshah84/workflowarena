# WorkFlow Arena: Training AI Agents to Orchestrate Enterprise Workflows

**How we built an RL environment where every reward is verified by real API responses — not LLM judgment.**

---

*Submission for the Meta PyTorch OpenEnv Hackathon Grand Finale — Theme 3.1 + Scaler AI Labs Sub-theme.*

## The Problem

Enterprise agents today can generate text, but can they actually **do the job**?

Every day, companies run workflows that look like this:
- **Onboarding**: Create email → add to Slack → set up HRIS → assign equipment → send welcome email
- **Incident response**: Create Jira ticket → update status page → page on-call → rollback deploy → notify customers

These workflows cost billions of dollars in human labor annually. But current AI agents can't handle them because:
1. They can't orchestrate multiple apps
2. They can't follow business rules (priority, policy, sequence)
3. There's no standardized way to train them on real workflow data

Existing RL environments test agents on games, puzzles, or code — not real enterprise work. **WorkFlow Arena fills that gap.**

## The Environment

WorkFlow Arena simulates a complete enterprise app ecosystem:

| App | Purpose | Methods |
|-----|---------|---------|
| **Gmail** | Email | `create_account`, `send_email` |
| **Slack** | Team communication | `add_user`, `send_message` |
| **Jira** | Issue tracking | `create_ticket`, `update_ticket`, `close_sprint` |
| **HRIS** | Employee management | `create_employee`, `assign_equipment` |
| **CRM** | Customer management | `update_customer`, `create_support_ticket` |
| **Deploy** | Release management | `service`, `rollback`, `update_status_page` |
| **Finance** | Expense management | `submit_expense`, `approve_expense` |

Every API call has a **deterministic, verifiable response** — the key innovation that makes rewards objective.

## 5 Workflows, Progressive Difficulty

| # | Workflow | Difficulty | Apps | Actions |
|---|----------|-----------|------|---------|
| 1 | Employee Onboarding | Easy | 3 | 6 |
| 2 | Customer Support Triage | Medium | 4 | 5 |
| 3 | Expense Approval | Medium | 3 | 5 |
| 4 | Sprint Release Management | Hard | 4 | 7 |
| 5 | Production Incident Response | Expert | 5 | 7 |

## Why Verifiable Rewards Matter

The hackathon judges were explicit: *"Prefer tasks with crisp verification over tasks that only 'look good' to a human."*

Every reward in WorkFlow Arena comes from actual API state:
- ✅ Email account created? Check `gmail.accounts` dict.
- ✅ Slack user added to right channels? Check `slack.users` state.
- ✅ Employee in right department? HRIS enum validation.
- ✅ Deploy rolled back? Service version reverted.

No LLM judges. No subjective grading. No reward hacking loopholes.

## Multi-Component Reward Function

Each required action earns points across dimensions:
- **70%** for correct API call succeeding
- **15%** bonus for providing reasoning
- **15%** bonus for correct priority order

This encourages agents to think before acting AND execute in the right business sequence.

## Training Results (real numbers, committed plots)

We ran two training tracks:

**Track 1 — Local bandit agent** (`train_simple_agent.py`, 80 episodes per workflow, no GPU). Produces the committed PNGs in the repo.

| Workflow | Random Baseline | Trained Agent | Improvement |
|----------|----------------:|--------------:|------------:|
| Employee Onboarding | 0.267 | **0.617** | **2.3×** |
| Expense Approval | 0.389 | **0.740** | **1.9×** |
| Customer Support | 0.389 | **0.680** | **1.7×** |

![Reward Curve](reward_curve.png)

![Random vs Trained](comparison_chart.png)

**Track 2 — LLM rollout** (`train_workflow_arena.ipynb`, Qwen3-1.7B on Colab free T4). Produces `llm_rollout_curve.png` and the per-workflow reward bars.

The bandit agent learned to:
1. Pick action templates that match the required workflow steps
2. Prefer calls that succeed under enum/policy validation
3. Suppress distractor actions that don't score

The LLM agent (when trained with GRPO) goes further — it generates the parameters from context instead of picking from a template pool.

## Tech Stack

- **Environment**: Python + FastAPI + Pydantic
- **UI**: Gradio (live demo at the HF Space URL)
- **Hosting**: HuggingFace Spaces (Docker)
- **Training**: TRL GRPOTrainer + Unsloth + vLLM (colocate)
- **Base Model**: Qwen3-1.7B (runs on Colab free tier)

## Links

- 🏢 **Live Environment**: https://huggingface.co/spaces/jaydeepshah2025/workflow-arena
- 💻 **GitHub**: https://github.com/Jaydeepshah84/workflowarena
- 📓 **Training Notebook**: `train_workflow_arena.ipynb`
- 🏋️ **Local Training Script**: `train_simple_agent.py`

## What's Next

Future extensions:
- **Schema drift**: Business rules that change mid-workflow
- **Partial failures**: API timeouts and retries
- **Multi-user scenarios**: Agents collaborating on workflows
- **Real API connectors**: Bridge to actual Gmail/Slack/Jira

## Acknowledgments

- Meta PyTorch team for OpenEnv
- Hugging Face team for TRL, Spaces, and the hackathon infrastructure
- Unsloth team for efficient RL training
- Scaler School of Technology for hosting the grand finale

---

*Built by Jaydeep Shah and Snigdha Aswal for the Meta PyTorch OpenEnv Hackathon 2026 Grand Finale.*
