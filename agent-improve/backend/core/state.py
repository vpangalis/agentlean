from typing import TypedDict, Optional

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
