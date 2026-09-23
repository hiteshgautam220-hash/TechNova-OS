"""Base Agent definitions and execution trace abstractions."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class AgentTraceStep(BaseModel):
    step_id: int
    agent_name: str
    step_type: str = Field(description="delegation, tool_call, tool_result, reasoning, recommendation")
    title: str
    details: Any = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3])

class AgentResponse(BaseModel):
    agent_name: str
    status: str = "success"
    summary: str
    findings: Dict[str, Any] = Field(default_factory=dict)
    tools_used: List[str] = Field(default_factory=list)
    trace_steps: List[AgentTraceStep] = Field(default_factory=list)

class BaseAgent:
    def __init__(self, name: str, role: str, system_prompt: str, approved_tools: List[str]):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.approved_tools = approved_tools

    def create_trace(self, step_id: int, step_type: str, title: str, details: Any = None) -> AgentTraceStep:
        return AgentTraceStep(
            step_id=step_id,
            agent_name=self.name,
            step_type=step_type,
            title=title,
            details=details
        )
