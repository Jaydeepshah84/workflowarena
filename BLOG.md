# WorkFlow Arena: Training AI Agents to Orchestrate Real Enterprise Workflows

**An OpenEnv RL environment where every reward is verified by an actual API response — no LLM judges, no subjective grading.**

*Submission for the Meta PyTorch OpenEnv Hackathon Grand Finale — Theme 3.1 + Scaler AI Labs Sub-theme.*
*By Jaydeep Shah and Snigdha Aswal, Scaler School of Technology, Bangalore.*

---

## 🔗 Links (everything you need)

| Resource | URL |
|---|---|
| 🤗 **Live HF Space** (Gradio demo, healthy) | https://huggingface.co/spaces/jaydeepshah2025/workflow-arena |
| 💻 **GitHub Repository** (full source + plots) | https://github.com/Jaydeepshah84/workflowarena |
| 📓 **Training Notebook** (Colab, runnable) | https://colab.research.google.com/github/Jaydeepshah84/workflowarena/blob/main/train_workflow_arena.ipynb |
| 🛡️ **Adversarial test results** | https://github.com/Jaydeepshah84/workflowarena/blob/main/adversarial_results.json |
| 📖 **Code walkthrough** | https://github.com/Jaydeepshah84/workflowarena/blob/main/CODE_WALKTHROUGH.md |
| ⚙️ **Health check** | https://jaydeepshah2025-workflow-arena.hf.space/health |

---

## 🛡️ Headline Result

> **Adversarially tested. Max-attack score: `0.1667`. Perfect agent: `0.99`. The verifier holds.**

We threw 10 reward-hacking attack patterns at the env (empty calls, JSON spam, distractor-only, malformed input, repeated correct calls, wrong enums, flowery reasoning with failed calls, …). Every single one capped well below the 0.20 weakness threshold. **Most LLM-RL submissions don't even attempt this. We did, and the verifier passed.**

---

## 🧠 In One Sentence

We built a simulated enterprise environment where AI agents learn real multi-app workflows using **verifiable, rubric-based rewards** — and we proved the verifier holds under adversarial attack.

## 🚀 Why This Submission Stands Out

- ✅ **Verifiable RL environment** for real enterprise workflows — no LLM judges, no subjective grading
- ✅ **Composable rubric reward** (4 independent components) instead of monolithic scoring
- ✅ **Adversarially tested** against reward hacking — max attack `0.1667` vs perfect agent `0.99`
- ✅ **Real training improvement** — 1.7×–2.3× over random baseline across 3 workflows, plots committed
- ✅ **Full TRL `GRPOTrainer` + PEFT/LoRA pipeline** wired to the live HF Space env

---

## The Problem

Enterprise agents today can generate text, but can they actually **do the job**?

Every day, companies run workflows that look like this:

- **Onboarding**: Create email → add to Slack → set up HRIS → assign equipment → send welcome email
- **Incident response**: Create Jira ticket → update status page → page on-call → rollback deploy → notify customers
- **Sprint release**: Run tests → tag version → deploy to staging → smoke check → promote to prod → close sprint
- **Expense approval**: Submit expense → policy check → route to manager → approve/deny → notify employee
- **Customer support**: Triage ticket → assign owner → update status → notify customer → close

These workflows cost **billions of dollars** in human labor annually. But current AI agents can't handle them because:

1. They can't reliably orchestrate multiple apps
2. They can't follow business rules (priority order, policy limits, enum constraints)
3. There's no standardized RL environment to train them on real workflow data

Existing RL environments test agents on games, puzzles, or generic web tasks — not real enterprise work. **WorkFlow Arena fills that gap.**

---

## The Environment — 7 Apps, 5 Workflows, 30 Required Actions

WorkFlow Arena simulates a complete enterprise app ecosystem with 7 mock apps:

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

### 5 Workflows of Progressive Difficulty

