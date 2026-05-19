from __future__ import annotations

from typing import TypedDict, Optional


class ImproveGraphState(TypedDict, total=False):
    """Single source of truth for Agent Improve.
    All fields optional (total=False).
    Nodes return dict slices only — never the full state."""

    # Case identity — set at session start from blob
    case_id: str | None
    current_phase: str | None          # define|measure|analyse_phase|improve|control
    current_user: str | None           # name of team member active this turn

    # Phase inputs — partial dict built turn by turn from extraction
    # Written by orchestrate nodes, read by validate nodes and UI
    phase_inputs: dict | None

    # Conversation history — append-only, never modified
    # [{turn, role, user, text, timestamp, citations}]
    chat_history: list | None

    # Gate state — reset to 0 on phase advance
    gate_attempts: int
    escalated: bool

    # Citations accumulated this session
    # [CitationRecord dicts] — see core/citations.py
    citations: list | None

    # Analyst output — written after gate pass
    analyst_output: dict | None

    # Uploaded files this session
    # [{filename, blob_path, classification, phase, uploaded_by, uploaded_at}]
    uploaded_files: list | None

    # Case metadata — loaded from blob at session start
    # {title, belt_level, leader, team, created_at, target_date, department}
    case_metadata: dict | None
