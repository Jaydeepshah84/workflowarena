"""Core environment logic for WorkFlow Arena.

The agent orchestrates multi-app enterprise workflows. Every API call
is executed against mock apps and REWARDS ARE VERIFIABLE through
actual API response success.

OpenEnv contract: implements reset() -> observation, step(action) -> (obs, reward, done, info),
state() -> current state. Server (FastAPI) exposes these as /reset, /step, /state per the
OpenEnv HTTP spec. The client (client.py) is a thin wrapper; no server logic leaks into it.
"""

import json
import uuid
from typing import Dict, List, Optional, Set, Tuple

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models import APICall
from workflows import WORKFLOWS
from mock_apps import EnterpriseApps

try:
    from openenv.core.environment import Environment as _OpenEnvBase
except Exception:
    class _OpenEnvBase:
        """Fallback base class when openenv-core is not on the current path."""
        pass


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
        self.step_count += 1

        api_calls = self._parse_calls(message)
        step_reward, feedback, execution_results = self._execute_and_grade(api_calls)

        # Ensure reward in (0, 1)
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
        """Execute a single API call and return the result."""
        app_name = call.app.lower()
        method = call.method.lower()

        # Route to the right app
        if app_name == "gmail":
            if method == "create_account":
                return self.apps.gmail_create_account(**call.params)
            elif method in ("send_email", "send"):
                return self.apps.gmail_send_email(**call.params)
        elif app_name == "slack":
            if method == "add_user":
                return self.apps.slack_add_user(**call.params)
            elif method in ("send_message", "message", "post"):
                return self.apps.slack_send_message(**call.params)
        elif app_name == "jira":
            if method == "create_ticket":
                return self.apps.jira_create_ticket(**call.params)
            elif method == "update_ticket":
                return self.apps.jira_update_ticket(**call.params)
            elif method == "close_sprint":
                return self.apps.jira_close_sprint(**call.params)
        elif app_name == "hris":
            if method == "create_employee":
                return self.apps.hris_create_employee(**call.params)
            elif method == "assign_equipment":
                return self.apps.hris_assign_equipment(**call.params)
        elif app_name == "crm":
            if method == "update_customer":
                return self.apps.crm_update_customer(**call.params)
            elif method == "create_support_ticket":
                return self.apps.crm_create_support_ticket(**call.params)
        elif app_name == "deploy":
            if method in ("service", "deploy_service"):
                return self.apps.deploy_service(**call.params)
            elif method == "rollback":
                return self.apps.deploy_rollback(**call.params)
            elif method == "update_status_page":
                return self.apps.deploy_update_status_page(**call.params)
        elif app_name == "finance":
            if method == "submit_expense":
                return self.apps.finance_submit_expense(**call.params)
            elif method == "approve_expense":
                return self.apps.finance_approve_expense(**call.params)

        return {"success": False, "error": f"Unknown app.method: {app_name}.{method}"}

    def _match_required_action(self, call: APICall, result: Dict) -> Optional[str]:
        """Check if this API call matches any pending required action."""
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

    def _execute_and_grade(self, api_calls: List[APICall]) -> Tuple[float, str, List[Dict]]:
        required_total = len(self.workflow["required_actions"])
        points_per_action = 1.0 / required_total
        step_reward = 0.0
        feedback_parts = []
        execution_results = []

        if not api_calls:
            feedback_parts.append("  No API calls submitted.")
            return step_reward, "\n".join(feedback_parts), execution_results

        for call in api_calls:
            self.api_calls_made += 1
            result = self._execute_api_call(call)
            execution_results.append({
                "call": f"{call.app}.{call.method}",
                "result": result,
            })

            if result.get("success"):
                self.api_calls_successful += 1
                matched_id = self._match_required_action(call, result)
                if matched_id:
                    self.completed_actions.add(matched_id)
                    action_reward = points_per_action * 0.7  # 70% for correct API call
                    # Bonus for reasoning
                    if call.reasoning.strip():
                        action_reward += points_per_action * 0.15
                    # Bonus for correct priority (doing things in the right order)
                    action_idx = next(i for i, a in enumerate(self.workflow["required_actions"]) if a["id"] == matched_id)
                    expected_priority = self.workflow["required_actions"][action_idx]["priority"]
                    if len(self.completed_actions) == expected_priority:  # In order!
                        action_reward += points_per_action * 0.15
                    step_reward += action_reward
                    feedback_parts.append(
                        f"  ✅ {call.app}.{call.method}: SUCCESS — completed '{matched_id}' (+{action_reward:.3f})"
                    )
                else:
                    step_reward += points_per_action * 0.05  # small credit for valid call
                    feedback_parts.append(
                        f"  ⚠️ {call.app}.{call.method}: API success but doesn't match any required action"
                    )
            else:
                # API call failed
                error = result.get("error", "unknown")
                feedback_parts.append(
                    f"  ❌ {call.app}.{call.method}: FAILED — {error}"
                )

        remaining = required_total - len(self.completed_actions)
        feedback_parts.append(
            f"\n  Progress: {len(self.completed_actions)}/{required_total} required actions. "
            f"API: {self.api_calls_successful}/{self.api_calls_made} successful."
        )
        return step_reward, "\n".join(feedback_parts), execution_results

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
