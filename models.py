"""Pydantic models for WorkFlow Arena."""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List


class APICall(BaseModel):
    """A single API call the agent makes."""
    app: str  # gmail, slack, jira, hris, crm, deploy, finance
    method: str
    params: Dict[str, Any] = Field(default_factory=dict)
    reasoning: str = ""


class WorkFlowAction(BaseModel):
    """Action: agent submits API calls as JSON."""
    message: str = Field(..., description="JSON with 'calls' list of API calls")


class WorkFlowObservation(BaseModel):
    content: str
    done: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkFlowState(BaseModel):
    episode_id: Optional[str] = None
    step_count: int = 0
    task_name: str = ""
    total_actions: int = 0
    completed_actions: int = 0
    api_calls_made: int = 0
    api_calls_successful: int = 0
    current_score: float = 0.0


class StepResult(BaseModel):
    observation: WorkFlowObservation
    reward: Optional[float] = None
    done: bool = False
    info: Dict[str, Any] = Field(default_factory=dict)