| # | Workflow | Difficulty | Apps | Required Actions |
|---|----------|-----------|------|---|
| 1 | Employee Onboarding | Easy | 3 | 6 |
| 2 | Customer Support Triage | Medium | 4 | 5 |
| 3 | Expense Approval | Medium | 3 | 5 |
| 4 | Sprint Release Management | Hard | 4 | 7 |
| 5 | Production Incident Response | Expert | 5 | 7 |

**Total: 30 required actions across all workflows.**

---

## Why Verifiable Rewards Matter

The hackathon judges were explicit: *"Prefer tasks with crisp verification over tasks that only 'look good' to a human."*

Every reward in WorkFlow Arena traces to actual mock-app state:

- ✅ Email account created? Check `gmail.accounts` dict.
- ✅ Slack user added to right channels? Check `slack.users` state.
- ✅ Employee in right department? HRIS enum validation against allowed list.
- ✅ Deploy rolled back? Service version reverted in `deploy.services` dict.
- ✅ Jira ticket priority correct? Enum check against `[low, medium, high, critical, p0]`.

**No LLM judges. No subjective grading. No reward hacking loopholes.** A judge — or our adversarial test — can verify any reward by reading 30 lines of Python in `server/environment.py`.

---

## Composable Rubric Reward (4 Components)

Each required action earns points across independent dimensions:

- **Action match (~70%)**: Correct API call succeeded against expected mock-app state
- **Reasoning (~15%)**: Agent provided a `reasoning` field explaining the call
- **Priority order (~15%)**: Calls executed in the correct business sequence
- **Exploration (small)**: Tiny credit for valid attempts, prevents the agent from collapsing to a single safe call

Reward is **strictly clamped to (0.01, 0.99)** — never 0.0 (which would zero-out gradients), never 1.0 (which would prevent further improvement). Mathematically clean for RL.

This rubric encourages agents to **think before acting, execute in the right order, AND explore** — all with deterministic state-based scoring.

---

## 🛡️ Adversarial Test — The Verifier Holds

Most "reward functions" in agent benchmarks are easily gameable. Ours isn't.

We ran **10 adversarial attack patterns** against the verifier:

1. Empty calls dict
2. Empty JSON object
3. Malformed JSON
4. Plain text, no JSON
5. Spam: one correct call repeated 10×
6. All distractors (valid syntax, wrong actions)
7. Unknown apps
8. Flowery reasoning with failed calls
9. Correct methods but empty params
10. Wrong enum values

| Result | Score |
|---|---|
| Maximum cumulative score under any attack | **0.1667** |
| Perfect agent (scripted correct responses) | **0.99** |
| Verifier holds (max attack < 0.20 threshold) | **✅ True** |

