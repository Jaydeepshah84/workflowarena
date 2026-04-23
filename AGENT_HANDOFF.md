# WorkFlow Arena - Agent Handoff Document

**Purpose**: This is a complete project memory for any AI agent that picks up work on this repo. Read this top-to-bottom before touching anything.

**Last updated**: 2026-04-23 by Jaydeep Shah
**Status**: Hackathon-ready. Pitch day is 2026-04-26 in Bangalore. 3 days remaining.

---

## 1. TL;DR (30 seconds)

- This is a Meta PyTorch **OpenEnv Hackathon Grand Finale** submission (Theme 3.1 + Scaler AI Labs sub-theme).
- It is an **RL environment** — not an agent, not a model. Agents train *against* it.
- 7 simulated enterprise apps (Gmail, Slack, Jira, HRIS, CRM, Deploy, Finance) + 5 progressive-difficulty workflows. Rewards come from actual API response state — no LLM judges.
- Already deployed, healthy, and submitted. Remaining work is **pitch practice**, not code.
- Team: Jaydeep Shah (owner, main dev) + Snigdha Aswal (co-presenter).

**Do not rewrite, refactor, or "clean up" this project.** It works. Judges are about to review it. Make the smallest possible changes needed.

---

## 2. Project status and URLs

| Thing | URL / Value |
|---|---|
| GitHub (public, `main` is default) | https://github.com/Jaydeepshah84/workflowarena |
| HF Space (live, healthy) | https://huggingface.co/spaces/jaydeepshah2025/workflow-arena |
| Colab notebook | https://colab.research.google.com/github/Jaydeepshah84/workflowarena/blob/main/train_workflow_arena.ipynb |
| Latest commit on main + master | `63dcc9b` |
| HF Space health | `GET /health` returns `{"status":"healthy"}` |
| Hackathon event | 2026-04-26, Scaler School of Technology, Bangalore |

**GitHub has two branches (main + master) kept in lockstep.** When you push, push to both:

```bash
git push origin master
git push origin master:main
```

The `hf` remote points at the Space — **do not push to it casually**; it triggers a rebuild. Only push if you deliberately want to redeploy.

---

## 3. What this project is (domain, not tech)

### The hackathon brief
"Build an OpenEnv RL environment with verifiable rewards. Train a small LLM against it. Show that reward goes up."

### Our take
Enterprises run multi-app workflows every day — onboarding, incidents, expense approval, release management. Current AI agents can't orchestrate Gmail + Slack + Jira + HRIS in the right order with the right business rules. Existing RL environments test games and puzzles, not real work.

We built a realistic enterprise-app simulator where:
1. The agent's job is to execute API calls in the correct sequence to complete a business workflow
2. Every reward comes from **actual API response success** — no LLM-as-judge
3. Business rules (enum validation, policy limits, priority ordering) are enforced

### The 5 workflows (progressive difficulty)
1. **Employee Onboarding** (Easy, 6 required actions)
2. **Customer Support Triage** (Medium, 5)
3. **Expense Approval** (Medium, 5)
4. **Sprint Release** (Hard, 7)
5. **P0 Incident Response** (Expert, 7)

### The reward function
- 70% for each correct API call that matches a required action
- 15% bonus for providing reasoning
- 15% bonus for correct priority order
- 0% (no penalty) for failed API calls — encourages exploration
- Rewards clamped strictly to (0.01, 0.99) — never 0.0 or 1.0

---

## 4. Architecture

```
Agent (any LLM)
   |
   | HTTP (POST /reset, POST /step, GET /state)
   v
FastAPI server (server/app.py)
   |
   | In-process function calls
   v
WorkFlowEnvironment (server/environment.py)
   |
   | Routes agent's "calls" to the right mock app
   v
EnterpriseApps (mock_apps.py)  --- 7 apps: gmail, slack, jira, hris, crm, deploy, finance
```

