"""HTTP client for WorkFlow Arena."""

from typing import Optional
import httpx
from models import WorkFlowAction, WorkFlowObservation, WorkFlowState, StepResult


class WorkFlowEnv:
    def __init__(self, base_url: str = "http://localhost:7860"):
        self.base_url = base_url.rstrip("/")
        self._http = None
        self._session_id = None

    def sync(self):
        return self

    def __enter__(self):
        self._http = httpx.Client(base_url=self.base_url, timeout=120.0)
        return self

    def __exit__(self, *args):
        if self._http:
            self._http.close()

    def reset(self, task_name="employee_onboarding"):
        d = self._http.post("/reset", json={"task_name": task_name}).json()
        self._session_id = d.get("session_id")
        return StepResult(
            observation=WorkFlowObservation(**d["observation"]),
            reward=d.get("reward"),
            done=d.get("done", False),
            info=d.get("info", {}),
        )

    def step(self, action: WorkFlowAction):
        d = self._http.post("/step", json={"session_id": self._session_id, "message": action.message}).json()
        return StepResult(
            observation=WorkFlowObservation(**d["observation"]),
            reward=d.get("reward", 0.0),
            done=d.get("done", False),
            info=d.get("info", {}),
        )

    def state(self):
        d = self._http.get("/state", params={"session_id": self._session_id}).json()
        return WorkFlowState(**d)

    def health(self):
        return self._http.get("/health").json()
