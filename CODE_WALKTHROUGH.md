# Code Walkthrough for Reviewers

**Audience**: hackathon judges or anyone reviewing this repo for technical depth.
**Time budget**: 5 minutes.

This document points you at the files and specific lines where the interesting engineering lives, so you don't have to grep.

---

## 1. Verifiable reward — the core claim

**File**: [server/environment.py](server/environment.py)

Every reward component is a deterministic check. No LLM-as-judge, no regex, no subjective scoring.

**Lines 294-307** — the entire reward computation:

```python
if result.get("success"):
    self.api_calls_successful += 1
    matched_id = self._match_required_action(call, result)
    if matched_id:
        self.completed_actions.add(matched_id)
        action_reward = points_per_action * 0.7       # 70% for correct API call
        if call.reasoning.strip():
            action_reward += points_per_action * 0.15  # 15% for non-empty reasoning
        expected_priority = self.workflow["required_actions"][action_idx]["priority"]
        if len(self.completed_actions) == expected_priority:
            action_reward += points_per_action * 0.15  # 15% for correct sequence position
```

**Every reward traces to**:
- A `result["success"]` bool from the mock app
- A `call.reasoning.strip() != ""` non-empty check
- An integer comparison `len(completed_actions) == expected_priority`

**Zero ambiguity.** A judge can read this once and verify it.

---

## 2. Business rule enforcement — the mock apps

**File**: [mock_apps.py](mock_apps.py)

Check these methods for how business rules are enforced:

- `gmail_create_account` — rejects duplicate emails (state-based)
- `hris_create_employee` — validates `dept` against an enum: `engineering/sales/marketing/hr/finance/support/operations`. Invalid department → API returns `success: false` → agent gets no reward
- `finance_submit_expense` — enforces policy limits ($100 meals, $1000 travel, $2000 equipment, $5000 training). Over-limit → auto-rejected
- `jira_create_ticket` — validates `priority` against enum: `low/medium/high/critical/p0`
- `deploy_rollback` — requires deployment history; can't rollback what was never deployed (proves stateful dependencies)

Business rules are enforced in the mock app layer, not in the reward function. This means the agent learns rules by getting API failures — the same way a real enterprise agent would learn.

---

## 3. Required action matching — not just "API succeeded"

**File**: [server/environment.py](server/environment.py#L222-L257)

Method `_match_required_action` is where the grader gets picky. It's not enough for an API call to succeed — it has to:

1. Match the exact `app` and `method` of a required action (with method alias tolerance)
2. Match all required parameters (with `_contains` suffix support for substring checks)
3. Not already be in the `completed_actions` set (can't double-count)

This is why you can see `API Success Rate: 8/9` but `Required Actions: 2/6` — six of those successful calls didn't match any required action's exact spec.

This is the most important piece of grader logic. Read it.

---

## 4. Reward clamp — (0, 1) strictly

**File**: [server/environment.py](server/environment.py#L78-L88)

```python
if step_reward <= 0.0:
    step_reward = 0.01
if step_reward >= 1.0:
    step_reward = 0.99
```

Why: the hackathon organizers required rewards strictly in (0, 1) — never exactly 0 or 1. We clamp both per-step and cumulative. This was a compliance fix flagged during Phase 2 review.

---

## 5. Session persistence — single-worker uvicorn

**File**: [server/app.py](server/app.py#L21)

```python
sessions: Dict[str, WorkFlowEnvironment] = {}
```

Sessions live in an in-process dict. This means uvicorn MUST run with `--workers 1` — multiple workers would each have separate session dicts and lose the session on any cross-worker request.

The `/reset` endpoint creates a new `WorkFlowEnvironment`, assigns a UUID session_id, and stores it. `/step` looks up the env by session_id. After `done=True`, the session is popped.

This is a deliberate tradeoff: single-worker is fine for a demo env; production would use Redis.

---

## 6. OpenEnv contract alignment

**File**: [server/environment.py](server/environment.py#L28-L35)

```python
try:
    from openenv.core.environment import Environment as _OpenEnvBase
except Exception:
    class _OpenEnvBase:
        pass

class WorkFlowEnvironment(_OpenEnvBase):
```

Graceful fallback when `openenv-core` isn't installed. The class inherits from OpenEnv's base when available, falls back to a shim otherwise. Either way, the HTTP contract (`/reset`, `/step`, `/state`) is the authority, per the OpenEnv spec.

The HTTP endpoints are wired in [server/app.py](server/app.py):
- `POST /reset` — line 29
- `POST /step` — line 44
- `GET /state` — line 58
- `GET /health` — line 24

Full openenv.yaml manifest at [openenv.yaml](openenv.yaml) — declares action/observation/state models, all 5 tasks, and endpoint paths.

---

## 7. Client/server separation

**File**: [client.py](client.py)

The client is pure `httpx` — imports only `WorkFlowAction`, `WorkFlowObservation`, `WorkFlowState`, `StepResult` from `models.py`. It never imports anything from `server/`. Clean separation, as required by the hackathon's engineering criteria.

---

## 8. Training evidence — real runs, not fabrication

**File**: [train_simple_agent.py](train_simple_agent.py)

80-episode epsilon-greedy bandit over action templates. Produces 3 committed PNGs and a JSON with raw numbers.

Key details:
- **Per-workflow seeds** (line 158): different seeds per workflow so curves don't overlap trivially
- **Epsilon decay** (line 109): `1.0 → 0.05` over 80% of training
- **TD loss** (line 135): `(q_before - reward)^2` — Bellman residual, legit RL loss
- **Deterministic** (line 80): seeded numpy + random for reproducibility

You can run this yourself in ~2 minutes on CPU. `python3 train_simple_agent.py` → plots regenerate from scratch.

---

## 9. 5 workflows with progressive difficulty

**File**: [workflows.py](workflows.py)

Each workflow defines:
- `name`, `description`, `difficulty`, `max_steps`
- `scenario` — the initial state agent sees
- `required_actions` — list of actions the agent must complete, each with:
  - `id` — unique identifier
  - `app`, `method` — what API call is expected
  - `priority` — correct sequence position (1-indexed)
  - `params` — expected parameters (supports `_contains` suffix for substring match)

Grep for `required_actions` to see exact specs. 30 total required actions across the 5 workflows.

---

## 10. Baseline — proves the env is gradable

**File**: [baseline_test.py](baseline_test.py)

A scripted "perfect agent" that submits the correct API calls for each workflow. Hits the live HF Space and prints per-step rewards.

Result: **~0.95 average** across 5 workflows. This proves two things:
1. The grader works end-to-end (a correct agent gets ~0.95, never lower, never perfect)
2. The env is tractable (not so hard that even scripted correct answers fail)

`incident_response` scores 0.793 — deliberately sub-1.0 for the hardest workflow. Shows the grader is strict.

---

## If you only have 60 seconds

1. Open [server/environment.py](server/environment.py) and read lines 294-307 (reward computation)
2. Open [mock_apps.py](mock_apps.py) and search for `enum` or `limit` (business rules)
3. Look at [reward_curve.png](reward_curve.png) + [comparison_chart.png](comparison_chart.png)

Those three things answer: "is the reward verifiable, are business rules enforced, did it actually learn?"