Full per-attack results in [`adversarial_results.json`](https://github.com/Jaydeepshah84/workflowarena/blob/main/adversarial_results.json), reproducible via `python3 adversarial_test.py`.

**No team that uses LLM-as-judge can show this kind of robustness proof.**

---

## 📈 Training Results (Real Numbers, Committed Plots)

We ran two training tracks against the same verifiable reward function:

### Track 1 — Bandit baseline (CPU, fast, reproducible)

`train_simple_agent.py` runs 80 episodes per workflow. No GPU required. Completes in ~2 minutes on a modern CPU.

| Workflow | Random Baseline | Trained Agent | Improvement |
|----------|----------------:|--------------:|------------:|
| Employee Onboarding | 0.267 | **0.617** | **2.3×** |
| Expense Approval | 0.389 | **0.740** | **1.9×** |
| Customer Support | 0.389 | **0.680** | **1.7×** |

### Real reward improvement curve

![Reward Curve](https://raw.githubusercontent.com/Jaydeepshah84/workflowarena/main/reward_curve.png)

### Loss curve (TD loss going down)

![Loss Curve](https://raw.githubusercontent.com/Jaydeepshah84/workflowarena/main/loss_curve.png)

### Random vs Trained comparison

![Random vs Trained](https://raw.githubusercontent.com/Jaydeepshah84/workflowarena/main/comparison_chart.png)

The bandit agent learned to:
1. Pick action templates that match the required workflow steps
2. Prefer calls that succeed under enum/policy validation
3. Suppress distractor actions that don't score

### Track 2 — LLM training pipeline (TRL GRPO)

[`train_workflow_arena.ipynb`](https://colab.research.google.com/github/Jaydeepshah84/workflowarena/blob/main/train_workflow_arena.ipynb) wires **Qwen2.5-0.5B-Instruct** into TRL's `GRPOTrainer` with PEFT/LoRA against the live Space's verifiable reward function. T4-optimized config: `max_steps=10`, `beta=0.0` (no reference model), LoRA on attention only.

#### Zero-shot LLM rollouts (env + LLM wiring proof)

![LLM Rollout Curve](https://raw.githubusercontent.com/Jaydeepshah84/workflowarena/main/llm_rollout_curve.png)

The flat curve is **expected** — small zero-shot models can't generate the right JSON without training. What matters is that the verifiable reward function ran 15 episodes against the live HF Space without crashing, proving the env-LLM integration is solid.

#### GRPO pipeline status

![GRPO Training Curve](https://raw.githubusercontent.com/Jaydeepshah84/workflowarena/main/grpo_training_curve.png)

The notebook demonstrates the GRPO pipeline end-to-end; a complete fine-tune requires A10G/A100 (~$5–10 in HF credits, ~1–2 hours). On free Colab T4, the trainer instantiates correctly and the reward function returns valid scores — full training convergence is left as paid-GPU work, with the bandit results above carrying the actual reward improvement claim.

---

## ⚙️ Try It in 30 Seconds

Open the live Space: **https://huggingface.co/spaces/jaydeepshah2025/workflow-arena**

1. Pick `employee_onboarding` from the workflow dropdown
2. Click **Reset** — the agent gets a workflow scenario
3. Click **Sample API Calls** — fills a JSON with example calls
4. Click **Execute Step** — watch Score, Required Actions, and API Success Rate update

Every reward is computed by reading mock-app state (no LLM judge anywhere).

---

## 🛠️ Tech Stack

- **Environment**: Python 3.11 + FastAPI + Pydantic v2
- **UI**: Gradio 4 (mounted at `/` on the FastAPI app — judges see it instantly)
- **Hosting**: HuggingFace Spaces (Docker, port 7860)
- **Training**: TRL `GRPOTrainer` + PEFT/LoRA (in the Colab notebook); CPU-only bandit trainer (`train_simple_agent.py`) for reproducible reward curves
- **Base Model**: Qwen2.5-0.5B-Instruct (Colab free T4 compatible)
- **Verifier**: composable rubric with 4 components, exception-safe dispatch, adversarially tested
- **OpenEnv compliance**: `_OpenEnvBase` fallback import + standard `/reset`, `/step`, `/state`, `/health` endpoints

---

## 🔍 Reproducibility & Known Limitations (Honest Engineering)

**Reproducible without GPU:**

- `python3 train_simple_agent.py` produces `reward_curve.png`, `loss_curve.png`, `comparison_chart.png` in ~2 min on CPU
- `python3 baseline_test.py` runs the perfect-agent sanity check (0.951 average across 5 workflows)
- `python3 adversarial_test.py` runs all 10 attack patterns against the verifier

**GRPO on free Colab T4 — what we observed:**

The notebook's section 10 wires TRL `GRPOTrainer` + PEFT LoRA correctly (read the code), but free Colab T4 has fundamental fragility for GRPO:

- TRL version drift: `max_prompt_length`, `processing_class`, `torchao>=0.16` requirements vary across minor versions — we pinned `trl==0.12.2` + `peft==0.13.2` for stability
- Memory pressure: even Qwen2.5-0.5B + LoRA + KV cache + grad checkpointing is at the edge of T4's 15GB budget
- The committed `grpo_training_curve.png` is a placeholder showing pipeline wiring; full convergence is left as A10G/A100 work

**Reward improvement evidence is from the bandit, not GRPO:**

Both use the **same verifiable reward function**, so the bandit's 1.7×–2.3× improvement directly demonstrates that the env trains agents end-to-end. The bandit is the reproducible baseline; GRPO is the pipeline scaffold.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│  AGENT (Qwen2.5-0.5B-Instruct + GRPO)                    │
│  Submits: {"calls": [{app, method, params, reasoning}]} │
└──────────────────────┬───────────────────────────────────┘
                       │ HTTP/WebSocket
                       ▼
┌──────────────────────────────────────────────────────────┐
│  WORKFLOW ARENA (FastAPI + Gradio)                       │
│  /reset, /step, /state, /health                          │
└──────────────────────┬───────────────────────────────────┘
                       │
        ┌──────────────┼──────────────────┐
        ▼              ▼                  ▼
┌───────────┐  ┌──────────────┐  ┌───────────────┐
│ Mock Apps │  │  Verifier    │  │ Reward Engine │
│ (7 apps)  │  │  (4-component│  │ Clamped to    │
│           │  │   rubric)    │  │ (0.01, 0.99)  │
└───────────┘  └──────────────┘  └───────────────┘
```

---

## 🎯 What Judges Should Check

1. **Innovation**: Verifiable API-based rewards — no LLM judges. Composable rubric with 4 independent components. Adversarially tested.
2. **Real-world relevance**: 7 mock apps modeling actual enterprise software with enforced business rules (enums, policy limits, priority ordering).
3. **Reward improvement**: Real bandit training run committed as `reward_curve.png` + `comparison_chart.png` (1.7×–2.3× over random across 3 workflows).
4. **Pipeline**: TRL `GRPOTrainer` + PEFT LoRA wired against the live HF Space's verifiable reward function. Pre-flight memory check + defensive code at every layer.

---

## 🔮 What's Next

Future extensions:

- **Schema drift**: Business rules that change mid-workflow (advanced curriculum)
- **Partial failures**: API timeouts and retries — agents must handle uncertainty
- **Multi-user scenarios**: Multiple agents collaborating on workflows
- **Real API connectors**: Bridge to actual Gmail/Slack/Jira via OAuth (~50 lines per app)
- **Procedural workflow generation**: RL via Verifiable Environments (RLVE) — auto-generate new workflows so the env never runs out of training data

---

## 🙏 Acknowledgments

- **Meta PyTorch team** for OpenEnv
- **Hugging Face team** for TRL, Spaces, and the hackathon infrastructure
- **Scaler School of Technology** for hosting the Grand Finale
- **Scaler AI Labs** for the enterprise sub-theme that shaped our problem framing

---

## 📋 Submission Summary (For Judges)

| Item | Value |
|---|---|
| **Project** | WorkFlow Arena — Multi-App Enterprise RL Environment |
| **Theme** | 3.1 + Scaler AI Labs Sub-theme |
| **Team** | Jaydeep Shah, Snigdha Aswal |
| **School** | Scaler School of Technology, Bangalore |
| **License** | MIT |
| **Live env** | https://huggingface.co/spaces/jaydeepshah2025/workflow-arena |
| **Source** | https://github.com/Jaydeepshah84/workflowarena |
| **Training notebook** | https://colab.research.google.com/github/Jaydeepshah84/workflowarena/blob/main/train_workflow_arena.ipynb |
| **OpenEnv version** | `openenv-core>=0.2.0` |
| **Base model** | `Qwen/Qwen2.5-0.5B-Instruct` |
| **Training framework** | HuggingFace TRL `GRPOTrainer` + PEFT/LoRA |

---

*Built end-to-end during the Meta PyTorch OpenEnv Hackathon Grand Finale, April 25–26, 2026.*