**Key design choices** (do not change these):
- FastAPI exposes 3 core endpoints matching the OpenEnv HTTP spec: `/reset`, `/step`, `/state`. These names are the standard — not reserved.
- Gradio UI is **mounted at `/`** via `gr.mount_gradio_app(api_app, gradio_demo, path="/")` so the HF Space root shows the UI.
- Sessions live in an in-process dict. Uvicorn runs with **1 worker** (not 4) so sessions survive across requests.
- Dockerfile base image is pinned to **AWS ECR mirror** of python:3.11-slim, not Docker Hub, to avoid manifest errors.

---

## 5. File-by-file map

```
workflowarena/
|
|-- server/                        SERVER-SIDE ONLY
|   |-- __init__.py
|   |-- app.py                     FastAPI + Gradio mount
|   |-- environment.py             Core env logic (reset/step/state)
|   \-- Dockerfile                 (copy of root Dockerfile for HF)
|
|-- mock_apps.py                   7 mock enterprise apps + business rules
|-- workflows.py                   5 workflow definitions with required_actions
|-- models.py                      Pydantic types (Action/Observation/State/APICall)
|-- ui.py                          Gradio UI (imported by server/app.py)
|-- client.py                      Thin HTTP client (for tests, not the server)
|
|-- inference.py                   Baseline OpenAI-compatible inference + logs
|-- baseline_test.py               Scripted "perfect agent" ~0.95 score validation
|-- demo_script.py                 Random vs perfect comparison
|-- train_simple_agent.py          LOCAL bandit trainer - produces committed PNGs
|-- train_workflow_arena.ipynb     Colab notebook (Qwen3-1.7B zero-shot rollouts)
|
|-- reward_curve.png               Real reward curve from train_simple_agent.py
|-- loss_curve.png                 Real TD loss curve
|-- comparison_chart.png           Random vs trained bar chart
|-- training_results.json          Raw per-episode numbers
|
|-- openenv.yaml                   OpenEnv metadata (tasks, interface, endpoints)
|-- pyproject.toml                 Package definition
|-- requirements.txt               Runtime + training deps
|-- uv.lock                        Locked versions
|-- Dockerfile                     Root Dockerfile (used by HF Space)
|
|-- README.md                      Main docs with embedded plots
|-- BLOG.md                        Mini-blog for HF submission
|-- PITCH.md                       3-minute pitch script + Q&A prep
|-- SUBMISSION.md                  Submission checklist
\-- AGENT_HANDOFF.md               THIS FILE
```

### Critical files (read before editing)
1. `server/environment.py` - reward logic, action matching, state tracking
2. `workflows.py` - the 5 workflow specs; `required_actions` drives grading
3. `mock_apps.py` - business rule enforcement (enums, policy limits)
4. `server/app.py` - HTTP routes; make sure uvicorn workers stays at 1

### Files you can generally ignore
- `uv.lock` (auto-managed)
- `__pycache__/` (gitignored)
- The `.png` + `.json` training outputs (regenerate via `train_simple_agent.py`)

---

## 6. Tools, frameworks, APIs used

| Layer | Choice | Version |
|---|---|---|
| Server | FastAPI | >=0.104 |
| Server runtime | Uvicorn | >=0.24 |
| Validation | Pydantic | v2 |
| UI | Gradio | 4.x |
| HTTP client | httpx | >=0.25 |
| LLM client | OpenAI SDK | >=1.0 (for inference.py) |
| OpenEnv spec | openenv-core | >=0.2.0 |
| Plotting | matplotlib + numpy | >=3.7 / >=1.24 |
| Training (Colab) | transformers, torch (Qwen3-1.7B) | latest |
| Tracking | trackio | optional |
| Container | Docker | python:3.11-slim (pinned to AWS ECR mirror) |
| Hosting | HuggingFace Spaces | SDK: docker |

**We deliberately avoided**:
- TRL's experimental OpenEnv integration (module not on PyPI at time of build)
- LLM-as-judge reward functions (hackathon explicitly prefers verifiable)
- Unsloth/vLLM in the committed notebook (would add GPU-only deps for Colab)

