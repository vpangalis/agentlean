# Waiting on you

The control board's "Waiting on you" box lists every line below that starts with `- `: the
decisions only the founder can make. Remove a line once it is ruled; with no line left the box is
hidden. Read by `tools/control_board/build_control_board.py` (`waiting_on_you`).

- An ADR for sign-in and the team roster (DEF-103, DEF-104, DEF-116, DEF-114): where the lead's roster changes are written after creation (ADR-0066 allows case-blob writes only at creation, upload and approval); where invite codes (single-use, 72 h, hashed) and sign-in records live; and the session thread_id comes from (signed cookie or token, lifetime). Stop condition 2 — Desktop drafts, the founder rules
- Save FUTURE_security_requirements.md into docs/founder-inputs/: the queued step that records R21 (coach charter), the R19 and W8 amendments and T95-T97 as DRAFT / Won't-now reads it, and it is not on this machine
