# Submission Checklist — WorkFlow Arena

**Team**: Jaydeep Shah + Snigdha Aswal
**Theme**: 3.1 + Scaler AI Labs Sub-theme

---

## ✅ Minimum Requirements (MUST HAVE)

| Requirement | Status | Location |
|-------------|--------|----------|
| Uses OpenEnv (latest) | ✅ | `pyproject.toml`, `openenv.yaml` |
| Training script (Colab, TRL/Unsloth) | ✅ | `train_workflow_arena.ipynb` |
| Mini-blog on HuggingFace (<2 min read) | ✅ | `BLOG.md` |
| OpenEnv environment on HF Spaces | ✅ | [Space URL](https://huggingface.co/spaces/jaydeepshah2025/workflow-arena) |

## ✅ Functional Requirements

| Requirement | Status |
|-------------|--------|
| Real-world task (not game/toy) | ✅ Enterprise workflows |
| OpenEnv spec: typed models | ✅ Pydantic models |
| step(action) → observation, reward, done, info | ✅ |
| reset() → initial observation | ✅ |
| state() → current state | ✅ |
| openenv.yaml metadata | ✅ |
| openenv validate passes | ✅ |
| Min 3 tasks, easy→hard | ✅ 5 workflows |
| Deterministic graders, 0.0–1.0 | ✅ API response verification |
| Meaningful reward function | ✅ Multi-component (action + reasoning + priority) |
| Baseline inference script | ✅ `inference.py` |
| OpenAI client for LLM calls | ✅ |
| API_BASE_URL + MODEL_NAME defaults | ✅ |
| API_KEY required (no default) | ✅ |

## ✅ Non-Functional Requirements

| Requirement | Status |
|-------------|--------|
| HF Space deployable | ✅ |
| `openenv` tag on Space | ✅ |
| Dockerfile works | ✅ Root + server/Dockerfile |
| README with description, spaces, setup, baselines | ✅ |

## ✅ Log Format

Every inference run produces:
```
[START] task=<name> env=workflow-arena model=<model>
[STEP] step=<n> action=<str> reward=<0.00> done=<true|false> error=<msg|null>
[END] success=<true|false> steps=<n> score=<0.00> rewards=<r1,r2,...>
```

---

## 📎 Submission URLs

**Paste these into the hackathon submission form:**

- **GitHub**: https://github.com/Jaydeepshah84/workflowarena
- **HF Space**: https://huggingface.co/spaces/jaydeepshah2025/workflow-arena
- **Training Notebook**: https://colab.research.google.com/github/Jaydeepshah84/workflowarena/blob/main/train_workflow_arena.ipynb
- **Blog**: https://github.com/Jaydeepshah84/workflowarena/blob/main/BLOG.md

---

## 🏆 Scoring Preparation

### Environment Innovation (40%)
**Talking points:**
- 7 simulated enterprise apps (Gmail, Slack, Jira, HRIS, CRM, Deploy, Finance)
- 100% verifiable rewards via API response state
- Business rule enforcement (enums, policy limits, priority order)
- Multi-step orchestration (5–7 actions per workflow)
- 30 total required actions across 5 difficulty levels

### Storytelling (30%)
**Tools:**
- Live Gradio UI demo at HF Space root
- Mentor-round talking points reference (`PITCH.md`)
- Mini-blog with problem / solution / results (`BLOG.md`)
- README walkthrough with embedded plots (judges read it cold in 3-5 minutes)

### Showing Improvement in Rewards (20%)
**Evidence (real numbers from `training_results.json`):**

| Workflow | Random Baseline | Trained Bandit | Improvement |
|----------|----------------:|---------------:|------------:|
| Employee Onboarding | 0.267 | 0.617 | **2.3×** |
| Expense Approval | 0.389 | 0.740 | **1.9×** |
| Customer Support | 0.389 | 0.680 | **1.7×** |

Plots committed: [reward_curve.png](reward_curve.png), [loss_curve.png](loss_curve.png), [comparison_chart.png](comparison_chart.png). Per-step `info["reward_components"]` exposes the rubric breakdown so trainers can monitor individual columns.

### Reward and Training Script (10%)
**Pipeline:**
- TRL `GRPOTrainer` with PEFT/LoRA, wired to the live HF Space as the reward function (notebook section 10 — proof-of-life run on Colab T4 with `max_steps=2`)
- Local CPU bandit trainer (`train_simple_agent.py`) for reproducible reward curves
- Composable rubric (`REWARD_RUBRIC` in `server/environment.py`): action_match, reasoning, priority_order, exploration
- Adversarial test (`adversarial_test.py`): 10 attack patterns, max attack scores 0.1667 vs perfect-agent 0.99 → verifier holds

---

## 🔄 Pre-Submission + Pre-Mentor-Round Sanity Checks

Before each Mentor Round, and before the 5 PM submission cutoff on 2026-04-26:

- [ ] HF Space stage = `RUNNING` (`curl https://huggingface.co/api/spaces/jaydeepshah2025/workflow-arena | grep stage`)
- [ ] `curl https://jaydeepshah2025-workflow-arena.hf.space/health` returns `{"status":"healthy"}`
- [ ] Gradio UI loads in browser at root URL
- [ ] `python3 baseline_test.py` runs and shows ~0.95 average score across all 5 workflows
- [ ] `python3 adversarial_test.py` shows verifier holds (max attack < 0.20)
- [ ] All committed PNGs render in README on github.com (no broken images)
- [ ] Colab badge in README launches `train_workflow_arena.ipynb` from `main`
- [ ] Submission form fields match the URLs in section "📎 Submission URLs" above

---

## 🎯 Demo flow (use during mentor rounds, ~60 seconds)

1. Open HF Space → Gradio UI loads instantly
2. Select **"P0 Incident Response"** from dropdown (the most impressive workflow)
3. Click **"Sample API Calls"** → shows pre-filled JSON
4. Click **"Execute Step"** → rewards appear, counters update
5. Point at "API Calls: 3/4 successful" + the per-component reward breakdown → verifiable, no LLM judge
6. Switch tab to README on GitHub → show the embedded `reward_curve.png` and the random-vs-trained comparison table

---

## 📞 If Something Fails At The Venue

### HF Space down?
Run locally:
```bash
cd workflowarena
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

### Colab notebook errors?
Fall back to showing:
- `baseline_test.py` output (proves env works against the live Space)
- Committed `reward_curve.png` + `comparison_chart.png` (training already happened, plots are in the repo)
- `adversarial_results.json` (anti-reward-hacking evidence)

### Laptop dies?
Mentor talking points are in `PITCH.md`. Key numbers:
- 7 apps, 5 workflows, 30 required actions across difficulty tiers
- 100% verifiable rewards (no LLM judge)
- Trained-bandit improvement: 1.7×–2.3× over random across 3 workflows
- Adversarial verifier: max-attack 0.17 vs perfect-agent 0.99

---

## 🗓️ Event Schedule (2026-04-25 → 2026-04-26)

| When | What |
|------|------|
| Day 1, 2026-04-25 7:00 AM | Registration desk opens at Scaler Campus, Electronic City |
| Day 1, 10:00 AM | Welcome |
| Day 1, 11:00 AM | Hacking opens |
| Day 1, **3:30–4:30 PM** | **Mentor Round 1** (classroom) |
| Day 1, **8:00–10:00 PM** | **Mentor Round 2** (classroom) |
| Day 2, 2026-04-26 **10:00 AM–12:00 PM** | **Mentor Round 3** (final, classroom) |
| Day 2, **5:00 PM SHARP** | **Submission form closes — hard stop, no late entries** |
| Day 2, 5:15 PM | Closing remarks |
| 2026-05-02 | Results announced via YouTube Live |

---

**Good luck! 🚀**