---

## 7. Setup on MacBook (fresh clone)

```bash
# 1. Clone
git clone https://github.com/Jaydeepshah84/workflowarena.git
cd workflowarena

# 2. Python 3.11 recommended
python3 --version   # 3.11 or 3.13 both work

# 3. Virtualenv
python3 -m venv .venv
source .venv/bin/activate

# 4. Install
pip install -r requirements.txt

# 5. Run the server locally
uvicorn server.app:app --host 0.0.0.0 --port 7860

# 6. Open the UI
open http://localhost:7860
```

**macOS-specific notes**:
- Use `python3`, not `py` (py is a Windows launcher). The scripts in this repo call `py`; on Mac you run them as `python3 train_simple_agent.py` instead.
- If port 7860 is taken, change it: `uvicorn server.app:app --port 8080`.
- Docker Desktop is only needed if you want to rebuild the container locally. The HF Space handles this in the cloud.

### Running the training script (produces committed PNGs)
```bash
python3 train_simple_agent.py
# ~2 min on CPU. Regenerates reward_curve.png, loss_curve.png, comparison_chart.png, training_results.json
```

### Running the baseline test
```bash
python3 baseline_test.py
# Hits the live HF Space. Expected: ~0.95 average score.
```

---

## 8. Coding standards and best practices (for this repo)

1. **Reward must be strictly in (0, 1)** — never 0.0, never 1.0. The env clamps to `[0.01, 0.99]`. If you add new reward logic, preserve this.
2. **No LLM judges, ever.** Every reward must trace to an actual mock-app state change.
3. **No Unicode box-drawing or em-dashes in Python files** — Windows `cp1252` stdout chokes on them. Use ASCII `---` and `-`.
4. **Environment variable contract** (organizer requirement, do not change):
   - `API_BASE_URL` - no default, must be set by user
   - `API_KEY` - no default, must be set (NOT `HF_TOKEN`, NOT `OPENAI_API_KEY`)
   - `MODEL_NAME` - default OK
5. **Log format** (organizer requirement, inference.py enforces this):
   ```
   [START] task=<name> env=workflow-arena model=<model>
   [STEP] step=<n> action=<str> reward=<0.00> done=<true|false> error=<msg|null>
   [END] success=<true|false> steps=<n> score=<0.00> rewards=<r1,r2,...>
   ```
   The `score=` field in `[END]` is **non-negotiable** — organizer flagged it specifically.
6. **Keep Gradio mounted at `/`.** If you accidentally move it to `/ui`, judges see a blank HF Space.
7. **Keep uvicorn workers at 1.** Sessions are in-process; multiple workers = session loss.
8. **When adding required_actions to a workflow**, always include `id`, `app`, `method`, `priority`, and `params`. The grader depends on these.
9. **Commit plots when training evidence changes.** Judges explicitly require plots in the repo, not just in Colab.

---

## 9. Common mistakes to avoid (learned the hard way during this build)

1. **Do not change the OpenEnv HTTP endpoint names.** `/reset`, `/step`, `/state` are the spec. "Reserved tool names" applies to MCP tools, not HTTP.
2. **Do not use the public Docker Hub base image directly.** HF had intermittent manifest errors. Keep `FROM public.ecr.aws/docker/library/python:3.11-slim`.
3. **Do not reset score cumulative to 0 when step reward hits the clamp.** The cumulative can saturate at 0.99 and must also be clamped there.
4. **Do not accept `trl.experimental.openenv` as a Colab dependency.** It's not on PyPI. The current notebook uses plain `transformers.generate()`.
5. **Do not set `workers=4` on uvicorn.** Broke session persistence on HF Space.
6. **Do not remove the few-shot example from the system prompt in the notebook.** Qwen3-1.7B produces invalid JSON without it → flat reward line at 0.03.
7. **Do not commit `.env` or anything with credentials.** `.gitignore` protects `.env` but be careful.
8. **Do not create a new git repo or reset history.** The public repo `Jaydeepshah84/workflowarena` is already linked in the submission form.
9. **Do not push to the `hf` remote unless you want to trigger a Space rebuild.** Current Space is stable; a rebuild risks breaking it before pitch day.
10. **Do not remove or rename committed PNGs.** README embeds them via relative path; broken images = judge deducts points.
11. **Do not "refactor" `WorkFlowEnvironment` to remove the `_OpenEnvBase` fallback.** It imports the OpenEnv base class if present, falls back to a shim otherwise — this satisfies the new judging criterion.

