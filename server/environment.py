"""Core environment logic for WorkFlow Arena.

The agent orchestrates multi-app enterprise workflows. Every API call
is executed against mock apps and REWARDS ARE VERIFIABLE through
actual API response success.

OpenEnv contract: implements reset() -> observation, step(action) -> (obs, reward, done, info),
state() -> current state. Server (FastAPI) exposes these as /reset, /step, /state per the
OpenEnv HTTP spec. The client (client.py) is a thin wrapper; no server logic leaks into it.

Reward structure uses a composable-rubric pattern (REWARD_RUBRIC below): each step reward
is the sum of independent scoring components, every one traceable to a mock-app state
change, a reasoning-field check, or an integer priority comparison. No LLM judges.
"""

import json
import uuid
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Set, Tuple

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models import APICall
from workflows import WORKFLOWS
from mock_apps import EnterpriseApps

# Try to extend OpenEnv's Environment base. The real class lives at
# openenv_core.env_server.interfaces.Environment (ABC with typed Observation /
# @property state) — our HTTP layer adapts dict-based IO, so we don't inherit
# directly; instead we verify openenv-core is importable and fall back otherwise.
try:
    from openenv.core.environment import Environment as _OpenEnvBase  # type: ignore
except Exception:
    try:
        import openenv_core  # noqa: F401  — presence check only
        class _OpenEnvBase:
            """Shim base — openenv-core is installed; dict-based IO adapted by server/app.py."""
            pass
    except Exception:
        class _OpenEnvBase:
            """Fallback — openenv-core not importable (e.g., Python <3.10)."""
            pass


@dataclass
class RubricContext:
    """Inputs every rubric component sees when scoring a single API call.

    post_add_completed_count is len(completed_actions) AFTER the matched_id (if any)
    has been recorded — needed so priority checks compare against the 1-indexed
    position the agent has just achieved.
    """
    call: APICall
    result: Dict
    matched_id: Optional[str]
    post_add_completed_count: int
    workflow: Dict
    points_per_action: float


def _rubric_action_match(ctx: RubricContext) -> float:
    """70% of per-action budget for executing a correct required action."""
    return ctx.points_per_action * 0.70 if ctx.matched_id else 0.0


def _rubric_reasoning(ctx: RubricContext) -> float:
    """15% bonus for providing a non-empty reasoning string on a matched action."""
    if ctx.matched_id and ctx.call.reasoning.strip():
        return ctx.points_per_action * 0.15
    return 0.0


def _rubric_priority_order(ctx: RubricContext) -> float:
    """15% bonus for completing the action in the workflow's specified priority order."""
    if not ctx.matched_id:
        return 0.0
    action_idx = next(
        (i for i, a in enumerate(ctx.workflow["required_actions"]) if a["id"] == ctx.matched_id),
        -1,
    )
    if action_idx < 0:
        return 0.0
    expected_priority = ctx.workflow["required_actions"][action_idx]["priority"]
    if ctx.post_add_completed_count == expected_priority:
        return ctx.points_per_action * 0.15
    return 0.0


def _rubric_exploration(ctx: RubricContext) -> float:
    """Small credit for a valid API call that didn't satisfy any required action.

    Rewards exploration without leaking signal that would let the agent game
    the rubric — 5% of per-action budget is too small to dominate the match bonus.
    """
    if ctx.result.get("success") and not ctx.matched_id:
        return ctx.points_per_action * 0.05
    return 0.0


# Composable rubric — each component scores one axis of behavior.
# Sum of components per call = per-call reward. Ordering is display-only.
REWARD_RUBRIC: List[Tuple[Callable[[RubricContext], float], str]] = [
    (_rubric_action_match, "action_match"),
    (_rubric_reasoning, "reasoning"),
    (_rubric_priority_order, "priority_order"),
    (_rubric_exploration, "exploration"),
]


