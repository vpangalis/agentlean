# ImproveGraphState — ONE TypedDict for Agent Improve
# Implementation pending — see ARCHITECTURE.md section 4
from typing import TypedDict, Optional, Any

class ImproveGraphState(TypedDict):
    case_id: str
    current_phase: str
    current_user: str
    phase_inputs: dict
    chat_history: list
    gate_attempts: int
    escalated: bool
    citations: list
    analyst_output: Optional[dict]
    uploaded_files: list
    case_metadata: dict