---

## 10. Execution steps - full flow

### Local dev (happy path)
```bash
source .venv/bin/activate
uvicorn server.app:app --host 0.0.0.0 --port 7860
# in another terminal:
python3 baseline_test.py   # expect ~0.95 avg score
```

### Generate training plots
```bash
python3 train_simple_agent.py
# reward_curve.png / loss_curve.png / comparison_chart.png / training_results.json
```

### Run on Colab (GPU)
1. Open https://colab.research.google.com/github/Jaydeepshah84/workflowarena/blob/main/train_workflow_arena.ipynb
2. Runtime -> Change runtime type -> T4 GPU
3. Run cells top to bottom (~15-20 min)
4. Downloads `llm_rollout_curve.png`

### Baseline OpenAI-compatible inference
```bash
export API_BASE_URL="https://api.openai.com/v1"
export API_KEY="sk-..."
export MODEL_NAME="gpt-4o-mini"
python3 inference.py
# Produces the [START]/[STEP]/[END] log format required by organizer
```

---

## 11. Deployment

**Current state: already deployed, do not touch.**

- Host: HuggingFace Spaces
- Deploy method: Docker SDK (`Dockerfile` at repo root)
- Space repo: separate from GitHub; pushed via `hf` git remote
- Health: `GET /health` -> `{"status":"healthy"}`
- Port: 7860
- Public URL: https://jaydeepshah2025-workflow-arena.hf.space

If you genuinely need to redeploy:
```bash
git push hf master:main
# wait ~3 min for Space rebuild; check the Logs tab on HF
```

If the Space fails to rebuild, **the backup plan for pitch day** is documented in `SUBMISSION.md`:
```bash
uvicorn server.app:app --host 0.0.0.0 --port 7860
```
Run locally on the laptop at the venue.

---

## 12. Debugging and troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| HF Space shows 500 on `/health` | Docker build failed | Check Space Logs; usually pip install timed out. Re-push. |
| HF Space shows blank page at root | Gradio mount path wrong | Verify `gr.mount_gradio_app(api_app, gradio_demo, path="/")` in server/app.py |
| `/step` returns 404 "Session not found" | Multiple workers | Check uvicorn startup command; force `--workers 1` |
| Colab notebook reward curve is flat at 0.03 | Qwen3-1.7B producing invalid JSON | Keep the few-shot example in SYSTEM_PROMPT; keep `extract_json()` in generate() |
| `baseline_test.py` shows 0.0 scores | Env URL wrong OR Space down | Curl `/health` first; swap `ENV_URL` to `http://localhost:7860` for local |
| `UnicodeDecodeError` on Windows | Em-dashes/box-drawing in Python file | Replace with ASCII `-` and `--` |
| Docker build fails with manifest error | Docker Hub outage | Confirm `FROM public.ecr.aws/docker/library/python:3.11-slim` (not `python:3.11-slim`) |
| `openenv validate` fails | openenv.yaml mismatch with models.py | Verify Pydantic model field names match the yaml `fields:` block |
| Phase 2 submission rejected with "score out of range" | Missing `score=` in [END] or API_BASE_URL has default | Check inference.py; env var must not have default |

---

## 13. Assumptions, constraints, important notes