class WorkFlowEnvironment(_OpenEnvBase):
    """WorkFlow Arena — Multi-app enterprise workflow environment.

    Inherits from openenv.core.environment.Environment when available.
    Contract: reset() / step(action) / state() — the three primitives the
    OpenEnv spec defines. Exposed over HTTP via server/app.py.
    """

    def __init__(self):
        self.task_name: str = ""
        self.workflow: Optional[Dict] = None
        self.episode_id: str = ""
        self.step_count: int = 0
        self.max_steps: int = 10
        self.apps: Optional[EnterpriseApps] = None
        self.completed_actions: Set[str] = set()
        self.total_reward: float = 0.0
        self.api_calls_made: int = 0
        self.api_calls_successful: int = 0

    def reset(self, task_name: str = "employee_onboarding") -> dict:
        if task_name not in WORKFLOWS:
            task_name = "employee_onboarding"

        self.task_name = task_name
        self.workflow = WORKFLOWS[task_name]
        self.episode_id = str(uuid.uuid4())
        self.step_count = 0
        self.max_steps = self.workflow["max_steps"]
        self.apps = EnterpriseApps()
        self.completed_actions = set()
        self.total_reward = 0.0
        self.api_calls_made = 0
        self.api_calls_successful = 0

        content = self._format_initial_observation()
        total_actions = len(self.workflow["required_actions"])

        return {
            "observation": {
                "content": content,
                "done": False,
                "metadata": {
                    "task_name": task_name,
                    "total_required_actions": total_actions,
                    "difficulty": self.workflow["difficulty"],
                },
            },
            "reward": None,
            "done": False,
            "info": {
                "task_name": task_name,
                "total_required_actions": total_actions,
            },
        }

    def step(self, message: str) -> dict:
        """Execute one agent step: parse API calls, run against mock apps, grade.

        The reward is fully deterministic — no LLM judge, no subjective scoring.
        Every reward component traces to either:
          - a boolean result["success"] from a mock app
          - a non-empty string check on reasoning
          - an integer comparison on action sequence position

        Boundaries clamped: exactly 0.0 -> 0.01, exactly 1.0 -> 0.99, so the reward
        range stays in the open interval (0, 1) per the OpenEnv hackathon contract.
        Intermediate values pass through unchanged.
        """
        self.step_count += 1

        api_calls = self._parse_calls(message)
        step_reward, feedback, execution_results, component_totals = self._execute_and_grade(api_calls)

        # Boundary clamp — keep the reward strictly in the open interval (0, 1),
        # per hackathon organizer requirement. Intermediate values unchanged.
        if step_reward <= 0.0:
            step_reward = 0.01
        if step_reward >= 1.0:
            step_reward = 0.99

        self.total_reward += step_reward
        if self.total_reward <= 0.0:
            self.total_reward = 0.01
        if self.total_reward >= 1.0:
            self.total_reward = 0.99

        total_required = len(self.workflow["required_actions"])
        done = self.step_count >= self.max_steps
        if len(self.completed_actions) >= total_required:
            done = True

        content = self._format_step_observation(feedback, execution_results, done)

        return {
            "observation": {
                "content": content,
                "done": done,
                "metadata": {
                    "step": self.step_count,
                    "completed_actions": len(self.completed_actions),
                    "total_required": total_required,
                    "cumulative_score": round(self.total_reward, 4),
                    "api_calls_made": self.api_calls_made,
                    "api_calls_successful": self.api_calls_successful,
                },
            },
            "reward": round(step_reward, 4),
            "done": done,
            "info": {
                "completed_actions": len(self.completed_actions),
                "total_required_actions": total_required,
                "cumulative_score": round(self.total_reward, 4),
                "api_calls_made": self.api_calls_made,
                "api_calls_successful": self.api_calls_successful,
                "reward_components": {k: round(v, 4) for k, v in component_totals.items()},
                "app_state": self.apps.get_state_snapshot() if self.apps else {},
            },
        }

    def state(self) -> dict:
        return {
            "episode_id": self.episode_id,
            "step_count": self.step_count,
            "task_name": self.task_name,
            "total_actions": len(self.workflow["required_actions"]) if self.workflow else 0,
            "completed_actions": len(self.completed_actions),
            "api_calls_made": self.api_calls_made,
            "api_calls_successful": self.api_calls_successful,
            "current_score": round(self.total_reward, 4),
        }

    # ── Helpers ──────────────────────────────────────────────────────────

    def _parse_calls(self, message: str) -> List[APICall]:
        try:
            msg = message.strip()
            data = None
            try:
                data = json.loads(msg)
            except json.JSONDecodeError:
                start = msg.find("{")
                end = msg.rfind("}") + 1
                if start >= 0 and end > start:
                    try:
                        data = json.loads(msg[start:end])
                    except json.JSONDecodeError:
                        pass

            if data is None:
                return []

            if isinstance(data, dict) and "calls" in data:
                calls_data = data["calls"]
            elif isinstance(data, list):
                calls_data = data
            else:
                calls_data = [data]

            calls = []
            for c in calls_data:
                if isinstance(c, dict) and "app" in c and "method" in c:
                    calls.append(APICall(
                        app=str(c["app"]),
                        method=str(c["method"]),
                        params=c.get("params", {}),
                        reasoning=str(c.get("reasoning", "")),
                    ))
            return calls
        except Exception:
            return []

    def _execute_api_call(self, call: APICall) -> Dict:
        """Execute a single API call and return a result dict.

        Wrapped in try/except so malformed inputs (missing required kwargs, wrong
        types) become a graceful {"success": False, "error": ...} response
        instead of raising — keeps the verifier robust under adversarial input
        and prevents an RL trainer's reward function from blowing up.
        """
        app_name = call.app.lower()
        method = call.method.lower()
        params = call.params if isinstance(call.params, dict) else {}

        try:
            if app_name == "gmail":
                if method == "create_account":
                    return self.apps.gmail_create_account(**params)
                elif method in ("send_email", "send"):
                    return self.apps.gmail_send_email(**params)
            elif app_name == "slack":
                if method == "add_user":
                    return self.apps.slack_add_user(**params)
                elif method in ("send_message", "message", "post"):
                    return self.apps.slack_send_message(**params)
            elif app_name == "jira":
                if method == "create_ticket":
                    return self.apps.jira_create_ticket(**params)
                elif method == "update_ticket":
                    return self.apps.jira_update_ticket(**params)
                elif method == "close_sprint":
                    return self.apps.jira_close_sprint(**params)
            elif app_name == "hris":
                if method == "create_employee":
                    return self.apps.hris_create_employee(**params)
                elif method == "assign_equipment":
                    return self.apps.hris_assign_equipment(**params)
            elif app_name == "crm":
                if method == "update_customer":
                    return self.apps.crm_update_customer(**params)
                elif method == "create_support_ticket":
                    return self.apps.crm_create_support_ticket(**params)
            elif app_name == "deploy":
                if method in ("service", "deploy_service"):
                    return self.apps.deploy_service(**params)
                elif method == "rollback":
                    return self.apps.deploy_rollback(**params)
                elif method == "update_status_page":
                    return self.apps.deploy_update_status_page(**params)
            elif app_name == "finance":
                if method == "submit_expense":
                    return self.apps.finance_submit_expense(**params)
                elif method == "approve_expense":
                    return self.apps.finance_approve_expense(**params)
        except TypeError as e:
            # Missing/extra keyword args — treat as a failed call, not a crash.
            return {"success": False, "error": f"bad_params: {e}"}
        except Exception as e:
            return {"success": False, "error": f"{type(e).__name__}: {e}"}

        return {"success": False, "error": f"Unknown app.method: {app_name}.{method}"}

    def _match_required_action(self, call: APICall, result: Dict) -> Optional[str]:
        """Return the ID of the required action this call satisfies, or None.

        Matching rules — all must pass:
          1. result["success"] is True (mock app accepted it)
          2. action not already in completed_actions (no double-counting)
          3. action["app"] == call.app (exact app match)
          4. action["method"] == call.method OR their _-stripped forms match (method alias)
          5. Every key in action["params"] matches call.params:
              - suffix "_contains" → substring check on the unsuffixed key
              - otherwise → case-insensitive string equality

        Returns the first matching required action's ID. This is how the env
        distinguishes "API call succeeded" (generic) from "completed a required
        workflow action" (specific) — critical for verifiable rewards.
        """
        if not result.get("success"):
            return None

        for action in self.workflow["required_actions"]:
            if action["id"] in self.completed_actions:
                continue
            if action["app"] != call.app.lower():
                continue
            # Match method (allow aliases)
            method_ok = (
                action["method"] == call.method.lower()
                or action["method"].replace("_", "") == call.method.lower().replace("_", "")
            )
            if not method_ok:
                continue
            # Check expected params
            expected = action.get("params", {})
            params_match = True
            for k, v in expected.items():
                # Soft matches: "_contains" suffix means substring check
                if k.endswith("_contains"):
                    actual_key = k.replace("_contains", "")
                    actual_val = str(call.params.get(actual_key, "")).lower()
                    if str(v).lower() not in actual_val:
                        params_match = False
                        break
                else:
                    if k in call.params:
                        if str(call.params[k]).lower() != str(v).lower():
                            params_match = False
                            break
            if params_match:
                return action["id"]
        return None

    def _execute_and_grade(
        self, api_calls: List[APICall]
    ) -> Tuple[float, str, List[Dict], Dict[str, float]]:
        """Score a batch of API calls by running each rubric component per call.

        Reward = sum over calls of (sum over rubric components of contribution).
        Side effects: updates self.completed_actions, self.api_calls_made,
        self.api_calls_successful.

        Returns (step_reward, feedback, execution_results, component_totals) where
        component_totals is a per-rubric-component breakdown for this step — used
        by judges/observers to monitor individual reward signals (the hackathon
        guide explicitly recommends "individual reward function columns").
        """
        required_total = len(self.workflow["required_actions"])
        points_per_action = 1.0 / required_total
        step_reward = 0.0
        feedback_parts = []
        execution_results = []
        component_totals: Dict[str, float] = {tag: 0.0 for _, tag in REWARD_RUBRIC}

        if not api_calls:
            feedback_parts.append("  No API calls submitted.")
            return step_reward, "\n".join(feedback_parts), execution_results, component_totals

        for call in api_calls:
            self.api_calls_made += 1
            result = self._execute_api_call(call)
            execution_results.append({
                "call": f"{call.app}.{call.method}",
                "result": result,
            })

            # Determine whether this call satisfied a required action — before
            # scoring, so the rubric sees the final completion state.
            matched_id: Optional[str] = None
            if result.get("success"):
                self.api_calls_successful += 1
                matched_id = self._match_required_action(call, result)
                if matched_id:
                    self.completed_actions.add(matched_id)

            ctx = RubricContext(
                call=call,
                result=result,
                matched_id=matched_id,
                post_add_completed_count=len(self.completed_actions),
                workflow=self.workflow,
                points_per_action=points_per_action,
            )

            # Apply the composable rubric: each component scores one axis.
            call_reward = 0.0
            for component_fn, tag in REWARD_RUBRIC:
                contrib = component_fn(ctx)
                component_totals[tag] += contrib
                call_reward += contrib
            step_reward += call_reward

            if matched_id:
                feedback_parts.append(
                    f"  ✅ {call.app}.{call.method}: SUCCESS — completed '{matched_id}' (+{call_reward:.3f})"
                )
            elif result.get("success"):
                feedback_parts.append(
                    f"  ⚠️ {call.app}.{call.method}: API success but doesn't match any required action"
                )
            else:
                error = result.get("error", "unknown")
                feedback_parts.append(
                    f"  ❌ {call.app}.{call.method}: FAILED — {error}"
                )

        feedback_parts.append(
            f"\n  Progress: {len(self.completed_actions)}/{required_total} required actions. "
            f"API: {self.api_calls_successful}/{self.api_calls_made} successful."
        )
        return step_reward, "\n".join(feedback_parts), execution_results, component_totals

    def _format_initial_observation(self) -> str:
        wf = self.workflow
        scenario_json = json.dumps(wf.get("scenario", {}), indent=2, default=str)
        actions_list = "\n".join(
            f"  {i+1}. [{a['app']}.{a['method']}] {a['id']} (priority {a['priority']})"
            for i, a in enumerate(wf["required_actions"])
        )

        apps_methods = {
            "gmail": ["create_account(email)", "send_email(to, subject, body)"],
            "slack": ["add_user(user_id, channels)", "send_message(channel, text)"],
            "jira": ["create_ticket(title, ticket_type, priority, assignee)",
                     "update_ticket(ticket_id, status)", "close_sprint(sprint_id)"],
            "hris": ["create_employee(emp_id, name, email, dept, start_date)",
                     "assign_equipment(emp_id, equipment)"],
            "crm": ["update_customer(customer_id, status, tier)",
                    "create_support_ticket(customer_id, issue, assignee)"],
            "deploy": ["service(service, version)", "rollback(service)",
                       "update_status_page(status)"],
            "finance": ["submit_expense(emp_id, amount, category, description)",
                        "approve_expense(expense_id, approver)"],
        }
        apps_text = "\n".join(
            f"  {app}: {', '.join(methods)}"
            for app, methods in apps_methods.items()
        )

        return (
            f"WORKFLOW: {wf['name']} ({wf['difficulty'].upper()})\n\n"
            f"DESCRIPTION:\n{wf['description']}\n\n"
            f"SCENARIO:\n{scenario_json}\n\n"
            f"REQUIRED ACTIONS ({len(wf['required_actions'])} total, complete in priority order):\n"
            f"{actions_list}\n\n"
            f"AVAILABLE APIs:\n{apps_text}\n\n"
            "INSTRUCTIONS:\n"
            "Submit API calls as JSON:\n"
            '{\n  "calls": [\n    {\n'
            '      "app": "gmail|slack|jira|hris|crm|deploy|finance",\n'
            '      "method": "<method_name>",\n'
            '      "params": {"key": "value"},\n'
            '      "reasoning": "<WHY this action is needed>"\n'
            '    }\n  ]\n}\n\n'
            "Every action has VERIFIABLE success via API response.\n"
            f"You have {self.max_steps} steps to complete all required actions."
        )

    def _format_step_observation(self, feedback: str, execution_results: List[Dict], done: bool) -> str:
        if done:
            total_required = len(self.workflow["required_actions"])
            score = min(max(self.total_reward, 0.01), 0.99)
            return (
                "WORKFLOW COMPLETE\n\n"
                f"FEEDBACK:\n{feedback}\n\n"
                f"FINAL STATS:\n"
                f"  Required actions completed: {len(self.completed_actions)}/{total_required}\n"
                f"  API calls made: {self.api_calls_made}\n"
                f"  API success rate: {self.api_calls_successful}/{self.api_calls_made}\n"
                f"  Final score: {score:.3f}\n"
            )

        app_state = json.dumps(self.apps.get_state_snapshot(), indent=2, default=str)
        return (
            f"FEEDBACK:\n{feedback}\n\n"
            f"CURRENT APP STATE:\n{app_state}\n\n"
            f"Steps remaining: {self.max_steps - self.step_count}\n"
            "Continue the workflow."
        )
