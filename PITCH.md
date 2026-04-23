# WorkFlow Arena — 3-Minute Pitch Script

**Team**: Jaydeep Shah + Snigdha Aswal
**Theme**: 3.1 + Scaler AI Labs (Multi-App Enterprise Workflow)

---

## 🎬 Slide 1 — The Hook (30 seconds)

*[Show a chaotic screenshot: Slack, Jira, Gmail tabs all open]*

> **"Every day, enterprises run workflows that cost billions in human labor.
> Onboarding. Incidents. Releases. These require orchestrating Gmail, Slack, Jira,
> HRIS, and more — with the right sequence, the right business rules, and zero
> mistakes.**
>
> **Current AI agents fail at this because there's no good way to train them.
> Existing RL environments test games, puzzles, and code — not real work.**
>
> **We built WorkFlow Arena to fix that."**

---

## 🎬 Slide 2 — The Environment (45 seconds)

*[Show the Gradio UI live]*

> **"WorkFlow Arena is a multi-app enterprise RL environment with 7 simulated apps:
> Gmail, Slack, Jira, HRIS, CRM, Deploy, and Finance.**
>
> **Agents execute API calls to complete real business workflows:
> onboarding new hires, resolving P0 incidents, managing releases.**
>
> **Here's what's different: every reward is VERIFIABLE.
> API call succeeds? Check the state. Policy limit followed? Check the enum.
> Priority order correct? Check the sequence. No LLM judges. No subjective grading.**
>
> *[Click through a workflow — show the agent making API calls]*
>
> **This is exactly what Scaler AI Labs asked for in their sub-theme:
> complex enterprise workflows with business rule nuances."**

---

## 🎬 Slide 3 — The Workflows (30 seconds)

*[Show the 5 workflows table]*

> **"Five workflows of progressive difficulty:**
>
> - **Easy**: Employee onboarding — 6 actions across 3 apps
> - **Medium**: Customer support triage, expense approval
> - **Hard**: Sprint release management
> - **Expert**: P0 production incident response — 7 actions, time-critical
>
> **30 total required actions. Every one is verified by a real API response."**

---

## 🎬 Slide 4 — The Results (45 seconds)

*[Show the reward curve chart from the notebook]*

> **"We ran a real training loop against the environment and committed the plots to the repo.**
>
> **Random baseline:
> - Employee onboarding: 0.267 reward
> - Expense approval: 0.389 reward
> - Customer support: 0.389 reward**
>
> **After 80 episodes of bandit training:
> - Employee onboarding: 0.617 reward — 2.3x improvement
> - Expense approval: 0.740 reward — 1.9x improvement
> - Customer support: 0.680 reward — 1.7x improvement**
>
> **The agent learned to respect business rules: correct department enums,
> proper priority order, sequential API dependencies.**
>
> *[Point at reward curve going up]*
>
> **This is what Meta's own training pipelines need: real enterprise work,
> real API responses, real improvement."**

---

## 🎬 Slide 5 — The Close (30 seconds)

*[Show the architecture diagram: apps → environment → agent → reward]*

> **"WorkFlow Arena demonstrates Scaler AI Labs' vision:
> RL environments that capture business rule nuances in complex enterprise workflows.**
>
> **It's live on HuggingFace Spaces. OpenEnv compliant. Open source.**
>
> **We believe this is what enterprise AI training actually needs.**
>
> **Thank you."**

---

## 📊 Key Numbers to Remember

- **7** simulated enterprise apps (Gmail, Slack, Jira, HRIS, CRM, Deploy, Finance)
- **5** workflows (easy → expert)
- **30** total required actions
- **100%** verifiable rewards (no LLM judges)
- **80** episodes trained (bandit) + Colab GRPO rollouts (Qwen3-1.7B)
- **2.3×** reward improvement on onboarding (0.267 → 0.617)
- **1.9×** reward improvement on expenses (0.389 → 0.740)
- **1.7×** reward improvement on customer support (0.389 → 0.680)
- **~2 min** for local bandit training (CPU); **~15–20 min** for Colab T4 LLM
- Plots committed: `reward_curve.png`, `loss_curve.png`, `comparison_chart.png`

## ❓ Expected Q&A (2 minutes)

**Q: "How is this different from browser-use or AgentBench?"**
A: Those test agents on generic web tasks. WorkFlow Arena simulates REAL enterprise apps with business rule enforcement (policy limits, priority order, department configs). The rewards come from actual API state changes, not page content.

**Q: "Why verifiable rewards over LLM judges?"**
A: The hackathon FAQ explicitly said to avoid LLM judges. They're gameable, expensive, and subjective. Our rewards come from deterministic API responses — if Gmail's `create_account` returns `success: true`, that's a fact, not an opinion.

**Q: "Can this extend to real APIs?"**
A: Yes. The mock apps implement the same interface real APIs would. Swapping in Gmail's actual API is ~50 lines of code. We designed it this way for reproducibility during training.

**Q: "What's the hardest workflow?"**
A: Incident Response. 7 required actions across 5 apps with time pressure and rollback logic. Even our perfect scripted agent scores 0.79 due to one edge case — proves the environment has genuine difficulty.

**Q: "How long did this take?"**
A: Environment: 6 hours. Workflows + verification: 4 hours. Training notebook: 2 hours. Total: ~12 hours in the finale sprint.

**Q: "Why Scaler AI Labs sub-theme specifically?"**
A: Their brief asked for "complex workflows, business rule nuances, large enterprise" — WorkFlow Arena delivers exactly that. Plus, Scaler's engineers will recognize real enterprise patterns.

---

## 🎥 Demo Plan (60 seconds max on stage)

1. **Open HF Space URL** — shows Gradio UI instantly (no loading)
2. **Select "Employee Onboarding"** from dropdown → hit Reset
3. **Click "Sample Action"** button → shows the agent's API call JSON
4. **Click "Execute Step"** → shows rewards, completed actions counter
5. **Switch to "Incident Response"** → show the harder P0 scenario
6. **Point to the reward history panel** → visual proof of verifiable rewards

---

## 🎯 Judging Criteria Coverage

| Criterion | Weight | What Wins Points |
|-----------|--------|------------------|
| Environment Innovation | 40% | Verifiable rewards, 7 apps, 5 workflows, business rules |
| Storytelling | 30% | This pitch script + Live Gradio demo |
| Reward Improvement | 20% | Reward curve from trained notebook |
| Pipeline | 10% | GRPO + Unsloth + TRL + OpenEnv |

---

## 📝 Submission URLs

- **GitHub**: https://github.com/Jaydeepshah84/workflowarena
- **HuggingFace Space**: https://huggingface.co/spaces/jaydeepshah2025/workflow-arena
- **Colab Notebook**: Open `train_workflow_arena.ipynb` via GitHub link
- **Blog**: `BLOG.md` in the repo