- **Judging criteria weighting** (last known as of 2026-04-23):
  - Environment Innovation: 40%
  - Storytelling: 30%
  - Showing Reward Improvement: 20%
  - Reward + Training Script quality: 10%
- **New hard requirements** (from the 2026-04-23 criteria update):
  - Loss and reward plots from a real training run must be committed to the repo (done - `reward_curve.png`, `loss_curve.png`)
  - Trained vs random baseline comparison must be shown quantitatively (done - `comparison_chart.png` + README table)
  - Plot axes must be labeled with units (done)
- **Assumption**: The perfect-agent baseline (`baseline_test.py`) will score ~0.95 average. If it starts scoring <0.9, something broke in the reward function or required_actions list.
- **Assumption**: The Space stays up until 2026-04-27. If HF has an outage, fall back to local uvicorn.
- **Constraint**: Qwen3-1.7B on Colab free T4 is the ceiling. Do not attempt to load a 7B+ model - it will OOM.
- **Constraint**: The git user is `jaydeep`. Do not change git config.
- **Out of scope for this hackathon**:
  - Real API integrations (Gmail/Slack actual endpoints)
  - Full GRPO training with Unsloth in the notebook (too fragile for free T4)
  - Schema evolution / drift handling
  - Multi-agent collaboration

---

## 14. What is DONE (as of handoff)

- [x] Environment with 5 workflows
- [x] 7 mock enterprise apps with business rules
- [x] Verifiable rewards via API state (no LLM judges)
- [x] FastAPI server + Gradio UI
- [x] Dockerfile (AWS ECR mirror base)
- [x] HF Space deployed, healthy
- [x] openenv.yaml with correct schema
- [x] baseline_test.py (scripted perfect agent, ~0.95 avg)
- [x] demo_script.py (random vs perfect comparison)
- [x] train_simple_agent.py (real 80-episode bandit trainer)
- [x] Committed plots: reward_curve.png, loss_curve.png, comparison_chart.png
- [x] training_results.json with real per-episode numbers
- [x] train_workflow_arena.ipynb (Colab notebook with few-shot + robust JSON)
- [x] README.md with embedded plots + real numbers
- [x] BLOG.md
- [x] PITCH.md with 3-min script + Q&A prep
- [x] SUBMISSION.md checklist
- [x] Inference log format with required `score=` field in [END]
- [x] GitHub `main` and `master` both pushed to `63dcc9b`
- [x] HF Space health verified

## 15. What is NOT done (remaining work)

- [ ] Pitch rehearsal with Snigdha (practice 3-min timing)
- [ ] Optional: re-run Colab notebook to generate `llm_rollout_curve.png` with non-flat data (nice-to-have, not required)
- [ ] Confirm hackathon submission portal has correct URLs
- [ ] Travel to Bangalore on 2026-04-25
- [ ] Venue Wi-Fi check on 2026-04-25 PM
- [ ] Pitch on 2026-04-26

**No new code is expected.** If a future agent is asked to "improve the project," push back and ask what specific criterion is unmet - over-engineering 3 days before the deadline is the biggest risk now.

---

## 16. If you must make changes

1. Read this file fully.
2. Read the specific file you're touching (especially `server/environment.py` if the change is about rewards).
3. Run `python3 baseline_test.py` locally before and after - the score must stay at ~0.95.
4. Run `python3 train_simple_agent.py` and commit the regenerated PNGs if the reward function changed.
5. Commit with a message that states the criterion motivating the change.
6. Push to BOTH `master` and `main`:
   ```bash
   git push origin master && git push origin master:main
   ```
7. Do NOT push to `hf` unless the user explicitly asks.

---

## 17. Contact / ownership

- Primary: Jaydeep Shah (sandeepshah103@gmail.com)
- Co-presenter: Snigdha Aswal
- Organization: Scaler School of Technology, Bangalore
- Repo owner on GitHub: `Jaydeepshah84`
- HF Space owner: `jaydeepshah2025`

---

**End of handoff. If anything in the running state contradicts this document, trust the running state and update this file.**
